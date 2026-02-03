import os
import sys
import argparse
import datetime
import hashlib
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional

import requests


def _get_env_timeout(default: float = 15.0) -> float:
    """Parse CONFLUENCE_HTTP_TIMEOUT from environment, returning default on error."""
    value = os.environ.get("CONFLUENCE_HTTP_TIMEOUT")
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


DEFAULT_TIMEOUT = _get_env_timeout(15.0)
REQUEST_TIMEOUT = DEFAULT_TIMEOUT

def redact_headers_for_debug(headers: Dict[str, str]) -> Dict[str, str]:
    """Return a copy of headers with secrets masked for debug logging."""
    redacted = dict(headers or {})
    auth = redacted.get("Authorization")
    if auth:
        try:
            scheme, _val = auth.split(" ", 1)
            redacted["Authorization"] = f"{scheme} [REDACTED]"
        except Exception:
            redacted["Authorization"] = "[REDACTED]"
    return redacted

def load_env(env_path: Path) -> Dict[str, str]:
    """
    Load environment variables from a .env file.
    Returns a dictionary of key-value pairs.
    """
    env = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.strip().startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env

def load_config(config_path: Path) -> Dict[str, str]:
    """
    Load configuration from a confluence.config file.
    Returns a dictionary of key-value pairs.
    """
    config = {}
    if config_path.exists():
        for line in config_path.read_text().splitlines():
            if line.strip().startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            config[k.strip()] = v.strip()
    return config

def get_auth_header(email: str, token: str) -> Dict[str, str]:
    """
    Create HTTP headers for Basic Auth using email and API token.
    Returns a dictionary suitable for requests headers.
    """
    import base64
    pair = f"{email}:{token}"
    b64 = base64.b64encode(pair.encode()).decode()
    return {"Authorization": f"Basic {b64}", "Accept": "application/json"}


def get_page(base_url: str, page_id: str, headers: Dict[str, str]) -> Any:
    """
    Fetch a Confluence page by ID using the REST API.
    Returns the page JSON object.
    """
    url = f"{base_url}/wiki/rest/api/content/{page_id}?expand=body.storage,version,ancestors,space"
    if hasattr(get_page, 'verbose') and get_page.verbose:
        print(f"[DEBUG] GET PAGE URL: {url}")
        print(f"[DEBUG] HEADERS: {redact_headers_for_debug(headers)}")
    resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def _add_linebreaks_after_tags(xhtml: str, newline: str = "\n") -> str:
    """Insert line breaks after select closing HTML tags to improve readability.
    Does not alter semantics; operates purely on text formatting.

    Tags targeted: p, li, tr, td, th, h1-h6, pre, blockquote.
    """
    if not xhtml:
        return xhtml
    # Match closing tags (case-insensitive)
    pattern = re.compile(r"(</(?:p|li|tr|td|th|h[1-6]|pre|blockquote|div|table)>)", re.IGNORECASE)
    return pattern.sub(r"\1" + newline, xhtml)

def get_attachments(base_url: str, page_id: str, headers: Dict[str, str]) -> list:
    """
    Fetch all attachments for a Confluence page by ID.
    Returns a list of attachment JSON objects.
    """
    url = f"{base_url}/wiki/rest/api/content/{page_id}/child/attachment?limit=100"
    if hasattr(get_attachments, 'verbose') and get_attachments.verbose:
        print(f"[DEBUG] GET ATTACHMENTS URL: {url}")
        print(f"[DEBUG] HEADERS: {redact_headers_for_debug(headers)}")
    resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json().get("results", [])

def get_children(base_url: str, page_id: str, headers: Dict[str, str]) -> Any:
    """
    Fetch all child pages for a Confluence page by ID.
    Returns a list of child page JSON objects.
    """
    url = f"{base_url}/wiki/rest/api/content/{page_id}/child/page?limit=100"
    if hasattr(get_children, 'verbose') and get_children.verbose:
        print(f"[DEBUG] GET CHILDREN URL: {url}")
        print(f"[DEBUG] HEADERS: {redact_headers_for_debug(headers)}")
    resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json().get("results", [])


