"""
confluence2md.py
Converts all .xhtml files in the confluence folder to Markdown (.md) files in the generated-materials folder.
"""

import os
from pathlib import Path
from bs4 import BeautifulSoup, Tag

def load_config(config_path):
    config = {}
    if Path(config_path).exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    config[k.strip()] = v.strip()
    return config


CONFIG_PATH = Path(__file__).parent.parent.parent / 'ai-agile' / 'ai-agile.config'
config = load_config(CONFIG_PATH)

SOURCE_DIR = config.get('SOURCE_MATERIAL_PATH', 'source-material/confluence')
DEST_DIR = config.get('GENERATED_MATERIAL_PATH', 'source-material/generated-materials')

# Assume both are relative to ai-agile folder
AI_AGILE_BASE = Path(__file__).parent.parent.parent / 'ai-agile'
CONFLUENCE_DIR = AI_AGILE_BASE / SOURCE_DIR
OUTPUT_DIR = AI_AGILE_BASE / DEST_DIR

print(f"[DEBUG] CONFIG_PATH: {CONFIG_PATH}")
print(f"[DEBUG] SOURCE_DIR: {SOURCE_DIR}")
print(f"[DEBUG] DEST_DIR: {DEST_DIR}")
print(f"[DEBUG] AI_AGILE_BASE: {AI_AGILE_BASE}")
print(f"[DEBUG] CONFLUENCE_DIR (absolute): {CONFLUENCE_DIR.resolve()}")
print(f"[DEBUG] OUTPUT_DIR (absolute): {OUTPUT_DIR.resolve()}")

if not CONFLUENCE_DIR.exists():
    print(f"[ERROR] Source directory does not exist: {CONFLUENCE_DIR.resolve()}")
    exit(1)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

found = False

# Recursively search for .xhtml files in all subfolders
found = False


def print_tree(path, prefix=""):
    if path.is_dir():
        print(f"{prefix}[DIR] {path}")
        for child in sorted(path.iterdir()):
            print_tree(child, prefix + "  ")
    else:
        print(f"{prefix}{path}")

