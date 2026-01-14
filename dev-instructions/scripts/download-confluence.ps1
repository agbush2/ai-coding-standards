[CmdletBinding()]
param(
    [string]$BaseUrl,
    [string]$Email,
    [string]$ApiToken,
    [string]$PageId,
    [string]$RootPageUrl,
    [string]$OutDir = "agile-ai/source-material/confluence",
    [ValidateSet('html', 'xhtml')] [string]$Format = 'xhtml',
    [int]$MaxDepth = 5,
    [switch]$SinglePageOnly
)

# Reference Implementation:
# Simple downloader for a Confluence page (by ID or URL) and optionally its descendants
# Saves each page as XHTML (Confluence storage) or HTML (export_view) with front-matter metadata.
# NO PRETTY PRINTING. PRESERVES RAW STORAGE FORMAT.

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

# Try to load config from OutDir/confluence.config (Simple Key=Value format)
$configPath = Join-Path -Path $OutDir -ChildPath 'confluence.config'
if (Test-Path $configPath) {
    try {
        # ConvertFrom-StringData parses "Key=Value" lines into a hashtable
        $config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-StringData
        if ($config.ContainsKey('BaseUrl') -and -not $BaseUrl) { $BaseUrl = $config['BaseUrl'] }
        if ($config.ContainsKey('PageId') -and -not $PageId) { $PageId = $config['PageId'] }
    }
    catch {
        Write-Warning "Failed to load config from $configPath : $_"
    }
}

# Fallback to env vars if parameters not supplied
if (-not $BaseUrl) { $BaseUrl = $env:BASE_URL }
if (-not $Email) { $Email = $env:CONF_EMAIL }
if (-not $ApiToken) { $ApiToken = $env:CONF_TOKEN }

# Validate credentials strictly (no hard-coded defaults)
if (-not $BaseUrl -or -not $Email -or -not $ApiToken) {
    throw "Missing credentials: set BASE_URL, CONF_EMAIL, and CONF_TOKEN via parameters or .env/ENV."
}

function New-AuthHeader {
    <#
    .SYNOPSIS
        Creates a Basic Auth header for Confluence API.
    .PARAMETER Email
        The user email address.
    .PARAMETER ApiToken
        The Atlassian API token.
    #>
    param(
        [string]$Email,
        [string]$ApiToken
    )
    $pair = "${Email}:${ApiToken}"
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($pair)
    $base64 = [Convert]::ToBase64String($bytes)
    return @{ Authorization = "Basic $base64"; 'Accept' = 'application/json' }
}

function Get-PageIdFromUrl {
    <#
    .SYNOPSIS
        Extracts the page ID from a Confluence web link.
    #>
    param([string]$Url)
    # Expecting .../pages/<id>/...
    if ($Url -match "/pages/([0-9]+)/") { return $Matches[1] }
    throw "Unable to parse page id from URL: $Url"
}

function Invoke-ConfluenceGet {
    <#
    .SYNOPSIS
        Wraps Invoke-RestMethod for Confluence calls with error handling.
    #>
    param(
        [string]$Path,
        [hashtable]$Headers
    )
    $uri = "$BaseUrl$Path"
    try {
        $response = Invoke-RestMethod -Method GET -Uri $uri -Headers $Headers -ErrorAction Stop
    }
    catch {
        $message = $_.Exception.Message
        if ($message -match '\(401\)') { throw "Unauthorized (401) calling $uri. Check CONF_EMAIL/CONF_TOKEN are correct and have Confluence access." }
        if ($message -match '\(403\)') { throw "Forbidden (403) calling $uri. The account lacks permission for this content." }
        if ($message -match '\(404\)') { throw "Not Found (404) calling $uri. Verify the BaseUrl ($BaseUrl) and path are correct, and the page exists." }
        throw
    }
    return $response
}

function Get-Page {
    <#
    .SYNOPSIS
        Retrieves a single page content (storage and export_view) from Confluence API.
    #>
    param(
        [string]$Id,
        [hashtable]$Headers
    )
    if (-not $Id -or -not ($Id -match '^[0-9]+$')) { throw "Invalid page id: '$Id'" }
    $path = ("/wiki/rest/api/content/{0}?expand=body.export_view,body.storage,version,ancestors,space" -f $Id)
    return Invoke-ConfluenceGet -Path $path -Headers $Headers
}

