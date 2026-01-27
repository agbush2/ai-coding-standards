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

## Module & Manifest Documentation
- **Module-Level Help**: Add comment-based help at the top of `.psm1` files to describe the module's purpose, usage, and exported functions.
- **Manifest (`.psd1`)**: Document all fields, especially `Description`, `Author`, `CompanyName`, `Copyright`, and `FunctionsToExport`.
- **Example**:
    ```powershell
    <#
    .SYNOPSIS
        MyModule provides advanced widget management.
    .DESCRIPTION
        This module exposes functions for creating, updating, and deleting widgets.
    .NOTES
        Author: Jane Doe
        CompanyName: ExampleCorp
    #>
    ```