def save_page(page: Dict[str, Any], out_dir: Path, base_url: str, headers: Dict[str, str], verbose: bool = False, attachments: list = None, download_attachments: bool = True, linebreak_mode: str = "none"):
    """
    Save a Confluence page as an .xhtml file with front-matter metadata.
    Optionally download attachments and images to the output directory.
    """
    title = page.get("title", "untitled")
    page_id = page.get("id")
    xhtml = page.get("body", {}).get("storage", {}).get("value", "")
    version = page.get("version", {}).get("number", "")
    space = page.get("space", {}).get("key", "")
    # Sanitize title: replace invalid chars, trim, limit length
    safe_title = re.sub(r'[\\/:*?"<>|]', '-', title).strip()
    if len(safe_title) > 120:
        safe_title = safe_title[:120]
    file_name = f"{space}-{page_id}-{safe_title}.xhtml"
    file_path = out_dir / file_name

    # Download attachments if enabled
    if download_attachments and attachments:
        for att in attachments:
            att_title = att.get('title', 'attachment')
            att_id = att.get('id', '')
            att_ext = Path(att_title).suffix or ''
            att_safe_title = re.sub(r'[\\/:*?"<>|]', '-', att_title).strip()
            if len(att_safe_title) > 120:
                att_safe_title = att_safe_title[:120]
            att_file_name = f"{space}-{page_id}-{att_safe_title}"
            att_file_path = out_dir / att_file_name
            att_url = att.get('_links', {}).get('download')
            if att_url:
                try:
                    # Ensure /wiki is present before /download/attachments
                    if att_url.startswith('/download/'):
                        wiki_base = base_url.rstrip('/') + '/wiki'
                        full_url = wiki_base + att_url
                    else:
                        full_url = base_url.rstrip('/') + att_url
                    if verbose:
                        print(f"[DEBUG] DOWNLOAD ATTACHMENT URL: {full_url}")
                        print(f"[DEBUG] HEADERS: {redact_headers_for_debug(headers)}")
                    resp = requests.get(full_url, headers=headers, timeout=REQUEST_TIMEOUT)
                    resp.raise_for_status()
                    att_file_path.write_bytes(resp.content)
                    if verbose:
                        print(f"Downloaded attachment: {att_file_path}")
                except Exception as e:
                    print(f"Failed to download attachment {att_title}: {e}")

    # Download images (from <ac:image> tags)
    if download_attachments and attachments:
        for img_match in re.findall(r'<ac:image[^>]*>(.*?)</ac:image>', xhtml, re.DOTALL):
            src_match = re.search(r'<ri:attachment ri:filename=\"([^\"]+)\"', img_match)
            if src_match:
                img_filename = src_match.group(1)
                img_safe_title = re.sub(r'[\\/:*?"<>|]', '-', img_filename).strip()
                if len(img_safe_title) > 120:
                    img_safe_title = img_safe_title[:120]
                img_file_name = f"{space}-{page_id}-{img_safe_title}"
                img_file_path = out_dir / img_file_name
                # Try to find the attachment in page attachments
                for att in attachments:
                    if att.get('title') == img_filename:
                        att_url = att.get('_links', {}).get('download')
                        if att_url:
                            try:
                                # Ensure /wiki is present before /download/attachments
                                if att_url.startswith('/download/'):
                                    wiki_base = base_url.rstrip('/') + '/wiki'
                                    full_url = wiki_base + att_url
                                else:
                                    full_url = base_url.rstrip('/') + att_url
                                if verbose:
                                    print(f"[DEBUG] DOWNLOAD IMAGE URL: {full_url}")
                                    print(f"[DEBUG] HEADERS: {redact_headers_for_debug(headers)}")
                                resp = requests.get(full_url, headers=headers, timeout=REQUEST_TIMEOUT)
                                resp.raise_for_status()
                                img_file_path.write_bytes(resp.content)
                                if verbose:
                                    print(f"Downloaded image: {img_file_path}")
                            except Exception as e:
                                print(f"Failed to download image {img_filename}: {e}")

    # Optional formatting for readability (preserve original for hashing/metrics)
    output_xhtml = xhtml
    if linebreak_mode and linebreak_mode.lower() == "tags":
        try:
            output_xhtml = _add_linebreaks_after_tags(output_xhtml)
        except Exception as _fmt_err:
            # Fail-safe: if formatting fails, fall back to original
            output_xhtml = xhtml

    # Source URL
    url = None
    links = page.get('_links') or page.get('links')
    if links:
        if 'webui' in links:
            url = base_url + links['webui']
        elif 'self' in links:
            url = links['self']

    # Retrieved timestamp
    retrieved = datetime.datetime.now().isoformat()
    # Format
    fmt = 'xhtml'
    # Content hash (MD5)
    content_hash = hashlib.md5(xhtml.encode('utf-8')).hexdigest() if xhtml else ''
    # Output hash (MD5) of the saved XHTML including readability line breaks
    output_hash = hashlib.md5(output_xhtml.encode('utf-8')).hexdigest() if output_xhtml else ''

    # Macro counts
    def macro_counts(content):
        import re
        structured_macro = len(re.findall(r'<ac:structured-macro', content))
        image = len(re.findall(r'<ac:image', content))
        link = len(re.findall(r'<ac:link', content))
        return structured_macro, image, link
    macro_structured_macro, macro_image, macro_link = macro_counts(xhtml)

    existing_meta: Dict[str, str] = {}
    if file_path.exists():
        try:
            existing_text = file_path.read_text(encoding="utf-8")
            if existing_text.startswith("---"):
                parts = existing_text.split("---", 2)
                if len(parts) >= 3:
                    for line in parts[1].strip().splitlines():
                        if ":" in line:
                            key, value = line.split(":", 1)
                            existing_meta[key.strip()] = value.strip()
        except Exception as parse_err:
            if verbose:
                print(f"[DEBUG] Failed to parse front matter for {file_path}: {parse_err}")

    if (
        existing_meta.get("output_hash") == output_hash
        and existing_meta.get("content_hash") == content_hash
        and existing_meta.get("version") == str(version)
    ):
        if verbose:
            print(f"No changes detected for {file_path}, skipping write.")
        return

    front_matter = (
        f"---\n"
        f"source: {url}\n"
        f"confluence_id: {page_id}\n"
        f"space: {space}\n"
        f"version: {version}\n"
        f"retrieved: {retrieved}\n"
        f"format: {fmt}\n"
        f"content_hash: {content_hash}\n"
        f"macro_structured_macro: {macro_structured_macro}\n"
        f"macro_image: {macro_image}\n"
        f"macro_link: {macro_link}\n"
        f"output_hash: {output_hash}\n"
        f"---\n"
    )
    file_path.write_text(front_matter + output_xhtml, encoding="utf-8")
    if verbose:
        print(f"Saved: {file_path} (Title: {title})")

