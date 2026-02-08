---
**Skill Name**: Agent Design & Orchestration  
**Version**: 1.0 (2026-01-28)  
**Persona(s)**: Developer, Product Manager, Quality Engineer  
**Description**:  
Define how to design and orchestrate multi-step, tool-using agents that reuse skills, respect personas, and operate safely under repository standards.

**Usage Example**:
```prompt
Act as the Developer persona.
Design an agent workflow for <task> that:
- Breaks work into clear steps with checkpoints
- Uses existing skills from dev-instructions/ai-instructions/skills where relevant
- Applies change control: propose file changes and ask approval before write/execute actions
- Includes basic failure modes and recovery steps
```

**Implementation Notes**:
- [ ] Change control: before running tools/commands or creating/editing files, first propose the exact actions and file changes and ask for explicit approval.
- [ ] Prefer skill reuse over bespoke one-off prompting; keep agent behaviors modular.
- [ ] Related to: create_skills, clarifying_questions, code_review
---

# Agent Skills Standard

## Definition
An "agent" is an autonomous or semi-autonomous AI entity capable of multi-step reasoning, tool use, and persona-driven task execution. Agents leverage skills, prompt templates, and standards to perform complex workflows, often interacting with external systems or orchestrating other AI components.

## Design Guidelines
- **Prompt Structure**: Agents should maintain context, manage memory, and handle errors gracefully.
- **Persona Integration**: Agents must respect persona boundaries and reference relevant persona standards.
- **Skill Reuse**: Agents should invoke skills from this folder for modularity and consistency.
- **Security & Compliance**: Validate all actions, especially those involving external systems or sensitive data.
- **Orchestration**: Agents may coordinate multiple sub-tasks, invoking other agents or skills as needed.

## Agent Skill Template
---
**Agent Name**: _[Descriptive title]_  
**Version**: _[e.g., 1.0, or date: YYYY-MM-DD]_  
**Persona(s)**: _[Applicable personas]_  
**Description**:  
_A brief summary of the agent's purpose and capabilities._

**Usage Example**:
```prompt
[Insert a sample agent prompt or scenario.]
```

**Implementation Notes**:
- [ ] _List orchestration, dependencies, or related skills._
---

## Example Agent Skill
---
**Agent Name**: Code Review Agent  
**Version**: 1.0 (2026-01-28)  
**Persona(s)**: Developer, Quality Engineer  
**Description**:  
Performs automated code review using organization standards, asks clarifying questions, and suggests improvements.

**Usage Example**:
```prompt
Review the following code for compliance with our Python standards. If any requirement is unclear, ask a clarifying question before proceeding.
```

**Implementation Notes**:
- [ ] Uses: clarifying_questions, python/testing_standards
- [ ] Orchestrates: code_review, documentation feedback
---

## References
- Related skills: clarifying_questions.md, chain_of_thought.md
- Personas: developer.md, quality_engineer.md
- Prompt templates: code_review.md

---