function Get-Children {
    <#
    .SYNOPSIS
        Retrieves direct child pages of a given page.
    #>
    param(
        [string]$Id,
        [hashtable]$Headers
    )
    if (-not $Id -or -not ($Id -match '^[0-9]+$')) { throw "Invalid page id: '$Id'" }
    $start = 0
    $limit = 100
    $results = @()
    while ($true) {
        $path = ("/wiki/rest/api/content/{0}/child/page?limit={1}&start={2}" -f $Id, $limit, $start)
        $response = Invoke-ConfluenceGet -Path $path -Headers $Headers
        if ($response.results) { $results += $response.results }
        
        # Check for pagination using psbase property check or try/catch to avoid strict mode error
        $hasNext = $false
        if ($response.psobject.Properties[' _links'] -or $response.psobject.Properties['_links']) {
             if ($response._links.psobject.Properties['next']) {
                 $hasNext = $true
             }
        }
        
        if (-not $hasNext) { break }
        $start += $limit
    }
    return $results
}

function Test-ConfluenceAuth {
    <#
    .SYNOPSIS
        Verifies authentication by requesting a lightweight resource.
    #>
    param([hashtable]$Headers)
    $probe = "/wiki/rest/api/space?limit=1"
    try {
        $null = Invoke-ConfluenceGet -Path $probe -Headers $Headers
        return $true
    }
    catch {
        Write-Warning $_
        return $false
    }
}

function ConvertTo-SafeFileName {
    <#
    .SYNOPSIS
        Sanitizes a string for use as a filename.
    #>
    param([string]$Name)
    $name = $Name -replace '[\\/:*?"<>|]', '-'
    $name = $name.Trim()
    if ($name.Length -gt 120) { $name = $name.Substring(0, 120) }
    return $name
}

function Get-StringHash {
    <#
    .SYNOPSIS
        Computes MD5 hash of string content for change detection.
    #>
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
    <#
    .SYNOPSIS
        Counts occurrences of specific Confluence macros in content.
    #>
    param([string]$Content)
    $counts = @{}
    $counts.structured_macro = ([regex]::Matches($Content, '<ac:structured-macro\b')).Count
    $counts.image = ([regex]::Matches($Content, '<ac:image\b')).Count
    $counts.link = ([regex]::Matches($Content, '<ac:link\b')).Count
    return $counts
}

function Save-Page {
    <#
    .SYNOPSIS
        Saves the page content to disk with front matter metadata.
    #>
    param(
        $Page,
        [string]$Dir,
        [string]$Format
    )
    $title = $Page.title
    $fileBase = ConvertTo-SafeFileName $title
    $id = $Page.id
    $version = $null
    if ($Page.psobject.Properties.Name -contains 'version') { $version = $Page.version.number }
    $space = $null
    if ($Page.psobject.Properties.Name -contains 'space' -and $Page.space) { $space = $Page.space.key }
    $url = $null
    if ($Page.psobject.Properties.Name -contains '_links' -and $Page._links -and $Page._links.webui) {
        $url = "$BaseUrl$($Page._links.webui)"
    }
    elseif ($Page.psobject.Properties.Name -contains 'links' -and $Page.links -and $Page.links.self) {
        $url = $Page.links.self
    }
    if (-not (Test-Path $Dir)) { New-Item -ItemType Directory -Force -Path $Dir | Out-Null }
    # Always save flat with ID prefix to avoid long paths
    $nameBase = "$id-$fileBase"

    if ($Format -eq 'xhtml') {
        # Save raw Confluence storage format (XHTML)
        $xhtml = $null
        if ($Page.body -and $Page.body.storage -and $Page.body.storage.value) { $xhtml = $Page.body.storage.value }
        elseif ($Page.body -and $Page.body.value) { $xhtml = $Page.body.value }

        # NO PRETTY PRINTING. PRESERVE RAW CONTENT.
        $rawContent = $xhtml

        $contentHash = Get-StringHash -Content $rawContent

        $macroCounts = Get-MacroCounts -Content $rawContent
        $front = "---$([System.Environment]::NewLine)source: $url$([System.Environment]::NewLine)confluence_id: $id$([System.Environment]::NewLine)space: $space$([System.Environment]::NewLine)version: $version$([System.Environment]::NewLine)retrieved: $(Get-Date -Format o)$([System.Environment]::NewLine)format: xhtml$([System.Environment]::NewLine)content_hash: $contentHash$([System.Environment]::NewLine)macro_structured_macro: $($macroCounts.structured_macro)$([System.Environment]::NewLine)macro_image: $($macroCounts.image)$([System.Environment]::NewLine)macro_link: $($macroCounts.link)$([System.Environment]::NewLine)---$([System.Environment]::NewLine)"
        $outPath = Join-Path $Dir "$nameBase.xhtml"

        # Concatenate front matter and raw content. 
        $fileContent = "$front$rawContent"

        # Save with UTF8 no BOM
        $fileContent | Out-File -FilePath $outPath -Encoding UTF8

        return [pscustomobject]@{ Id = $id; Title = $title; Version = $version; Format = 'xhtml'; Path = $outPath; Macros = $macroCounts }
    }
    elseif ($Format -eq 'html') {
        $html = $null
        if ($Page.body -and $Page.body.export_view -and $Page.body.export_view.value) { $html = $Page.body.export_view.value }

        $rawContent = $html

        $contentHash = Get-StringHash -Content $rawContent

        $macroCounts = Get-MacroCounts -Content $rawContent
        $front = "---$([System.Environment]::NewLine)source: $url$([System.Environment]::NewLine)confluence_id: $id$([System.Environment]::NewLine)space: $space$([System.Environment]::NewLine)version: $version$([System.Environment]::NewLine)retrieved: $(Get-Date -Format o)$([System.Environment]::NewLine)format: html$([System.Environment]::NewLine)content_hash: $contentHash$([System.Environment]::NewLine)macro_structured_macro: $($macroCounts.structured_macro)$([System.Environment]::NewLine)macro_image: $($macroCounts.image)$([System.Environment]::NewLine)macro_link: $($macroCounts.link)$([System.Environment]::NewLine)---$([System.Environment]::NewLine)"
        $outPath = Join-Path $Dir "$nameBase.html"
        $fileContent = "$front$rawContent"
        $fileContent | Out-File -FilePath $outPath -Encoding UTF8
        return [pscustomobject]@{ Id = $id; Title = $title; Version = $version; Format = 'html'; Path = $outPath; Macros = $macroCounts }
    }
    else {
        throw "Unsupported format '$Format'. Use 'xhtml' or 'html'."
    }
}

