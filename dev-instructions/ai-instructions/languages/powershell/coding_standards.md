# PowerShell Coding Standards
Implementation of: /master_standards.md

## Relationship to Standards
This file provides the PowerShell-specific implementation ("How") for the general coding and style guidelines defined in `/master_standards.md` ("What").

## Interpreter
- **Version**: Target PowerShell 7.4+ (Core). Maintain 5.1 compatibility only if explicitly requested.
- **Strict Mode**: Use `Set-StrictMode -Version Latest` in all scripts/modules.

## Style & Formatting
- **Linter**: `PSScriptAnalyzer`. All code must pass default rules.
- **Indentation**: 4 spaces.
- **Braces**: OTBS (One True Brace Style) - Open brace on the same line.
- **Casing**:
    - **Variables**: `camelCase` (e.g., `$myVariable`).
    - **Parameters**: `PascalCase` (e.g., `-ComputerName`).
    - **Functions**: `PascalCase` with Verb-Noun (e.g., `Get-MyWidget`).
- **Verbs**: STRICTLY adhere to `Get-Verb`. Do not invent verbs.

## Naming & Structure
- **Functions**: Use `Verb-Noun` syntax. Noun must be singular (e.g., `Get-User` not `Get-Users`).
- **Parameters**: Use standard names (`-Name`, `-Path`, `-Force`, `-Credential`) where applicable.
- **Aliases**: Avoid aliases in scripts/modules (use `Select-Object` not `select`).

## Error Handling
- **Preferences**: Set `$ErrorActionPreference = 'Stop'` at the top of scripts.
- **Try/Catch**: Wrap risky operations in `try/catch` blocks.
- **Exceptions**: Throw typed exceptions where possible, or use `Write-Error`.

## Module Layout
```text
src/
  MyModule/
    MyModule.psd1        # Manifest
    MyModule.psm1        # Root module
    Public/              # Exported functions
      Get-MyWidget.ps1
    Private/             # Internal helper functions
      Invoke-Helper.ps1
tests/
  MyModule.Tests.ps1     # Pester tests
```

## Best Practices
- **Output**: Return objects, not text. Use `[PSCustomObject]`.
- **Pipeline**: Support pipeline input (`ValueFromPipeline`) where logical.
- **Comments**: Use distinct comments. Avoid block comments for single lines.
