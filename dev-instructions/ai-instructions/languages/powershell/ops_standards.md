# PowerShell Ops Standards
Implementation of: /ops_standards.md

## Build Process
- **Tool**: Invoke-Build or psake.
- **Tasks**:
    1.  Clean
    2.  Lint (PSScriptAnalyzer)
    3.  Test (Pester)
    4.  Build (Assemble module if necessary)
    5.  Publish

## CI/CD
- **Pipeline**: GitHub Actions or Azure Pipelines.
- **Matrix**: Test across required OS versions (Ubuntu-latest, Windows-latest) if cross-platform.

## Versioning
- **Semantic Versioning**: Follow SemVer (MAJOR.MINOR.PATCH).
- **Manifest**: Update `ModuleVersion` in `.psd1` automatically during build.

## Logging
- **Standard**: Use `Write-Verbose`, `Write-Warning`, `Write-Error`.
- **Debug**: Use `Write-Debug` for detailed developer tracing.
- **Structured**: If logging to file/backend, use structured JSON/Hashtables.
