#!/usr/bin/env python3
"""initialize.pl (Python)

Interactive initializer for this repository layout.

What it does:
- Prompts for the repo root folder
- Creates <repoRoot>/ai-agile if missing
- Copies dev-instructions/scripts/ai-agile.sample.json to <repoRoot>/ai-agile/ai-agile.json
- Rewrites basePaths to match the selected repo root

Run:
  python dev-instructions/scripts/initialize.pl

Optional non-interactive:
  python dev-instructions/scripts/initialize.pl --root C:\\path\\to\\dev-prompts
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _to_posix(path: Path) -> str:
    # Produces C:/... on Windows, /... on *nix
    return path.resolve().as_posix()


def _prompt_for_existing_dir(prompt: str) -> Path:
    while True:
        value = input(prompt).strip().strip('"')
        if not value:
            print("Please enter a path.")
            continue
        p = Path(value)
        if p.exists() and p.is_dir():
            return p
        print(f"Path not found or not a directory: {p}")


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in {path}: {e}") from e


def _write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _safe_mkdir(path: Path) -> bool:
    """Create a directory if missing.

    Returns True if created, False if it already existed.
    """
    if path.exists():
        return False
    path.mkdir(parents=True, exist_ok=True)
    return True


def _iter_stage_dirs(ai_agile_dir: Path, cfg: dict) -> list[Path]:
    """Compute stage directories from cfg.process.stepOrder + cfg.process.steps.

    Folders are treated as paths relative to ai_agile_dir.
    Also expands any optional `subfolders` values (relative paths).
    """
    process = cfg.get("process") or {}
    step_order = process.get("stepOrder") or []
    steps = process.get("steps") or {}

    stage_dirs: list[Path] = []
    for step_name in step_order:
        step = steps.get(step_name)
        if not isinstance(step, dict):
            continue

        folder = step.get("folder")
        if isinstance(folder, str) and folder.strip():
            stage_dirs.append(ai_agile_dir / folder.strip())

        subfolders = step.get("subfolders")
        if isinstance(subfolders, dict):
            for _label, rel in subfolders.items():
                if isinstance(rel, str) and rel.strip():
                    stage_dirs.append(ai_agile_dir / rel.strip())

    # De-dupe while preserving order
    seen: set[str] = set()
    out: list[Path] = []
    for p in stage_dirs:
        key = str(p.resolve())
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "--root",
        dest="repo_root",
        default=None,
        help="Repository root folder (the folder that will contain ai-agile/ and dev-instructions/)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite ai-agile/ai-agile.json if it already exists",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root) if args.repo_root else _prompt_for_existing_dir("Enter repo root folder path: ")
    repo_root = repo_root.resolve()

    dev_instructions_dir = repo_root / "dev-instructions"
    ai_instructions_dir = dev_instructions_dir / "ai-instructions"

    if not dev_instructions_dir.exists():
        print(f"[WARN] Expected folder not found: {dev_instructions_dir}")
    if not ai_instructions_dir.exists():
        print(f"[WARN] Expected folder not found: {ai_instructions_dir}")

    ai_agile_dir = repo_root / "ai-agile"
    ai_agile_already_exists = ai_agile_dir.exists()
    ai_agile_dir.mkdir(parents=True, exist_ok=True)

    script_dir = Path(__file__).resolve().parent
    sample_config = script_dir / "ai-agile.sample.json"
    if not sample_config.exists():
        print(f"[ERROR] Sample config not found: {sample_config}")
        return 2

    target_config = ai_agile_dir / "ai-agile.json"

    if target_config.exists() and not args.force:
        answer = input(f"{target_config} already exists. Overwrite? (y/N): ").strip().lower()
        if answer not in {"y", "yes"}:
            print("Aborted (no changes made).")
            return 0

    cfg = _load_json(sample_config)

    cfg.setdefault("basePaths", {})
    cfg["basePaths"]["repoRoot"] = _to_posix(repo_root)
    cfg["basePaths"]["aiAgileRoot"] = _to_posix(ai_agile_dir)
    cfg["basePaths"]["aiInstructionsRoot"] = _to_posix(ai_instructions_dir)

    _write_json(target_config, cfg)

    # Create stage folders (idempotent)
    stage_dirs = _iter_stage_dirs(ai_agile_dir, cfg)
    created: list[Path] = []
    existed: list[Path] = []
    for d in stage_dirs:
        if _safe_mkdir(d):
            created.append(d)
        else:
            existed.append(d)

    print("Initialized ai-agile workspace.")
    if ai_agile_already_exists:
        print(f"- ai-agile already existed: {ai_agile_dir}")
    else:
        print(f"- Created: {ai_agile_dir}")
    print(f"- Wrote config: {target_config}")
    if stage_dirs:
        print(f"- Stage folders: created={len(created)}, already-existed={len(existed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
