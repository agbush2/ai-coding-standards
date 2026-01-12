# PowerShell Documentation Standards
Implementation of: /documentation_standards.md

## Comment-Based Help
- **Mandatory**: Every exported function must have `.SYNOPSIS`, `.DESCRIPTION`, `.PARAMETER`, and `.EXAMPLE`.
- **Location**: Inside the function body, at the top.

## Structure
```powershell
function Get-Widget {
    <#
    .SYNOPSIS
        Short summary.

    .DESCRIPTION
        Detailed explanation.

    .PARAMETER Name
        Description of the parameter.

    .EXAMPLE
        Get-Widget -Name 'Foo'
        Explanation of what this does.
    #>
    param()
}
```

## README
- **Root**: `README.md` must exist in the root of the project.
- **Sections**:
    - Project Title
    - Description
    - Installation (`Install-Module...`)
    - Usage Examples
    - Development Setup

## Changelog
- Maintain `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
