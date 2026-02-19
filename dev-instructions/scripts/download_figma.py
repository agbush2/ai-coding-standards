#!/usr/bin/env python
"""download_figma.py

Download all files in a Figma Project into the ai-agile SourceMaterial folder.

Behavior mirrors the existing Confluence sync scripts in this repo:
- Auto-detects the ai-agile root (ai-agile.json) when possible
- Reads local credentials from <output_dir>/.env (never commit)
- Writes deterministic JSON artifacts into SourceMaterial (read-only evidence)

Required:
- FIGMA_TOKEN (Personal Access Token)
- FIGMA_PROJECT_ID

Typical run:
  python "dev-instructions\scripts\download_figma.py" --no-file-json

Or:
  python "dev-instructions\scripts\download_figma.py" --project-id <id> --token <token>

Output (default):
  <ai-agile-root>/01_source-material/figma/

Notes:
- This script downloads project file listings and (optionally) full file JSON via /v1/files/{key}.
- ai-agile is gitignored in this repository by design.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import requests


FIGMA_API_BASE_DEFAULT = "https://api.figma.com"


def _get_env_timeout(default: float = 30.0) -> float:
    value = os.environ.get("FIGMA_HTTP_TIMEOUT")
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


DEFAULT_TIMEOUT = _get_env_timeout(30.0)
REQUEST_TIMEOUT = DEFAULT_TIMEOUT


def load_env(env_path: Path) -> dict[str, str]:
    """Load environment variables from a .env file (simple KEY=VALUE lines)."""
    env: dict[str, str] = {}
    if not env_path.exists():
        return env
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def _redact_token(token: str) -> str:
    if not token:
        return ""
    if len(token) <= 8:
        return "[REDACTED]"
    return f"{token[:4]}...[REDACTED]...{token[-2:]}"


def _safe_filename(value: str, max_len: int = 120) -> str:
    safe = re.sub(r"[\\/:*?\"<>|]", "-", value).strip()
    safe = re.sub(r"\s+", " ", safe)
    if not safe:
        safe = "untitled"
    if len(safe) > max_len:
        safe = safe[:max_len]
    return safe


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in {path}: {e}") from e


def _find_ai_agile_root(start: Path, max_up: int = 8) -> Optional[Path]:
    """Find the ai-agile root directory (the directory that contains ai-agile.json).

    Handles cases where you run from repo root, dev-instructions/scripts, etc.
    """
    cur = start
    for _ in range(max_up):
        if (cur / "ai-agile.json").exists():
            return cur
        if (cur / "ai-agile" / "ai-agile.json").exists():
            return cur / "ai-agile"
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def _get_figma_rel_from_ai_agile_json(cfg: dict[str, Any]) -> str:
    """Return a relative path (from ai-agile root) to the figma source-material folder."""
    process = cfg.get("process") if isinstance(cfg, dict) else None
    if isinstance(process, dict):
        steps = process.get("steps")
        if isinstance(steps, dict):
            source_step = steps.get("SourceMaterial")
            if isinstance(source_step, dict):
                subfolders = source_step.get("subfolders")
                if isinstance(subfolders, dict):
                    figma = subfolders.get("figma")
                    if isinstance(figma, str) and figma.strip():
                        return figma.strip()
                folder = source_step.get("folder")
                if isinstance(folder, str) and folder.strip():
                    return f"{folder.strip().rstrip('/')}/figma"

    paths = cfg.get("paths") if isinstance(cfg, dict) else None
    if isinstance(paths, dict):
        source_material = paths.get("source_material")
        if isinstance(source_material, str) and source_material.strip():
            return f"{source_material.strip().rstrip('/')}/figma"

    return "01_source-material/figma"


@dataclass(frozen=True)
class ProjectFile:
    key: str
    name: str
    last_modified: Optional[str]
    thumbnail_url: Optional[str]


def _headers(token: str) -> dict[str, str]:
    return {
        "X-Figma-Token": token,
        "Accept": "application/json",
    }


def _figma_get(session: requests.Session, api_base: str, path: str, *, params: dict[str, Any] | None, token: str, verbose: bool) -> dict[str, Any]:
    url = api_base.rstrip("/") + path
    if verbose:
        printable_params = params or {}
        print(f"[DEBUG] GET {url} params={printable_params}")
        print(f"[DEBUG] X-Figma-Token={_redact_token(token)}")
    resp = session.get(url, headers=_headers(token), params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected response shape from {url}: expected object JSON")
    return data


def list_project_files(
    session: requests.Session,
    api_base: str,
    project_id: str,
    *,
    token: str,
    page_size: int,
    verbose: bool,
) -> list[ProjectFile]:
    """List all files in a project, handling pagination when present."""
    out: list[ProjectFile] = []

    cursor: Optional[str] = None
    while True:
        params: dict[str, Any] = {}
        if page_size > 0:
            params["page_size"] = page_size
        if cursor:
            params["cursor"] = cursor

        data = _figma_get(
            session,
            api_base,
            f"/v1/projects/{project_id}/files",
            params=params or None,
            token=token,
            verbose=verbose,
        )

        files = data.get("files")
        if not isinstance(files, list):
            raise RuntimeError("Figma API response missing 'files' list")

        for f in files:
            if not isinstance(f, dict):
                continue
            key = f.get("key")
            name = f.get("name")
            if not isinstance(key, str) or not key.strip():
                continue
            if not isinstance(name, str) or not name.strip():
                name = key
            out.append(
                ProjectFile(
                    key=key,
                    name=name,
                    last_modified=f.get("last_modified") if isinstance(f.get("last_modified"), str) else None,
                    thumbnail_url=f.get("thumbnail_url") if isinstance(f.get("thumbnail_url"), str) else None,
                )
            )

        # Pagination fields vary by API versions; be tolerant.
        next_cursor = data.get("next_cursor")
        next_page = data.get("next_page")
        if isinstance(next_cursor, str) and next_cursor.strip():
            cursor = next_cursor.strip()
            continue
        if isinstance(next_page, str) and next_page.strip():
            cursor = next_page.strip()
            continue

        break

    return out


def get_file_json(session: requests.Session, api_base: str, file_key: str, *, token: str, verbose: bool) -> dict[str, Any]:
    return _figma_get(
        session,
        api_base,
        f"/v1/files/{file_key}",
        params=None,
        token=token,
        verbose=verbose,
    )


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Download all Figma files in a project into ai-agile SourceMaterial.")
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=None,
        help="Output folder (default: auto-detect via ai-agile/ai-agile.json)",
    )
    parser.add_argument(
        "--ai-agile-root",
        dest="ai_agile_root",
        default=os.environ.get("AI_AGILE_ROOT"),
        help="Path to ai-agile root containing ai-agile.json (optional override)",
    )
    parser.add_argument(
        "--api-base",
        dest="api_base",
        default=os.environ.get("FIGMA_API_BASE", FIGMA_API_BASE_DEFAULT),
        help=f"Figma API base URL (default: {FIGMA_API_BASE_DEFAULT})",
    )
    parser.add_argument(
        "--project-id",
        dest="project_id",
        default=None,
        help="Figma Project ID (or set FIGMA_PROJECT_ID in .env/environment)",
    )
    parser.add_argument(
        "--token",
        dest="token",
        default=None,
        help="Figma PAT (or set FIGMA_TOKEN in .env/environment)",
    )
    parser.add_argument(
        "--page-size",
        dest="page_size",
        type=int,
        default=100,
        help="Page size for project file listing (default: %(default)s)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="HTTP timeout (seconds) for Figma requests (default: %(default)s)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing downloaded artifacts",
    )
    parser.add_argument(
        "--no-file-json",
        action="store_true",
        help="Only download the project file listing + manifest (skip /v1/files/{key})",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging (secrets are redacted)",
    )

    args = parser.parse_args()

    global REQUEST_TIMEOUT
    REQUEST_TIMEOUT = max(args.timeout, 0.1)

    output_dir: Path
    if args.output_dir:
        output_dir = Path(args.output_dir).expanduser().resolve()
    else:
        cwd = Path.cwd()
        ai_agile_root = Path(args.ai_agile_root).expanduser().resolve() if args.ai_agile_root else _find_ai_agile_root(cwd)
        if ai_agile_root is None:
            raise RuntimeError(
                "Could not locate ai-agile root. Provide --ai-agile-root, pass output_dir, or run from within the repository."
            )

        ai_agile_json_path = ai_agile_root / "ai-agile.json"
        if not ai_agile_json_path.exists():
            raise RuntimeError(
                f"Expected ai-agile.json at {ai_agile_json_path}, but it was not found. "
                "Run dev-instructions/scripts/initialize.pl or create ai-agile/ai-agile.json manually."
            )

        cfg = _load_json(ai_agile_json_path)
        rel = _get_figma_rel_from_ai_agile_json(cfg)
        output_dir = (ai_agile_root / rel).resolve()

    output_dir.mkdir(parents=True, exist_ok=True)

    env = load_env(output_dir / ".env")
    token = args.token or env.get("FIGMA_TOKEN") or os.environ.get("FIGMA_TOKEN")
    project_id = args.project_id or env.get("FIGMA_PROJECT_ID") or os.environ.get("FIGMA_PROJECT_ID")

    if not token:
        raise RuntimeError(
            "Missing FIGMA_TOKEN. Provide --token, set FIGMA_TOKEN in environment, or add it to <output_dir>/.env."
        )
    if not project_id:
        raise RuntimeError(
            "Missing FIGMA_PROJECT_ID. Provide --project-id, set FIGMA_PROJECT_ID in environment, or add it to <output_dir>/.env."
        )

    retrieved_at = datetime.datetime.now(datetime.UTC).isoformat()

    session = requests.Session()

    files = list_project_files(
        session,
        args.api_base,
        project_id,
        token=token,
        page_size=args.page_size,
        verbose=args.verbose,
    )

    manifest_dir = output_dir
    listing_path = manifest_dir / "project-files.json"
    manifest_path = manifest_dir / "manifest.json"

    listing_obj = {
        "projectId": project_id,
        "retrievedAt": retrieved_at,
        "apiBase": args.api_base,
        "files": [
            {
                "key": f.key,
                "name": f.name,
                "lastModified": f.last_modified,
                "thumbnailUrl": f.thumbnail_url,
                "url": f"https://www.figma.com/file/{f.key}",
            }
            for f in files
        ],
    }

    _write_json(listing_path, listing_obj)

    file_outputs: list[dict[str, Any]] = []
    skipped = 0
    downloaded = 0

    files_dir = output_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    if not args.no_file_json:
        for f in files:
            safe_name = _safe_filename(f.name)
            out_path = files_dir / f"{f.key}-{safe_name}.json"
            if out_path.exists() and not args.force:
                skipped += 1
                file_outputs.append(
                    {
                        "key": f.key,
                        "name": f.name,
                        "lastModified": f.last_modified,
                        "url": f"https://www.figma.com/file/{f.key}",
                        "relativePath": str(out_path.relative_to(output_dir)).replace("\\", "/"),
                        "sha256": None,
                        "status": "skipped-existing",
                    }
                )
                continue

            data = get_file_json(session, args.api_base, f.key, token=token, verbose=args.verbose)
            raw = (json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
            sha = _sha256_bytes(raw)
            out_path.write_bytes(raw)
            downloaded += 1

            file_outputs.append(
                {
                    "key": f.key,
                    "name": f.name,
                    "lastModified": f.last_modified,
                    "url": f"https://www.figma.com/file/{f.key}",
                    "relativePath": str(out_path.relative_to(output_dir)).replace("\\", "/"),
                    "sha256": sha,
                    "status": "downloaded",
                }
            )

    manifest_obj = {
        "projectId": project_id,
        "retrievedAt": retrieved_at,
        "apiBase": args.api_base,
        "outputDir": str(output_dir).replace("\\", "/"),
        "counts": {
            "projectFiles": len(files),
            "downloaded": downloaded,
            "skipped": skipped,
            "fileJsonEnabled": not args.no_file_json,
        },
        "artifacts": {
            "projectListing": "project-files.json",
            "filesFolder": "files/" if not args.no_file_json else None,
        },
        "files": file_outputs,
    }

    _write_json(manifest_path, manifest_obj)

    print(f"Wrote: {listing_path}")
    print(f"Wrote: {manifest_path}")
    if args.no_file_json:
        print(f"Skipped file JSON download (use without --no-file-json to fetch /v1/files/{{key}})")
    else:
        print(f"File JSON: downloaded={downloaded}, skipped_existing={skipped}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
