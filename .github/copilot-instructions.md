# Copilot instructions for dev-prompts

This repository is a standards knowledge-base plus Confluence sync tooling.

## Big picture
- `dev-instructions/`: source-of-truth AI standards + scripts
- `ai-agile/`: sandbox workspace where synced source material and generated artifacts live

## Mandatory context loading (use these files, not generic advice)
1. Persona routing + behavior rules: `dev-instructions/ai-instructions/persona_standards.md`
2. Global rules: `dev-instructions/ai-instructions/master_standards.md`
3. Forbidden patterns: `dev-instructions/ai-instructions/forbidden_standards.md`
4. If you need a map: `dev-instructions/ai-instructions/llms.txt` and `dev-instructions/ai-instructions/ai-context.json`

## Structure you must preserve
- Root standards (“what”): `dev-instructions/ai-instructions/*.md`
- Language standards (“how”): `dev-instructions/ai-instructions/languages/<lang>/*.md`
- Personas: `dev-instructions/ai-instructions/personas/`
- If you move/rename standards files, update `dev-instructions/ai-instructions/ai-context.json`

## Confluence synchronization (project-specific workflow)
- Scripts (preferred):
  - Download: `dev-instructions/scripts/download_confluence.py`
  - Upload: `dev-instructions/scripts/upload_confluence.py`
- Config discovery: `ai-agile/ai-agile.json` defines the source-material folder and the Confluence subfolder.
- The Confluence config folder must contain:
  - `.env` (local only; NEVER commit) with `CONF_EMAIL`, `CONF_TOKEN`, `BASE_URL`
  - `confluence.config` with `BaseUrl`, `PageId`

```powershell
python "dev-instructions\scripts\download_confluence.py" --no-attachments
python "dev-instructions\scripts\upload_confluence.py" --dry-run
```

## Change control (repo rule)
Before modifying files or running write/execute actions: propose the exact changes (files + brief bullets) and wait for explicit approval.