def download_tree(base_url: str, root_id: str, headers: Dict[str, str], out_dir: Path, max_depth: int = 5, depth: int = 0, seen=None, download_attachments: bool = True, linebreak_mode: str = "none"):
    """
    Recursively download a Confluence page and its descendants up to max_depth.
    Saves each page and optionally its attachments/images.
    """
    if seen is None:
        seen = set()
    if root_id in seen or depth > max_depth:
        return
    seen.add(root_id)
    # Propagate verbose flag to all functions
    if hasattr(download_tree, 'verbose') and download_tree.verbose:
        get_page.verbose = True
        get_attachments.verbose = True
        get_children.verbose = True
    else:
        get_page.verbose = False
        get_attachments.verbose = False
        get_children.verbose = False
    page = get_page(base_url, root_id, headers)
    attachments = get_attachments(base_url, root_id, headers) if download_attachments else []
    save_page(page, out_dir, base_url, headers, verbose=download_tree.verbose if hasattr(download_tree, 'verbose') else False, attachments=attachments, download_attachments=download_attachments, linebreak_mode=linebreak_mode)
    for child in get_children(base_url, root_id, headers):
        download_tree(base_url, child["id"], headers, out_dir, max_depth, depth + 1, seen, download_attachments=download_attachments, linebreak_mode=linebreak_mode)



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
        # Case 1: ai-agile.json in this folder
        if (cur / "ai-agile.json").exists():
            return cur
        # Case 2: ai-agile/ai-agile.json beneath this folder
        if (cur / "ai-agile" / "ai-agile.json").exists():
            return cur / "ai-agile"
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def main():
    """
    Main entry point: auto-detects config locations so you can run from anywhere
    (including dev-instructions/scripts) without cd'ing manually. Arguments
    allow overrides but are optional.
    """
    cwd = Path.cwd()

    parser = argparse.ArgumentParser(add_help=True)
    # Accept legacy-style -OutDir while also supporting --out-dir
    parser.add_argument('-OutDir', '--out-dir', dest='out_dir', default=None, help='Output directory for downloaded pages')
    parser.add_argument('--config-dir', dest='config_dir', default=os.environ.get('CONFLUENCE_CONFIG_DIR'), help='Directory containing .env and confluence.config')
    parser.add_argument('--ai-agile-root', dest='ai_agile_root', default=os.environ.get('AI_AGILE_ROOT'), help='Path to ai-agile root containing ai-agile.json')
    parser.add_argument('--attachments', dest='attachments', action='store_true', help='Enable downloading attachments/images')
    parser.add_argument('--no-attachments', dest='attachments', action='store_false', help='Disable downloading attachments/images')
    parser.set_defaults(attachments=True)
    parser.add_argument('--verbose', action='store_true', help='Enable verbose debug output')
    parser.add_argument('--linebreaks', dest='linebreaks', choices=['none', 'tags'], default=os.environ.get('LINEBREAKS', 'none'), help='Insert line breaks after select closing tags for readability (default: none)')
    parser.add_argument('--timeout', type=float, default=DEFAULT_TIMEOUT, help='HTTP timeout (seconds) for Confluence requests (default: %(default)s)')
    # Ignore unknown args to be backward-friendly
    args, _unknown = parser.parse_known_args()

    # Determine confluence_dir (where .env and confluence.config live)
    confluence_dir: Optional[Path] = None

    # 1) If provided explicitly
    if args.config_dir:
        p = Path(args.config_dir)
        if (p / 'confluence.config').exists():
            confluence_dir = p
        else:
            raise RuntimeError(f"--config-dir '{p}' does not contain confluence.config")

    # 2) If current dir already looks like the config dir
    if confluence_dir is None and (cwd / 'confluence.config').exists():
        confluence_dir = cwd

    # 3) If AI_AGILE_ROOT provided or can be auto-found, use ai-agile.json to derive path
    ai_agile_root: Optional[Path] = None
    if confluence_dir is None:
        if args.ai_agile_root:
            ai_agile_root = Path(args.ai_agile_root)
        else:
            ai_agile_root = _find_ai_agile_root(cwd)

        if ai_agile_root is None:
            # As a last resort, try repo-root/ai-agile if present
            if (cwd / 'ai-agile' / 'ai-agile.json').exists():
                ai_agile_root = cwd / 'ai-agile'
            elif (cwd.parent / 'ai-agile' / 'ai-agile.json').exists():
                ai_agile_root = cwd.parent / 'ai-agile'

        if ai_agile_root is None:
            raise RuntimeError("Could not locate ai-agile root. Set AI_AGILE_ROOT or run from within the repository.")

        ai_agile_json_path = ai_agile_root / 'ai-agile.json'
        if not ai_agile_json_path.exists():
            raise RuntimeError(
                f"Expected ai-agile.json at {ai_agile_json_path}, but it was not found. "
                "Run dev-instructions/scripts/initialize.pl or create ai-agile/ai-agile.json manually."
            )

        ai_agile_cfg = load_ai_agile_json(ai_agile_json_path)
        confluence_rel = _get_confluence_rel_from_ai_agile_json(ai_agile_cfg)
        confluence_dir = ai_agile_root / confluence_rel

    # Validate confluence_dir
    if not (confluence_dir / 'confluence.config').exists():
        raise RuntimeError(f"Expected confluence.config in {confluence_dir}, but it was not found.")

    # Output directory default: confluence_dir (unless overridden)
    out_dir = Path(args.out_dir) if args.out_dir else confluence_dir

    # Load env/config
    env = load_env(confluence_dir / '.env')
    config = load_config(confluence_dir / 'confluence.config')
    base_url = config.get('BaseUrl') or env.get('BASE_URL')
    page_id = config.get('PageId')
    email = env.get('CONF_EMAIL')
    token = env.get('CONF_TOKEN')

    if not all([base_url, page_id, email, token]):
        raise RuntimeError("Missing credentials or config. Check .env and confluence.config in the confluence folder.")

    headers = get_auth_header(email, token)

    # Verbose control
    verbose = args.verbose or os.environ.get('VERBOSE', '0') == '1'
    download_tree.verbose = verbose

    # Attachments control (already set by argparse defaults and flags)
    download_attachments = args.attachments

    # Apply timeout configuration
    global REQUEST_TIMEOUT
    REQUEST_TIMEOUT = max(args.timeout, 0.1)

    # Run download
    download_tree(base_url.rstrip('/'), page_id, headers, out_dir, download_attachments=download_attachments, linebreak_mode=args.linebreaks)

if __name__ == "__main__":
        main()
