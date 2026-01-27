## Quick Start for Agents

When asked to write PowerShell code:

1. Read `/master_instructions.md` for the plan.
2. Read `languages/powershell/coding_standards.md` for style and module structure.
3. Read `languages/powershell/examples.md` for templates.
4. Check `languages/powershell/forbidden_standards.md` before finalizing.
# POWERSHELL INSTRUCTIONS (The "How")
Version: 1.0.0
Parent: /master_instructions.md

## Relationship to Standards
This file provides the PowerShell-specific implementation ("How") for the global master instructions defined in `/master_instructions.md` ("What"). It serves as the entry point for all PowerShell-related code generation tasks.

## Purpose
Provide PowerShell-specific implementation details for the Global Standards.

## Reference Map
| Standard | PowerShell Implementation File |
| :--- | :--- |
| **Coding Style** | `coding_standards.md` |
| **Testing** | `testing_standards.md` |
| **Security** | `security_standards.md` |
| **CI/CD** | `ops_standards.md` |
| **Documentation** | `documentation_standards.md` |
| **Forbidden** | `forbidden_standards.md` |

## PowerShell Persona
- **Version**: PowerShell 7.4+ (Core) preferred, Windows PowerShell 5.1 compatible where necessary.
- **Paradigm**: Module-based development, Pipeline-oriented.
- **Linting**: PSScriptAnalyzer.
- **Testing**: Pester 5+.

## Quick Start for Agents

When asked to write PowerShell code:

1. Read `/master_instructions.md` for the plan.
2. Read `languages/powershell/coding_standards.md` for style and module structure.
3. Read `languages/powershell/security_standards.md` for secure execution and credential handling.
4. Check `languages/powershell/forbidden_standards.md` before finalizing.
