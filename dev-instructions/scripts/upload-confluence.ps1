param(
  [string]$BaseUrl,
  [string]$Email,
  [string]$ApiToken,
  [string]$SourceDir = "agile-ai/source-material/confluence",
  [switch]$DryRun
)

# Uploads local files with front-matter back to Confluence.
# NO FORMATTING OR PRETTY PRINTING. PRESERVES RAW STORAGE FORMAT.
# It reads .xhtml files from a source directory, parses the front-matter for metadata,
# and uses the Confluence API to update the corresponding pages.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Load .env if present to set folder-scoped env vars
$envPath = Join-Path -Path (Get-Location) -ChildPath '.env'
if (Test-Path $envPath) {
  foreach ($line in Get-Content -LiteralPath $envPath) {
    if ($line -match '^\s*#') { continue }
    if ($line -match '^(?<k>[A-Za-z_][A-Za-z0-9_]*)=(?<v>.*)$') {
      $key = $Matches['k']
      $val = $Matches['v']
      [Environment]::SetEnvironmentVariable($key, $val, 'Process')
    }
  }
}

# Try to load config from SourceDir/confluence.config (Simple Key=Value format)
$configPath = Join-Path -Path $SourceDir -ChildPath 'confluence.config'
if (Test-Path $configPath) {
    try {
        # ConvertFrom-StringData parses "Key=Value" lines into a hashtable
        $config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-StringData
        if ($config.ContainsKey('BaseUrl') -and -not $BaseUrl) { $BaseUrl = $config['BaseUrl'] }
        # Validates config loading but upload doesn't need PageId as it reads from file metadata
    }
    catch {
        Write-Warning "Failed to load config from $configPath : $_"
    }
}

# Fallback to env vars if parameters not supplied
if (-not $BaseUrl) { $BaseUrl = $env:BASE_URL }
if (-not $Email)   { $Email   = $env:CONF_EMAIL }
if (-not $ApiToken){ $ApiToken= $env:CONF_TOKEN }

# Validate credentials strictly (no hard-coded defaults)
if (-not $BaseUrl -or -not $Email -or -not $ApiToken) {
    throw "Missing credentials: set BASE_URL, CONF_EMAIL, and CONF_TOKEN via parameters or .env/ENV."
}

# --- Confluence API Functions ---

function New-AuthHeader {
  param([string]$Email,[string]$ApiToken)
  $pair = "${Email}:${ApiToken}"
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($pair)
  $b64 = [Convert]::ToBase64String($bytes)
  @{ Authorization = "Basic $b64"; 'Accept' = 'application/json' }
}

function Invoke-ConfluenceApi {
    param(
        [string]$Method,
        [string]$Path,
        [hashtable]$Headers,
        [string]$Body
    )
    $uri = "$BaseUrl$Path"
    $invokeParams = @{
        Method = $Method
        Uri = $uri
        Headers = $Headers
        ErrorAction = 'Stop'
    }
    if ($Body) {
        $invokeParams.Body = $Body
        $invokeParams.ContentType = 'application/json; charset=utf-8'
    }

    try {
        return Invoke-RestMethod @invokeParams
    } catch {
        $responseStream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($responseStream)
        $errorBody = $reader.ReadToEnd()
        Write-Error "API Error calling $Method $uri. Status: $($_.Exception.Response.StatusCode). Body: $errorBody"
        throw
    }
}

function Get-Page {
  param([string]$Id,[hashtable]$Headers)
  if (-not $Id -or -not ($Id -match '^[0-9]+$')) { throw "Invalid page id: '$Id'" }
  $path = ("/wiki/rest/api/content/{0}?expand=version" -f $Id)
  return Invoke-ConfluenceApi -Method 'GET' -Path $path -Headers $Headers
}

function Test-ConfluenceAuth {
  param([hashtable]$Headers)
  $probe = "/wiki/rest/api/space?limit=1"
  try {
    $null = Invoke-ConfluenceApi -Method 'GET' -Path $probe -Headers $Headers
    return $true
  } catch {
    Write-Warning $_.Exception.Message
    return $false
  }
}

function Get-StringHash {
    param([string]$Content)
    if ([string]::IsNullOrEmpty($Content)) { return "" }
    # Normalize line endings to LF and trim whitespace to ensure consistency
    $normalizedContent = $Content.Replace("`r`n", "`n").Trim()
    $hasher = [System.Security.Cryptography.MD5]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($normalizedContent)
    $hashBytes = $hasher.ComputeHash($bytes)
    return [System.BitConverter]::ToString($hashBytes).Replace('-', '').ToLowerInvariant()
}

function Get-MacroCounts {
    param([string]$Content)
    $counts = @{}
    $counts.structured_macro = ([regex]::Matches($Content, '<ac:structured-macro\b')).Count
    $counts.image = ([regex]::Matches($Content, '<ac:image\b')).Count
    $counts.link = ([regex]::Matches($Content, '<ac:link\b')).Count
    return $counts
}

# --- File Processing Functions ---

