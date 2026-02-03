# AI Coding Standards & Instructions

This serves as the **minimum viable foundation** for any development team to immediately bootstrap AI-assisted development with consistent, enterprise-grade standards. Rather than each team reinventing coding guidelines from scratch, this repository provides a battle-tested framework that can be copied into any project to instantly enable AI agents with professional-level architectural knowledge and security awareness.

**It is expected that Development leads, with their teams, take responsibility for evolving these prompts to best align with the team's culture and coding standards, learning as you go.**

## 🎯 Purpose

The goal of this project is to ensure that all AI-generated code and documentation:

1.  **Multi-Persona Support**: Adheres to specialized roles (**Developer**, **Product Manager**, **Quality Engineer**) rather than a generic assistant.
2.  **Strict Standards**: Follows **Security > Reliability > Maintainability > Performance** priorities.
3.  **Context Aware**: Implements specific language idioms and integrates with tooling like Confluence.

## 📂 Repository Structure

The core documentation is located in `dev-instructions/`.

```text
.
├── README.md                   # This file
└── dev-instructions/
    ├── ai-instructions/        # The knowledge base for AI
    │   ├── personas/           # 🎭 Role definitions (Dev, PM, QA)
    │   ├── persona_standards.md # 🚀 ENTRY POINT: Routing & Context
    │   ├── master_standards.md # Core Engineering Standards
    │   ├── ai-context.json     # Machine-readable context map
    │   └── languages/          # Language-specific implementations ("How")
    └── scripts/                # 🤖 Automation Tools
        ├── download-confluence.ps1 # Sync requirements from Confluence
        └── upload-confluence.ps1   # Publish docs/specs to Confluence
```

## 🚀 How to Use

### Project Setup

To implement these standards in your application:

1.  Copy the entire `dev-instructions/` folder into the **root level** of your project repository.
2.  Ensure that `dev-instructions/ai-instructions/persona_standards.md` is accessible.
3.  Commit these files to your version control system.

### For AI Agents (Context Loading)

When starting a new session with an AI coding assistant, provide the following context:

1.  **Primary Instruction**: "Read `dev-instructions/ai-instructions/persona_standards.md` to map your persona."
2.  **Activation**:
    *   "Act as **Developer**" (Default: Implementation & Architecture)
    *   "Act as **Product Manager**" (Requirements & User Stories)
    *   "Act as **QA**" (Testing & Verification)

### Confluence Integration

This project includes scripts to sync documentation with Atlassian Confluence:

*   **Download**: `scripts/download-confluence.ps1` - Fetches pages as XHTML/HTML to `ai-agile/01_source-material/confluence`.
*   **Upload**: `scripts/upload-confluence.ps1` - Pushes updates back to Confluence.

The **Product Manager** persona is trained to use these scripts for requirements gathering.

### The "What" vs. "How" Philosophy

This project separates universal principles from specific implementations:

* **The "What" (Root Docs)**: Universal rules.
  * *Example*: "All external inputs must be validated (Zero Trust)." (`security_standards.md`)
* **The "How" (Language Docs)**: Technical specifics.
  * *Example*: "Use Pydantic V2 `model_validator` for input validation." (`languages/python/coding_standards.md`)

## 🔑 Key Principles

* **Persona**: Senior Principal Engineer & Security Architect.
* **Mindset**: Zero Trust, Fail Fast, Explicit over Implicit.
* **Workflow**: Every task requires a "Plan of Action" covering Context, Files, Dependencies, Security, and Testing before code generation.

## 👮 Governance & Responsibility

It is now a **primary responsibility of the Development Manager** to take ownership of these master prompt files. This includes:

1. **Management**: Regularly reviewing and updating the content to reflect evolving team standards and technology choices.
2. **Alignment**: Ensuring the instructions in `dev-instructions/` accurately represent the architectural and security requirements of the specific application.
3. **Enforcement**: Verifying that the team (and their AI agents) are utilizing these standards during development.

## 🛠 Contributing

1. **Global Changes**: Edit files in `dev-instructions/` for rules that apply to all languages.
2. **Language Changes**: Edit files in `dev-instructions/languages/<lang>/` for syntax or tool-specific updates.
