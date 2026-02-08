---
**Skill Name**: Confluence Sync Workflow  
**Version**: 1.1 (2026-02-03)  
**Persona(s)**: Product Manager, Developer  
**Description**:  
Use the repository’s scripts to download/upload Confluence content reliably (JSON config discovery, safe handling of credentials, and dry-run-first uploads).

**Usage Example**:
```prompt
Goal: Pull the latest Confluence material into the local workspace, then (optionally) upload edits safely.

Pre-reqs:
- Ensure ai-agile/ai-agile.json exists (create it with dev-instructions/scripts/initialize.pl)
- Ensure ai-agile/01_source-material/confluence contains:
  - confluence.config (BaseUrl, PageId)
  - .env (CONF_EMAIL, CONF_TOKEN)  [never paste these into chat]

Download latest (preferred):
1) From repo root, run:
	python dev-instructions/scripts/download_confluence.py --no-attachments
	(use --attachments if you need images/files)
2) Verify updated .xhtml timestamps under ai-agile/01_source-material/confluence

Local work:
3) Convert / derive artifacts (if needed):
	python dev-instructions/scripts/confluence2md.py
4) Review and edit only local files; keep changes scoped and reversible.

Upload safely:
5) Preview changes:
	python dev-instructions/scripts/upload_confluence.py --dry-run
6) If the dry-run looks correct, upload:
	python dev-instructions/scripts/upload_confluence.py
```

**Implementation Notes**:
- [ ] Change control: before running any commands/scripts or creating/editing files, first propose the exact actions and file changes and ask for explicit approval.
- [ ] Scripts discover the Confluence folder via ai-agile/ai-agile.json (process.steps.SourceMaterial.subfolders.confluence). If auto-detection fails, pass `--ai-agile-root`.
- [ ] LLM behavior: when asked to “pull latest Confluence material”, instruct the user to run download_confluence.py locally first, then base analysis only on the refreshed local `.xhtml` (and any derived `.md`). Do not assume remote content.
- [ ] Prefer `--dry-run` for uploads; do not perform a real upload unless explicitly requested.
- [ ] Never paste secrets (CONF_TOKEN, CONF_EMAIL) into prompts, issues, or chat logs.
- [ ] Related to: documentation_quality, requirements_gathering
---