function Invoke-TreeWalk {
    <#
    .SYNOPSIS
        Recursively downloads a page and its descendants.
    #>
    param(
        [string]$RootId,
        [hashtable]$Headers,
        [string]$OutDir,
        [string]$Format,
        [int]$MaxDepth
    )
    $seenPages = New-Object System.Collections.Generic.HashSet[string]

    function Recurse([string]$Id, [string]$Dir, [int]$Depth) {
        if ($seenPages.Contains($Id)) { return }
        $null = $seenPages.Add($Id)
        $page = Get-Page -Id $Id -Headers $Headers
        $saved = Save-Page -Page $page -Dir $Dir -Format $Format
        if ($saved) {
            Write-Verbose "Saved page id=$($saved.Id) v$($saved.Version) format=$($saved.Format) macros=[structured:$($saved.Macros.structured_macro),image:$($saved.Macros.image),link:$($saved.Macros.link)] -> $($saved.Path)"
        }

        # Stop recursion when reaching the maximum depth
        if ($Depth -ge $MaxDepth) { return }

        $children = Get-Children -Id $Id -Headers $Headers
        
        # Safe count check for Strict Mode
        $childCount = 0
        if ($children) {
             if ($children.psobject.Properties['Count']) { $childCount = $children.Count }
             elseif ($children -is [array]) { $childCount = $children.Length }
             else { $childCount = 1 } # Single object
        }

        if ($childCount -gt 0) {
            Write-Verbose "Found $childCount child page(s) under id=$Id"
        }
        foreach ($childPage in $children) {
            # Always write to the same directory (flat)
            $subDir = $Dir
            Recurse -Id $childPage.id -Dir $subDir -Depth ($Depth + 1)
        }
    }

    # Root starts at depth 0
    Recurse -Id $RootId -Dir $OutDir -Depth 0
}

# Entry
$headers = New-AuthHeader -Email $Email -ApiToken $ApiToken

# Preflight auth check
if (-not (Test-ConfluenceAuth -Headers $headers)) {
    throw "Confluence auth or BaseUrl is not valid. Ensure BASE_URL, CONF_EMAIL, and CONF_TOKEN are set (via .env) and correct."
}

if ($PageId) {
    $rootId = $PageId
}
elseif ($RootPageUrl) {
    $rootId = Get-PageIdFromUrl -Url $RootPageUrl
}
else {
    throw "You must provide -PageId or -RootPageUrl."
}

if (-not $SinglePageOnly) {
    Write-Verbose "Starting tree download from page id=$rootId (max depth $MaxDepth)"
    Invoke-TreeWalk -RootId $rootId -Headers $headers -OutDir $OutDir -Format $Format -MaxDepth $MaxDepth
}
else {
    Write-Verbose "Downloading single page id=$rootId"
    $page = Get-Page -Id $rootId -Headers $headers
    $saved = Save-Page -Page $page -Dir $OutDir -Format $Format
    if ($saved) {
        Write-Verbose "Saved page id=$($saved.Id) v$($saved.Version) format=$($saved.Format) macros=[structured:$($saved.Macros.structured_macro),image:$($saved.Macros.image),link:$($saved.Macros.link)] -> $($saved.Path)"
    }
}
