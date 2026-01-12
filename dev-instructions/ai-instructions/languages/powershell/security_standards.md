# PowerShell Security Standards
Implementation of: /security_standards.md

## Purpose
Enforce secure scripting practices and prevent common PowerShell attack vectors.

## 1. Injection Prevention
- **Invoke-Expression**: **STRICTLY FORBIDDEN**. Never use `iex` or `Invoke-Expression`.
- **Script Blocks**: Use `& $ScriptBlock` or `Invoke-Command -ScriptBlock` instead of string execution.
- **SQL**: Use parameterized queries with `Invoke-SqlCmd` or Ado.Net. Never concatenate SQL strings.

## 2. Credential Management
- **Interactive**: Use `Get-Credential` for interactive scripts.
- **Automation**: Accept `[PSCredential]` objects as parameters.
- **Secrets**: Never hardcode passwords. Use `SecretManagement` module or Azure Key Vault.
- **SecureString**: Use `ConvertTo-SecureString` and `ConvertFrom-SecureString` for local persistence if necessary (tied to user context).

## 3. Remote Execution
- **Remoting**: Use `Invoke-Command` over SSH (PS7+) or WinRM (HTTPS preferred).
- **Session Configuration**: Restrict JEA (Just Enough Administration) endpoints where possible.

## 4. Logging & Obfuscation
- **Protected Event Logging**: Ensure script block logging is enabled in the environment (GPO).
- **Log Forging**: Sanitize all user input before writing to event logs or files.
- **Secrets in Logs**: Absolutely no logging of credential objects or tokens.

## 5. File System
- **Paths**: Use `Join-Path` or `[System.IO.Path]::Combine`.
- **Validation**: Validate paths with `Test-Path` before operations. Avoid "TOCTOU" (Time of check to time of use) race conditions by using try/catch on file handles.

## 6. External Input
- **Validation**: Validate all parameters using `[ValidateSet()]`, `[ValidatePattern()]`, or `[ValidateScript()]`.
