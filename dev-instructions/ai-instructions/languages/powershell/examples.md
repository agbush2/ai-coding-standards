# PowerShell Examples & Templates
Implementation of: /master_standards.md

## Relationship to Standards
This file provides PowerShell-specific code templates and usage patterns as referenced in `/master_standards.md` ("What").

---

## Template 1: Module Structure
```text
src/
  MyModule/
    MyModule.psd1        # Manifest
    MyModule.psm1        # Root module
    Public/              # Exported functions
      Get-MyWidget.ps1
    Private/             # Internal helper functions
      Invoke-Helper.ps1
```

---

## Template 2: Function with Comment-Based Help
```powershell
function Get-Widget {
    <#
    .SYNOPSIS
        Gets a widget by name.
    .DESCRIPTION
        Retrieves widget details from the data source.
    .PARAMETER Name
        The name of the widget.
    .EXAMPLE
        Get-Widget -Name 'Foo'
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Name
    )
    # ...function logic...
}
```

---

## Template 3: Error Handling
```powershell
$ErrorActionPreference = 'Stop'
try {
    # Risky operation
    Remove-Item -Path $Path -Force
} catch {
    Write-Error "Failed to remove item: $_"
}
```

---

## Template 4: Pester Test
```powershell
Describe 'Get-Widget' {
    Context 'When widget exists' {
        Mock Get-Widget { return @{ Name = 'TestWidget' } }
        It 'Returns the correct widget name' {
            $result = Get-Widget -Name 'TestWidget'
            $result.Name | Should -Be 'TestWidget'
        }
    }
}
```

---

## Template 5: Secure Credential Handling
```powershell
param(
    [Parameter(Mandatory)]
    [PSCredential]$Credential
)
# Use $Credential to authenticate securely
```

---

## Template 6: Logging
```powershell
Write-Verbose "Processing item $Name"
Write-Warning "Item $Name not found"
Write-Error "Critical failure for $Name"
```
