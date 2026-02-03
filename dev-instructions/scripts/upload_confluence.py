import os
import argparse
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

import requests


def _get_env_timeout(default: float = 15.0) -> float:
    value = os.environ.get("CONFLUENCE_HTTP_TIMEOUT")
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


DEFAULT_TIMEOUT = _get_env_timeout(15.0)
REQUEST_TIMEOUT = DEFAULT_TIMEOUT


def load_env(env_path: Path) -> Dict[str, str]:
    env = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.strip().startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env

def load_config(config_path: Path) -> Dict[str, str]:
    config = {}
    if config_path.exists():
        for line in config_path.read_text().splitlines():
            if line.strip().startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            config[k.strip()] = v.strip()
    return config

def get_auth_header(email: str, token: str) -> Dict[str, str]:
    import base64
    pair = f"{email}:{token}"
    b64 = base64.b64encode(pair.encode()).decode()
    return {"Authorization": f"Basic {b64}", "Accept": "application/json"}

def parse_front_matter(content: str):
    """Parse simple YAML-style front matter while preserving exact body text."""
    if not content.startswith('---'):
        return {}, content

    newline = '\r\n' if content.startswith('---\r\n') else '\n'
    closing_marker = f"{newline}---{newline}"
    start_offset = len('---' + newline)
    end_index = content.find(closing_marker, start_offset)

    if end_index == -1:
        # Fallback to legacy splitlines approach if markers aren't well-formed
        lines = content.splitlines()
        front = {}
        body_start = None
        in_front = False
        for i, line in enumerate(lines):
            if line.strip() == '---':
                if not in_front:
                    in_front = True
                    continue
                body_start = i + 1
                break
            if in_front:
                m = re.match(r'([^:]+):\s*(.+)', line)
                if m:
                    front[m.group(1).strip()] = m.group(2).strip()
        body = '\n'.join(lines[body_start:]) if body_start is not None else ''
        return front, body

    front_block = content[start_offset:end_index]
    body = content[end_index + len(closing_marker):]

    front = {}
    for line in front_block.splitlines():
        m = re.match(r'([^:]+):\s*(.+)', line)
        if m:
            front[m.group(1).strip()] = m.group(2).strip()

    return front, body

def get_macro_counts(content: str):
    return {
        'structured_macro': len(re.findall(r'<ac:structured-macro', content)),
        'image': len(re.findall(r'<ac:image', content)),
        'link': len(re.findall(r'<ac:link', content)),
    }

def get_md5_exact(content: str):
    """Return MD5 of the content exactly as-is (no normalization)."""
    return hashlib.md5(content.encode('utf-8')).hexdigest() if content else ''

