---
**Skill Name**: Create Skills (Authoring + Standards Validation)  
**Version**: 1.0 (2026-02-06)  
**Persona(s)**: Developer, Product Manager, Quality Engineer  
**Description**:  
Create new reusable skill files in this repository using the canonical skill template and validate them against the latest standards (master, persona, security, documentation, tools, and any domain-specific standards).

**Usage Example**:
```prompt
Act as the repository GenAI maintainer.
Create a new skill called "<skill_name>".

Requirements:
- Use the repo’s standard skill template (skill card).
- Include: Skill Name, Version, Persona(s), Description, Usage Example, Implementation Notes.
- In Implementation Notes, include a short validation checklist against current standards.
- Propose the exact file changes and ask for approval before creating/editing any files.

After approval:
1) Create the new skill file under dev-instructions/ai-instructions/skills/
2) Validate it against master_standards.md + persona_standards.md + security_standards.md + documentation_standards.md + tools_standards.md
3) Report any gaps and propose fixes.
```

**Implementation Notes**:
- [ ] **Change control (required)**: before creating/editing any files or running any scripts/commands, first propose the exact file changes (paths + brief bullets) and ask for explicit approval.
- [ ] **Where to place new skills**: create the skill under `dev-instructions/ai-instructions/skills/` with a clear, descriptive filename (snake_case preferred), e.g., `clarifying_questions.md`.
- [ ] **Best-practice skill template (copy/paste)**: use this exact shape for new skills:

  ```markdown
  ---
  **Skill Name**: <Concise, descriptive title>  
  **Version**: <e.g., 1.0 (YYYY-MM-DD)>  
  **Persona(s)**: <Developer | Product Manager | Quality Engineer | ...>  
  **Description**:  
  <What the skill enables; keep it short and concrete.>

  **Usage Example**:
  ```prompt
  <A realistic prompt that demonstrates the skill.>
  ```

  **Implementation Notes**:
  - [ ] <High-signal do/don’t rules; keep it actionable.>
  - [ ] <List dependencies, inputs/outputs, or related skills.>
  - [ ] Change control reminder if the skill may trigger writes/exec.
  ---
  ```

- [ ] **Template conformance checks**:
  - [ ] Skill card is present and uses `---` delimiters.
  - [ ] Fields are present: **Skill Name**, **Version**, **Persona(s)**, **Description**, **Usage Example**, **Implementation Notes**.
  - [ ] Usage Example contains at least one concrete acceptance-style instruction (what “done” looks like).
  - [ ] Implementation Notes include: related skills (when applicable) and a permission gate reminder (when the skill may cause writes/exec).

- [ ] **Standards validation (latest)**: validate the new skill against:
  - [ ] `dev-instructions/ai-instructions/master_standards.md` (persona/mindset, priorities, plan-of-action expectations, permission gate, doc hierarchy)
  - [ ] `dev-instructions/ai-instructions/persona_standards.md` (persona activation + persona bias; PM defaults to artifacts vs tooling)
  - [ ] `dev-instructions/ai-instructions/security_standards.md` (no secrets, zero-trust inputs, safe defaults)
  - [ ] `dev-instructions/ai-instructions/documentation_standards.md` (documentation clarity expectations)
  - [ ] `dev-instructions/ai-instructions/tools_standards.md` (tooling guidance; avoid unnecessary new tooling)
  - [ ] Plus any relevant domain standards (e.g., testing/architecture/API/data/frontend/ops) based on the skill scope.

- [ ] **Quality bar**:
  - [ ] Skill scope is narrow and reusable (not project-specific).
  - [ ] Guidance is deterministic where possible (clear ordering, limits like “ask up to 5 questions”, etc.).
  - [ ] Avoids encouraging unsafe behavior (secrets, destructive commands, touching immutable source materials).

- [ ] **Cross-linking (recommended)**:
  - [ ] Add a “Related to:” line in Implementation Notes pointing to adjacent skills (e.g., `requirements_gathering`, `security_review`, `test_case_generation`).
  - [ ] If a skill defines a new repeated pattern, consider updating the relevant standards doc (documentation-first), but only with explicit approval.
---