function Parse-FrontMatter {
    param([string]$Content)
    $frontMatter = @{}
    # Split strictly on NewLine as saved by update script (LF or CRLF), handle both
    $lines = $Content -split '\r?\n'
    
    # Find the start of the front-matter
    $firstLineIndex = -1
    for ($i = 0; $i -lt $lines.Length; $i++) {
        if ($lines[$i].Trim() -eq '---') {
            $firstLineIndex = $i
            break
        }
    }

    if ($firstLineIndex -eq -1) { return $null }

    $inFrontMatter = $true
    $bodyStartIndex = 0
    for ($i = $firstLineIndex + 1; $i -lt $lines.Length; $i++) {
        $line = $lines[$i]
        if ($line.Trim() -eq '---') {
            $inFrontMatter = $false
            $bodyStartIndex = $i + 1
            break
        }
        if ($inFrontMatter) {
            if ($line -match '^(?<key>[^:]+):\s*(?<value>.+)') {
                $frontMatter[$Matches.key.Trim()] = $Matches.value.Trim()
            }
        }
    }
    
    # Re-assemble body precisely. 
    # Use Join-String or -join "`n" to reconstruct. 
    # Since download script uses [System.Environment]::NewLine for internal standardizing, we should respect that.
    $bodyContent = $lines[$bodyStartIndex..($lines.Length - 1)] -join [System.Environment]::NewLine
    
    return @{ FrontMatter = $frontMatter; Body = $bodyContent }
}


# --- Main Execution ---

$headers = New-AuthHeader -Email $Email -ApiToken $ApiToken

Write-Host "Authenticating with Confluence at $BaseUrl..."
if (-not (Test-ConfluenceAuth -Headers $headers)) {
  throw "Confluence auth or BaseUrl is not valid. Ensure BASE_URL, CONF_EMAIL, and CONF_TOKEN are set and correct."
}
Write-Host "Authentication successful."

$filesToUpload = @(Get-ChildItem -Path $SourceDir -Filter "*.xhtml" -File)
if ($filesToUpload.Count -eq 0) {
    Write-Host "No .xhtml files found in '$SourceDir'. Nothing to upload."
    exit
}

Write-Host "Found $($filesToUpload.Count) file(s) to process."

foreach ($file in $filesToUpload) {
    Write-Host "`nProcessing file: $($file.FullName)"
    $content = Get-Content -Path $file.FullName -Raw
    
    $parsed = Parse-FrontMatter -Content $content
    if (-not $parsed) {
        Write-Warning "Skipping file with no front-matter: $($file.Name)"
        continue
    }

    $meta = $parsed.FrontMatter
    $body = $parsed.Body

    if (-not $meta.confluence_id) {
        Write-Warning "Skipping file with no 'confluence_id' in front-matter: $($file.Name)"
        continue
    }

    # Check for content changes using hash
    if ($meta.content_hash) {
        $currentHash = Get-StringHash -Content $body
        if ($currentHash -eq $meta.content_hash) {
            Write-Host "  - No changes detected (content hash matches). Skipping."
            continue
        }
        Write-Host "  - Content has changed (hash mismatch). Proceeding with update."
    } else {
        Write-Host "  - No content_hash found in front-matter. Proceeding with update."
    }

    # Warn if macro counts appear reduced compared to original snapshot
    $newCounts = Get-MacroCounts -Content $body
    $origStructured = [int]($meta.macro_structured_macro | ForEach-Object { $_ })
    $origImage = [int]($meta.macro_image | ForEach-Object { $_ })
    $origLink = [int]($meta.macro_link | ForEach-Object { $_ })
    if ($origStructured -gt 0 -and $newCounts.structured_macro -lt $origStructured) {
        Write-Warning "  - Structured macro count decreased: $($newCounts.structured_macro) vs original $origStructured. Verify no macros were lost."
    }
    if ($origImage -gt 0 -and $newCounts.image -lt $origImage) {
        Write-Warning "  - Image macro count decreased: $($newCounts.image) vs original $origImage."
    }
    if ($origLink -gt 0 -and $newCounts.link -lt $origLink) {
        Write-Warning "  - Link macro count decreased: $($newCounts.link) vs original $origLink."
    }

    try {
        $pageId = $meta.confluence_id
        Write-Host "  - Found Confluence Page ID: $pageId"

        # Get current page to find the latest version number
        $currentPage = Get-Page -Id $pageId -Headers $headers
        $currentVersion = $currentPage.version.number
        $newVersion = $currentVersion + 1
        
        Write-Host "  - Current version: $currentVersion. Updating to version: $newVersion."

                # Proper JSON construction using object serialization
                $payloadObj = @{
                    id      = $pageId
                    type    = "page"
                    title   = $currentPage.title
                    version = @{ number = $newVersion }
                    body    = @{
                        storage = @{
                            value = $body
                            representation = "storage"
                        }
                    }
                }
                $payload = $payloadObj | ConvertTo-Json -Depth 10 -Compress

        if ($DryRun) {
            Write-Host "  - [DRY RUN] Would update page '$($currentPage.title)' (ID: $pageId) to version $newVersion."
            # Write-Host "Payload: $payload" # Uncomment for debugging
        } else {
            Write-Host "  - Updating page '$($currentPage.title)' (ID: $pageId)..."
            $updatePath = "/wiki/rest/api/content/$pageId"
            $result = Invoke-ConfluenceApi -Method 'PUT' -Path $updatePath -Headers $headers -Body $payload
            Write-Host "  - Successfully updated. New version is $($result.version.number)."
        }

    } catch {
        Write-Error "Failed to process file $($file.Name). Reason: $($_.Exception.Message)"
    }
}

Write-Host "`nUpload process finished."
