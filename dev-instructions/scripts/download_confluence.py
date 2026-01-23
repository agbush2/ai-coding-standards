import os
import requests
from pathlib import Path
from typing import Dict, Any
import sys

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
        print(f"[DEBUG] HEADERS: {headers}")
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def get_attachments(base_url: str, page_id: str, headers: Dict[str, str]) -> list:
    """
    Fetch all attachments for a Confluence page by ID.
    Returns a list of attachment JSON objects.
    """
    url = f"{base_url}/wiki/rest/api/content/{page_id}/child/attachment?limit=100"
    if hasattr(get_attachments, 'verbose') and get_attachments.verbose:
        print(f"[DEBUG] GET ATTACHMENTS URL: {url}")
        print(f"[DEBUG] HEADERS: {headers}")
    resp = requests.get(url, headers=headers)
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
        print(f"[DEBUG] HEADERS: {headers}")
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("results", [])


def save_page(page: Dict[str, Any], out_dir: Path, base_url: str, headers: Dict[str, str], verbose: bool = False, attachments: list = None, download_attachments: bool = True):
    """
    Save a Confluence page as an .xhtml file with front-matter metadata.
    Optionally download attachments and images to the output directory.
    """
    import re, hashlib, datetime
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
        # Use credentials passed to save_page, not from environment
        # Find email/token from headers
        auth_header = headers if 'Authorization' in headers else None
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
                        print(f"[DEBUG] HEADERS: {headers}")
                    resp = requests.get(full_url, headers=headers)
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
                                    print(f"[DEBUG] HEADERS: {headers}")
                                resp = requests.get(full_url, headers=headers)
                                resp.raise_for_status()
                                img_file_path.write_bytes(resp.content)
                                if verbose:
                                    print(f"Downloaded image: {img_file_path}")
                            except Exception as e:
                                print(f"Failed to download image {img_filename}: {e}")

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

    # Macro counts
    def macro_counts(content):
        import re
        structured_macro = len(re.findall(r'<ac:structured-macro', content))
        image = len(re.findall(r'<ac:image', content))
        link = len(re.findall(r'<ac:link', content))
        return structured_macro, image, link
    macro_structured_macro, macro_image, macro_link = macro_counts(xhtml)

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
        f"---\n"
    )
    file_path.write_text(front_matter + xhtml, encoding="utf-8")
    if verbose:
        print(f"Saved: {file_path} (Title: {title})")

def download_tree(base_url: str, root_id: str, headers: Dict[str, str], out_dir: Path, max_depth: int = 5, depth: int = 0, seen=None, download_attachments: bool = True):
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
    save_page(page, out_dir, base_url, headers, verbose=download_tree.verbose if hasattr(download_tree, 'verbose') else False, attachments=attachments, download_attachments=download_attachments)
    for child in get_children(base_url, root_id, headers):
        download_tree(base_url, child["id"], headers, out_dir, max_depth, depth + 1, seen, download_attachments=download_attachments)



def load_ai_agile_config(config_path: Path) -> Dict[str, str]:
    """
    Load configuration from ai-agile.config file.
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

def main():
    """
    Main entry point: loads config, parses arguments, and starts download.
    """
    cwd = Path.cwd()
    # Find ai-agile root (walk up until ai-agile.config is found)
    ai_agile_root = cwd
    for _ in range(5):
        if (ai_agile_root / "ai-agile.config").exists():
            break
        if ai_agile_root.parent == ai_agile_root:
            break
        ai_agile_root = ai_agile_root.parent
    ai_agile_config = load_ai_agile_config(ai_agile_root / "ai-agile.config")

    # Get all relevant folders from ai-agile.config
    source_material_path = ai_agile_config.get("SOURCE_MATERIAL_PATH", "01_source-material")
    generated_material_path = ai_agile_config.get("GENERATED_MATERIAL_PATH", "02_generated_materials")
    requirements_path = ai_agile_config.get("REQUIREMENTS_PATH", "03_requirements")
    specifications_path = ai_agile_config.get("SPECIFICATIONS_PATH", "04_specifications")

    # Use the source material path as the default working directory for confluence sync
    confluence_dir = ai_agile_root / source_material_path / "confluence"
    out_dir = confluence_dir

    env = load_env(confluence_dir / ".env")
    config = load_config(confluence_dir / "confluence.config")
    base_url = config.get("BaseUrl") or env.get("BASE_URL")
    page_id = config.get("PageId")
    email = env.get("CONF_EMAIL")
    token = env.get("CONF_TOKEN")

    if not all([base_url, page_id, email, token]):
        raise RuntimeError("Missing credentials or config. Check .env and confluence.config in the source material confluence folder.")

    headers = get_auth_header(email, token)
    # Enable verbose output if requested via environment or argument
    verbose = '--verbose' in sys.argv or os.environ.get('VERBOSE', '0') == '1'
    download_tree.verbose = verbose

    # Parse --attachments option (default True)
    download_attachments = True
    for arg in sys.argv:
        if arg.startswith('--attachments='):
            val = arg.split('=', 1)[1].strip().lower()
            if val in ('0', 'false', 'no', 'off'):
                download_attachments = False
            elif val in ('1', 'true', 'yes', 'on'):
                download_attachments = True
    if '--no-attachments' in sys.argv:
        download_attachments = False
    if '--attachments' in sys.argv:
        download_attachments = True

    download_tree(base_url.rstrip("/"), page_id, headers, out_dir, download_attachments=download_attachments)

if __name__ == "__main__":
        main()