def get_page(base_url: str, page_id: str, headers: Dict[str, str]):
    url = f"{base_url}/wiki/rest/api/content/{page_id}?expand=version"
    resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def update_page(base_url: str, page_id: str, title: str, body: str, version: int, headers: Dict[str, str]):
    url = f"{base_url}/wiki/rest/api/content/{page_id}"
    payload = {
        "id": page_id,
        "type": "page",
        "title": title,
        "version": {"number": version},
        "body": {"storage": {"value": body, "representation": "storage"}}
    }
    resp = requests.put(
        url,
        headers={**headers, "Content-Type": "application/json; charset=utf-8"},
        data=json.dumps(payload),
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def load_ai_agile_json(config_path: Path) -> Dict[str, Any]:
    """Load configuration from ai-agile.json file."""
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in {config_path}: {e}") from e


def _get_confluence_rel_from_ai_agile_json(cfg: Dict[str, Any]) -> str:
    """Return a relative path (from ai-agile root) to the confluence config folder."""
    process = cfg.get("process") if isinstance(cfg, dict) else None
    if isinstance(process, dict):
        steps = process.get("steps")
        if isinstance(steps, dict):
            source_step = steps.get("SourceMaterial")
            if isinstance(source_step, dict):
                subfolders = source_step.get("subfolders")
                if isinstance(subfolders, dict):
                    confluence = subfolders.get("confluence")
                    if isinstance(confluence, str) and confluence.strip():
                        return confluence.strip()
                folder = source_step.get("folder")
                if isinstance(folder, str) and folder.strip():
                    return f"{folder.strip().rstrip('/')}/confluence"

    paths = cfg.get("paths") if isinstance(cfg, dict) else None
    if isinstance(paths, dict):
        source_material = paths.get("source_material")
        if isinstance(source_material, str) and source_material.strip():
            return f"{source_material.strip().rstrip('/')}/confluence"

    return "01_source-material/confluence"


def _find_ai_agile_root(start: Path, max_up: int = 8) -> Optional[Path]:
    """Find the ai-agile root directory (the directory that contains ai-agile.json).
    Handles cases where you're in repo root, dev-instructions/scripts, etc."""
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

def main():
    parser = argparse.ArgumentParser(description="Upload local Confluence storage exports back to Confluence.")
    parser.add_argument(
        "source_dir",
        nargs="?",
        default=None,
        help="Directory containing exported .xhtml files and credentials (default: auto-detect via ai-agile/ai-agile.json)",
    )
    parser.add_argument(
        "--ai-agile-root",
        dest="ai_agile_root",
        default=os.environ.get("AI_AGILE_ROOT"),
        help="Path to ai-agile root containing ai-agile.json (optional override)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without uploading",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="HTTP timeout (seconds) for Confluence requests (default: %(default)s)",
    )
    args = parser.parse_args()

    if args.source_dir:
        source_dir = Path(args.source_dir).expanduser().resolve()
    else:
        cwd = Path.cwd()
        ai_agile_root = Path(args.ai_agile_root).expanduser().resolve() if args.ai_agile_root else _find_ai_agile_root(cwd)
        if ai_agile_root is None:
            # As a last resort, try repo-root/ai-agile if present
            if (cwd / "ai-agile" / "ai-agile.json").exists():
                ai_agile_root = cwd / "ai-agile"
            elif (cwd.parent / "ai-agile" / "ai-agile.json").exists():
                ai_agile_root = cwd.parent / "ai-agile"

        if ai_agile_root is None:
            raise RuntimeError(
                "Could not locate ai-agile root. Provide --ai-agile-root or run from within the repository."
            )

        ai_agile_json_path = ai_agile_root / "ai-agile.json"
        if not ai_agile_json_path.exists():
            raise RuntimeError(
                f"Expected ai-agile.json at {ai_agile_json_path}, but it was not found. "
                "Run dev-instructions/scripts/initialize.pl or create ai-agile/ai-agile.json manually."
            )

        ai_agile_cfg = load_ai_agile_json(ai_agile_json_path)
        confluence_rel = _get_confluence_rel_from_ai_agile_json(ai_agile_cfg)
        source_dir = (ai_agile_root / confluence_rel).resolve()

    if not source_dir.exists():
        print(f"Source directory '{source_dir}' does not exist.")
        return

    if not (source_dir / "confluence.config").exists():
        print(f"Expected confluence.config in '{source_dir}', but it was not found.")
        return

    env = load_env(source_dir / ".env")
    config = load_config(source_dir / "confluence.config")
    base_url = config.get("BaseUrl") or env.get("BASE_URL") or os.environ.get("BASE_URL")
    email = env.get("CONF_EMAIL") or os.environ.get("CONF_EMAIL")
    token = env.get("CONF_TOKEN") or os.environ.get("CONF_TOKEN")
    dry_run = args.dry_run

    global REQUEST_TIMEOUT
    REQUEST_TIMEOUT = max(args.timeout, 0.1)

    if not all([base_url, email, token]):
        print("Missing credentials: set BASE_URL, CONF_EMAIL, and CONF_TOKEN via .env or environment.")
        return

    headers = get_auth_header(email, token)
    # Test authentication
    try:
        test_url = f"{base_url}/wiki/rest/api/space?limit=1"
        resp = requests.get(test_url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        print(f"Authenticated with Confluence at {base_url}.")
    except Exception as e:
        print(f"Confluence auth failed: {e}")
        return

    files = sorted(source_dir.glob("*.xhtml"))
    if not files:
        print(f"No .xhtml files found in '{source_dir}'. Nothing to upload.")
        return
    print(f"Found {len(files)} file(s) to process.")

    would_update = []
    skipped = []

    for file in files:
        # Extract space name from filename (assumes format: Space-Id-Title.xhtml)
        fname = file.name
        space_name = None
        m = re.match(r'([^-]+)-[0-9]+-', fname)
        if m:
            space_name = m.group(1)
        print(f"\nProcessing file: {file.name} (Space: {space_name if space_name else 'Unknown'})")
        content = file.read_text(encoding="utf-8")
        meta, body = parse_front_matter(content)
        if not meta or 'confluence_id' not in meta:
            print(f"Skipping file with no front-matter or confluence_id: {file.name}")
            continue
        # Check for content changes using hash
        change_detected = True
        reason = "No hashes found"
        if 'output_hash' in meta:
            current_output_hash = get_md5_exact(body)
            if current_output_hash == meta['output_hash']:
                print("  - No changes detected (output hash matches). Skipping.")
                skipped.append((file, meta.get('confluence_id', '?')))
                continue
            change_detected = True
            reason = "output hash mismatch"
            print("  - Changes detected (output hash mismatch). Proceeding with update.")
        elif 'content_hash' in meta:
            # Fallback when output_hash is absent; content_hash is of raw storage body.
            # We cannot perfectly reconstruct storage body from the saved file (it may include readability line breaks),
            # so treat as change (conservative) to avoid missing updates.
            change_detected = True
            reason = "no output_hash; conservative update"
            print("  - No output_hash present; cannot reliably detect formatting-only changes. Proceeding with update.")
        else:
            change_detected = True
            reason = "no hashes present"
            print("  - No hashes found in front-matter. Proceeding with update.")
        # Warn if macro counts appear reduced compared to original snapshot
        new_counts = get_macro_counts(body)
        orig_structured = int(meta.get('macro_structured_macro', 0))
        orig_image = int(meta.get('macro_image', 0))
        orig_link = int(meta.get('macro_link', 0))
        if orig_structured > 0 and new_counts['structured_macro'] < orig_structured:
            print(f"  - Structured macro count decreased: {new_counts['structured_macro']} vs original {orig_structured}. Verify no macros were lost.")
        if orig_image > 0 and new_counts['image'] < orig_image:
            print(f"  - Image macro count decreased: {new_counts['image']} vs original {orig_image}.")
        if orig_link > 0 and new_counts['link'] < orig_link:
            print(f"  - Link macro count decreased: {new_counts['link']} vs original {orig_link}.")
        try:
            page_id = meta['confluence_id']
            print(f"  - Found Confluence Page ID: {page_id}")
            current_page = get_page(base_url, page_id, headers)
            current_version = current_page['version']['number']
            new_version = current_version + 1
            print(f"  - Current version: {current_version}. Updating to version: {new_version}.")
            if dry_run:
                would_update.append((file, page_id, current_page['title'], new_version, reason))
                print(f"  - [DRY RUN] Would update page '{current_page['title']}' (ID: {page_id}) to version {new_version}. Reason: {reason}.")
            else:
                print(f"  - Updating page '{current_page['title']}' (ID: {page_id})...")
                result = update_page(base_url, page_id, current_page['title'], body, new_version, headers)
                print(f"  - Successfully updated. New version is {result['version']['number']}.")
        except Exception as e:
            print(f"Failed to process file {file.name}. Reason: {e}")
    print("\nUpload process finished.")
    if dry_run:
        print("\nDry-run summary:")
        print(f"  Would update: {len(would_update)} page(s)")
        for f, pid, title, ver, why in would_update:
            print(f"   - {f.name} (ID: {pid}) -> '{title}' v{ver} [{why}]")
        print(f"  Skipped (unchanged): {len(skipped)} page(s)")
        for f, pid in skipped:
            print(f"   - {f.name} (ID: {pid})")

if __name__ == "__main__":
    main()
