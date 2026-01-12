# PowerShell Forbidden Standards
Applies to: All PowerShell Code

## Critical Blocks
The following code patterns are strictly prohibited.

1.  **Invoke-Expression (`iex`)**
    - **Reason**: Arbitrary code execution vulnerability.
    - **Alternative**: `&` operator, `Invoke-Command`, or refactoring logic.

2.  **Hardcoded Credentials**
    - **Reason**: Security risk.
    - **Alternative**: `[PSCredential]`, `Get-Credential`, Key Vault.

3.  **Aliases in Scripts**
    - **Reason**: Reduces readability and reliability (aliases can change).
    - **Banned**: `ls`, `curl`, `wget`, `gwmi`, `select`, `where`, `%`, `?`.
    - **Alternative**: Use full cmdlet names (`Get-ChildItem`, `Invoke-WebRequest`, `Select-Object`).

4.  **Write-Host (for data)**
    - **Reason**: Breaks the pipeline.
    - **Alternative**: `Write-Output` (for data), `Write-Information`, `Write-Verbose`.
    - **Exception**: Interactive user prompts (e.g. colors for console UI), but sparingly.

5.  **Positional Parameters (Implicit)**
    - **Reason**: Fragile and hard to read.
    - **Alternative**: Always use named parameters in scripts (e.g. `Get-Item -Path .` not `Get-Item .`).