def xhtml_to_markdown(soup: BeautifulSoup) -> str:
    """
    Convert a BeautifulSoup XHTML soup to Markdown, handling headings, bold, italics, lists, links, images, code, blockquotes, and paragraphs.
    """
    lines = []

    def handle_tag(tag: Tag, depth=0):
        # Handle Confluence layout and macro wrappers by recursing into their children
        layout_tags = [
            'ac:layout', 'ac:layout-section', 'ac:layout-cell',
            'ac:rich-text-body', 'ac:body', 'ac:plain-text-body',
        ]
        if tag.name in layout_tags:
            for child in tag.children:
                if isinstance(child, Tag):
                    handle_tag(child, depth+1)
            return

        # Handle Confluence macros
        if tag.name == 'ac:structured-macro':
            macro_name = tag.get('ac:name', '').lower()
            if macro_name == 'info':
                # Info macro as blockquote
                info_body = tag.find(['ac:rich-text-body', 'ac:plain-text-body'])
                if info_body:
                    info_lines = []
                    for child in info_body.children:
                        if isinstance(child, Tag):
                            sublines = []
                            handle_tag_collect(child, sublines, depth+1)
                            info_lines.extend(sublines)
                        elif str(child).strip():
                            info_lines.append(str(child).strip())
                    for line in info_lines:
                        lines.append(f"> {line.strip()}")
                    lines.append('')
                return
            elif macro_name == 'code':
                # Code macro as fenced code block
                code_body = tag.find('ac:plain-text-body')
                if code_body:
                    code = code_body.get_text("\n", strip=False)
                    lines.append(f"```\n{code}\n```")
                    lines.append('')
                return
            elif macro_name == 'drawio':
                # Drawio macro as image placeholder
                lines.append('![Diagram: drawio diagram not rendered](#)')
                lines.append('')
                return
            elif macro_name == 'mermaid-cloud':
                # Mermaid macro as fenced mermaid code block
                filename = tag.get('ac:parameter', '')
                lines.append('```mermaid')
                lines.append('%% Mermaid diagram placeholder')
                lines.append('```')
                lines.append('')
                return
            elif macro_name == 'toc':
                # Table of contents macro as placeholder
                lines.append('[TOC]')
                lines.append('')
                return
            # Unknown macro: recurse into children
            for child in tag.children:
                if isinstance(child, Tag):
                    handle_tag(child, depth+1)
            return

        # Standard HTML tags
        if tag.name in [f'h{i}' for i in range(1, 7)]:
            level = int(tag.name[1])
            lines.append(f"{'#' * level} {tag.get_text(strip=True)}\n")
        elif tag.name == 'p':
            text = ''.join(handle_inline(child) if isinstance(child, Tag) else str(child) for child in tag.children)
            if text.strip():
                lines.append(text.strip() + '\n')
        elif tag.name == 'ul':
            for li in tag.find_all('li', recursive=False):
                li_text = ''.join(handle_inline(child) if isinstance(child, Tag) else str(child) for child in li.children)
                lines.append(f"- {li_text.strip()}")
            lines.append('')
        elif tag.name == 'ol':
            idx = 1
            for li in tag.find_all('li', recursive=False):
                li_text = ''.join(handle_inline(child) if isinstance(child, Tag) else str(child) for child in li.children)
                lines.append(f"{idx}. {li_text.strip()}")
                idx += 1
            lines.append('')
        elif tag.name == 'table':
            rows = tag.find_all('tr')
            for i, row in enumerate(rows):
                cols = [col.get_text(strip=True) for col in row.find_all(['td', 'th'])]
                lines.append(' | '.join(cols))
                if i == 0:
                    lines.append(' | '.join(['---'] * len(cols)))
            lines.append('')
        elif tag.name == 'blockquote':
            quote = tag.get_text("\n", strip=True)
            for line in quote.splitlines():
                lines.append(f"> {line}")
            lines.append('')
        elif tag.name == 'pre':
            code = tag.get_text("\n", strip=False)
            lines.append(f"```\n{code}\n```")
            lines.append('')
        else:
            for child in tag.children:
                if isinstance(child, Tag):
                    handle_tag(child, depth+1)

    # Helper for collecting lines in macros
    def handle_tag_collect(tag: Tag, out_lines, depth=0):
        # Like handle_tag, but appends to out_lines instead of global lines
        layout_tags = [
            'ac:layout', 'ac:layout-section', 'ac:layout-cell',
            'ac:rich-text-body', 'ac:body', 'ac:plain-text-body',
        ]
        if tag.name in layout_tags:
            for child in tag.children:
                if isinstance(child, Tag):
                    handle_tag_collect(child, out_lines, depth+1)
            return
        if tag.name == 'p':
            text = ''.join(handle_inline(child) if isinstance(child, Tag) else str(child) for child in tag.children)
            if text.strip():
                out_lines.append(text.strip())
        elif tag.name in [f'h{i}' for i in range(1, 7)]:
            level = int(tag.name[1])
            out_lines.append(f"{'#' * level} {tag.get_text(strip=True)}")
        else:
            for child in tag.children:
                if isinstance(child, Tag):
                    handle_tag_collect(child, out_lines, depth+1)

    def handle_inline(tag: Tag) -> str:
        if tag.name in ['strong', 'b']:
            return f"**{tag.get_text(strip=True)}**"
        elif tag.name in ['em', 'i']:
            return f"*{tag.get_text(strip=True)}*"
        elif tag.name == 'code':
            return f"`{tag.get_text(strip=True)}`"
        elif tag.name == 'a':
            href = tag.get('href', '')
            text = tag.get_text(strip=True)
            return f"[{text}]({href})"
        elif tag.name == 'img':
            src = tag.get('src', '')
            alt = tag.get('alt', '')
            return f"![{alt}]({src})"
        else:
            return tag.get_text(strip=True)

    # Start from <body> if present, else from root
    body = soup.find('body')
    if body:
        for child in body.children:
            if isinstance(child, Tag):
                handle_tag(child)
    else:
        # fallback: process all top-level tags
        for child in soup.children:
            if isinstance(child, Tag):
                handle_tag(child)
    return '\n'.join(line for line in lines if line.strip())

print(f"Scanning for .xhtml files in {CONFLUENCE_DIR} and subfolders:")
print_tree(CONFLUENCE_DIR)

found = False
for xhtml_file in CONFLUENCE_DIR.rglob("*.xhtml"):
    print(f"Found: {xhtml_file}")
    found = True
    with xhtml_file.open("r", encoding="utf-8") as f:
        xhtml_content = f.read()
    soup = BeautifulSoup(xhtml_content, "lxml")
    # Convert to Markdown
    markdown = xhtml_to_markdown(soup)
    md_file = OUTPUT_DIR / (xhtml_file.stem + ".md")
    with md_file.open("w", encoding="utf-8") as out:
        out.write(markdown)
    print(f"Converted {xhtml_file.relative_to(CONFLUENCE_DIR)} -> {md_file.name}")
if not found:
    print(f"No .xhtml files found in {CONFLUENCE_DIR} or its subfolders.")
