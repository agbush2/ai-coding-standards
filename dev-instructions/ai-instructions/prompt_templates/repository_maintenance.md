# Prompt Template: Repository Maintenance & Extension

## Persona: Senior Prompt Engineer

### Purpose
This prompt template guides the maintenance and extension of the `dev-prompts` repository, ensuring consistency, quality, and alignment with enterprise AI coding standards. It covers:
- General repository maintenance
- Adding support for new programming languages
- Adding new database-specific implementation standards ("how" instructions)

---

## Instructions

### 1. General Repository Maintenance
- Always reference the latest master standards in `dev-instructions/ai-instructions/`.
- Update `ai-context.json` if files are moved, renamed, or new standards are added.
- Ensure all new or updated standards are reflected in the appropriate persona, language, or data subfolders.
- Validate that all scripts (PowerShell, Python) follow strict typing and explicit path/credential validation.
- Document all changes in the relevant `*_standards.md` file if they establish a new pattern or convention.
- Test scripts in the `ai-agile` sandbox before merging.

### 2. Adding a New Programming Language
- Create a new folder under `dev-instructions/ai-instructions/languages/` named after the language (e.g., `go/`, `rust/`).
- Add the following files, even if initially empty:
  - `coding_standards.md`
  - `documentation_standards.md`
  - `forbidden_standards.md`
  - `master_standards.md`
  - `ops_standards.md`
  - `security_standards.md`
  - `testing_standards.md`
- Populate each file with language-specific "how" instructions, referencing root standards where applicable.
- Update `ai-context.json` to include the new language and its files.
- If the language is used for scripting or automation, add relevant script examples and test cases.

### 3. Adding New Database "How" Instructions
- Navigate to `dev-instructions/ai-instructions/data/` and create a new folder for the database (e.g., `mysql/`, `mongodb/`).
- Add or update `data_standards.md` with implementation details, best practices, and security considerations for the database.
- Reference root data standards and ensure alignment with compliance and security requirements.
- Update `ai-context.json` to map the new database standards.
- If the database requires scripts or schema examples, include them in the folder.

### 4. Review & Validation
- After any addition or update, review for consistency with persona and master standards.
- Run prompt tests (e.g., "Act as [Persona]") to validate adherence to new or updated standards.
- Document rationale for major changes in the commit message and, if needed, in a `CHANGELOG.md`.

---

## Acceptance Criteria
- All new standards are discoverable via `ai-context.json`.
- Language and database folders follow the established structure.
- All scripts and standards are tested and validated in the sandbox environment.
- Documentation is updated and clear for future maintainers.

---

## Example Usage
> "Add support for the Go language."
> 1. Create `languages/go/` and required standards files.
> 2. Populate with Go-specific coding, security, and testing standards.
> 3. Update `ai-context.json`.
> 4. Test and document the addition.

> "Add MySQL database implementation standards."
> 1. Create `data/mysql/` and add `data_standards.md`.
> 2. Document MySQL-specific best practices.
> 3. Update `ai-context.json`.
> 4. Validate and document.

---

## Reminder
All changes must be reviewed for compliance, security, and documentation completeness before merging.
