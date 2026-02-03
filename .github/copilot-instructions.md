# GitHub Copilot Instructions for `dev-prompts`

You are an expert AI development assistant working in the `dev-prompts` repository. This project focuses on defining, managing, and distributing enterprise-grade AI coding standards and integrating them with Atlassian Confluence.

## 🏗 Project Architecture & Structure

This repository is divided into two main components:

1.  **`dev-instructions/` (Core Product)**:
    *   Contains the "Source of Truth" for AI coding standards.
    *   **Structure**:
        *   `ai-instructions/`: Markdown files defining rules (Security, Architecture, etc.).
        *   `ai-instructions/personas/`: Role definitions (Developer, PM, QA).
        *   `scripts/`: PowerShell automation for Confluence sync (`download-confluence.ps1`, `upload-confluence.ps1`).
    *   **Key File**: `ai-instructions/ai-context.json` maps standards to files.

2.  **`ai-agile/` (Workspace/Usage)**:
    *   Represents a "user" environment where standards are applied.
    *   Stores downloaded Confluence content in `01_source-material/confluence/`.
    *   Contains local configuration (`.env`, `confluence.config`).

## 💻 Developer Workflows

### 1. Confluence Synchronization
*   **Scripts**: Located in `dev-instructions/scripts/`.
*   **Execution**:
    *   **Context Matters**: Scripts load `.env` from the **current working directory**.
    *   **Pattern**: always use `Set-Location` to the target configuration folder (e.g., `ai-agile/01_source-material/confluence`) before running scripts.
    *   **Permissions**: frequent need for `-ExecutionPolicy Bypass` if running on restricted setups.
    *   **Command**: `PowerShell -ExecutionPolicy Bypass -File "..\..\dev-instructions\scripts\download-confluence.ps1" -OutDir .` (relative path example)
*   **Configuration**:
    *   `confluence.config`: Defines `BaseUrl` and `PageId`.
    *   `.env`: Defines `CONF_EMAIL`, `CONF_TOKEN` (API Key), `BASE_URL`.

### 2. Standards Management
*   **"What" vs. "How"**:
    *   **Root Standards** (`dev-instructions/ai-instructions/*.md`): Universal principles (e.g., "Validate all inputs").
    *   **Language Standards** (`dev-instructions/ai-instructions/languages/<lang>/*.md`): Implementation details (e.g., "Use Pydantic").
*   **Personas**:
    *   Changes to behavior logic go in `dev-instructions/ai-instructions/persona_standards.md`.
    *   Role-specific prompts go in `dev-instructions/ai-instructions/personas/*.md`.

## 🧩 Project Conventions & Patterns

*   **Persona-Driven Development**: All AI interactions are scoped by a persona (Developer, PM, QA). Reference `persona_standards.md` for logic.
*   **Strict Typing**: Even in scripts (PowerShell), use `[CmdletBinding()]` and typed parameters.
*   **Zero Trust**: Scripts must validate credentials and paths explicitly.
*   **Documentation-First**: Changes to code must be reflected in the corresponding `*_standards.md` file if they establish a new pattern.

## ⚠️ Critical Files & Paths

*   `dev-instructions/ai-instructions/ai-context.json`: **MUST** be updated if files are moved or renamed.
*   `dev-instructions/.github/copilot-instructions.md`: The template instructions distributed to consumers of this project.
*   `.env`: Local development only. **NEVER** commit.

## 🧪 Testing & Validation
*   **Script Testing**: Test PowerShell scripts by running them against the `ai-agile` sandbox.
*   **Prompt Testing**: Validate updated standards by instructing an AI session to "Act as [Persona]" and verifying adherence to the new rules.

## 🚀 Common Commands

```powershell
# Sync Confluence content (Run from target directory)
Set-Location ai-agile\01_source-material\confluence
PowerShell -ExecutionPolicy Bypass -File "..\..\..\dev-instructions\scripts\download-confluence.ps1" -OutDir .
```
