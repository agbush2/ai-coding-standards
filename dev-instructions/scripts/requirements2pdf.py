#!/usr/bin/env python
"""requirements2pdf

Create a single, formatted PDF from per-document canonical requirements JSON files.

- Reads locations from ai-agile/ai-agile.json (process.steps.* by name).
- Defaults:
  - Input dir: <ai-agile-root>/<GeneratedMaterials.folder>/canonical-requirements
  - Output:   <ai-agile-root>/<GeneratedMaterials.folder>/canonical-requirements.pdf
  - --include-references: false

This script intentionally treats SourceMaterial as read-only evidence.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StepFolders:
    ai_agile_root: Path
    source_material: Path
    generated_materials: Path


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_folders(repo_root: Path) -> StepFolders:
    ai_agile_json = repo_root / "ai-agile" / "ai-agile.json"
    if not ai_agile_json.exists():
        raise FileNotFoundError(f"Missing config file: {ai_agile_json}")

    cfg = _load_json(ai_agile_json)

    # Prefer basePaths.aiAgileRoot when present, otherwise derive from repoRoot.
    base_paths = cfg.get("basePaths", {})
    ai_agile_root_raw = base_paths.get("aiAgileRoot")
    ai_agile_root = Path(ai_agile_root_raw) if ai_agile_root_raw else (repo_root / "ai-agile")

    process = cfg.get("process", {})
    steps = process.get("steps", {})

    def step_folder(step_name: str) -> Path:
        step = steps.get(step_name)
        if not isinstance(step, dict) or "folder" not in step:
            raise KeyError(f"Could not resolve process.steps.{step_name}.folder from {ai_agile_json}")
        return ai_agile_root / str(step["folder"])

    return StepFolders(
        ai_agile_root=ai_agile_root,
        source_material=step_folder("SourceMaterial"),
        generated_materials=step_folder("GeneratedMaterials"),
    )


def iter_requirement_files(input_dir: Path, glob_pattern: str) -> list[Path]:
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    files = sorted(p for p in input_dir.glob(glob_pattern) if p.is_file())
    if not files:
        raise FileNotFoundError(f"No files matched {glob_pattern!r} in {input_dir}")
    return files


def _safe_get(dct: dict[str, Any], path: list[str], default: Any = None) -> Any:
    cur: Any = dct
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _escape_for_paragraph(text: str) -> str:
    # ReportLab Paragraph uses a minimal XML-ish markup.
    # Escape &, <, > to avoid rendering errors.
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _doc_title_from_json(doc: dict[str, Any], fallback: str) -> str:
    title = _safe_get(doc, ["sourceDocument", "title"], None)
    if isinstance(title, str) and title.strip():
        return title.strip()

    # Try to use relativePath basename.
    rel = _safe_get(doc, ["sourceDocument", "relativePath"], None)
    if isinstance(rel, str) and rel.strip():
        return Path(rel).name

    return fallback


def _format_source_metadata(doc: dict[str, Any]) -> str:
    parts: list[str] = []
    source_type = _safe_get(doc, ["sourceDocument", "sourceType"], None)
    if isinstance(source_type, str) and source_type:
        parts.append(f"Source type: {source_type}")

    rel = _safe_get(doc, ["sourceDocument", "relativePath"], None)
    if isinstance(rel, str) and rel:
        parts.append(f"Source: {rel}")

    conf = _safe_get(doc, ["sourceDocument", "confluence"], None)
    if isinstance(conf, dict):
        page_id = conf.get("pageId")
        space = conf.get("space")
        version = conf.get("version")
        url = conf.get("url")
        if page_id:
            parts.append(f"Confluence pageId: {page_id}")
        if space:
            parts.append(f"Confluence space: {space}")
        if version is not None:
            parts.append(f"Confluence version: {version}")
        if url:
            parts.append(f"Confluence URL: {url}")

    retrieved = _safe_get(doc, ["sourceDocument", "retrievedAt"], None)
    if isinstance(retrieved, str) and retrieved:
        parts.append(f"Retrieved at: {retrieved}")

    return "\n".join(parts)


def _group_requirements(requirements: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {
        "Business": [],
        "Functional": [],
        "Architecture": [],
        "NonFunctional": [],
        "Other": [],
    }

    for req in requirements:
        primary = _safe_get(req, ["classification", "primary"], "Other")
        if primary not in groups:
            primary = "Other"
        groups[primary].append(req)

    # Drop empty groups (except keep order stable in rendering)
    return groups


def _default_brd_sections_path() -> Path:
    return Path(__file__).resolve().parent / "brd_sections.json"


def _load_brd_sections(path: Path) -> dict[str, Any]:
    data = _load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid brd_sections.json (expected object): {path}")
    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        raise ValueError(f"Invalid brd_sections.json (missing sections[]): {path}")
    return data


def _get_by_dotted_path(obj: Any, dotted: str) -> Any:
    """Get a value from a dict using dotted paths like 'requirement.kind'.

    Only supports dict traversal. If a non-dict is encountered mid-path, returns None.
    """

    if not isinstance(dotted, str) or not dotted.strip():
        return None

    path = dotted.strip()
    if path.startswith("requirement."):
        path = path[len("requirement.") :]
    elif path == "requirement":
        return obj

    cur: Any = obj
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _eval_op(value: Any, op: str, expected: Any) -> bool:
    if op == "exists":
        exists = value is not None
        return exists is bool(expected) if isinstance(expected, bool) else exists

    if op == "eq":
        return value == expected

    if op == "in":
        return isinstance(expected, list) and value in expected

    if op == "contains":
        if isinstance(value, list):
            return expected in value
        if isinstance(value, str) and isinstance(expected, str):
            return expected in value
        return False

    if op == "containsText":
        if isinstance(expected, str):
            needle = expected.lower()
        else:
            return False

        if isinstance(value, str):
            return needle in value.lower()
        if isinstance(value, list):
            return any(isinstance(v, str) and needle in v.lower() for v in value)
        return False

    return False


def _eval_match_expr(requirement: dict[str, Any], expr: Any) -> bool:
    """Evaluate a brd_sections.json match expression against a requirement."""

    if not isinstance(expr, dict):
        return False

    if "any" in expr:
        items = expr.get("any")
        return isinstance(items, list) and any(_eval_match_expr(requirement, it) for it in items)

    if "all" in expr:
        items = expr.get("all")
        return isinstance(items, list) and all(_eval_match_expr(requirement, it) for it in items)

    field = expr.get("field")
    op = expr.get("op")
    expected = expr.get("value")
    if not isinstance(field, str) or not isinstance(op, str):
        return False

    value = _get_by_dotted_path(requirement, field)
    return _eval_op(value, op, expected)


def _assign_brd_section_id(
    requirement: dict[str, Any],
    *,
    sections: list[dict[str, Any]],
    assignment_policy: dict[str, Any],
) -> str:
    first_match_wins = bool(assignment_policy.get("firstMatchWins", True))
    unassigned_id = assignment_policy.get("unassignedSectionId")
    unassigned = unassigned_id if isinstance(unassigned_id, str) and unassigned_id else "BRD-99"

    matched: list[str] = []
    for section in sections:
        sid = section.get("id")
        if not isinstance(sid, str) or not sid:
            continue

        match_rules = section.get("match")
        if not isinstance(match_rules, list) or not match_rules:
            continue

        # Treat match list as OR across rule blocks.
        if any(_eval_match_expr(requirement, rule) for rule in match_rules):
            matched.append(sid)
            if first_match_wins:
                return sid

    return matched[0] if matched else unassigned


def _coerce_brd_section_id(
    section_id: Any,
    *,
    valid_ids: set[str],
    unassigned_id: str,
) -> str:
    if isinstance(section_id, str) and section_id in valid_ids:
        return section_id
    return unassigned_id


def _escape_join(lines: list[str]) -> str:
    return _escape_for_paragraph("\n".join(lines)).replace("\n", "<br/>")


def _format_story_summary(story: Any) -> str:
    if not isinstance(story, dict):
        return "—"
    as_a = story.get("asA")
    i_want = story.get("iWant")
    so_that = story.get("soThat")
    lines: list[str] = []
    if isinstance(as_a, str) and as_a.strip():
        lines.append(f"As a: {as_a.strip()}")
    if isinstance(i_want, str) and i_want.strip():
        lines.append(f"I want: {i_want.strip()}")
    if isinstance(so_that, str) and so_that.strip():
        lines.append(f"So that: {so_that.strip()}")
    return "\n".join(lines) if lines else "—"


def _format_bdd_summary(bdd: Any) -> str:
    if not isinstance(bdd, dict):
        return "—"
    feature = bdd.get("feature")
    scenario = bdd.get("scenario")
    steps = bdd.get("steps")

    lines: list[str] = []
    if isinstance(feature, str) and feature.strip():
        lines.append(f"Feature: {feature.strip()}")
    if isinstance(scenario, str) and scenario.strip():
        lines.append(f"Scenario: {scenario.strip()}")

    if isinstance(steps, list) and steps:
        step_lines: list[str] = []
        for step in steps:
            if not isinstance(step, dict):
                continue
            kw = step.get("keyword")
            txt = step.get("text")
            if isinstance(kw, str) and kw.strip() and isinstance(txt, str) and txt.strip():
                step_lines.append(f"{kw.strip()} {txt.strip()}")
        if step_lines:
            lines.append("Steps:")
            lines.extend(step_lines)

    return "\n".join(lines) if lines else "—"


def build_pdf(
    requirement_files: list[Path],
    output_pdf: Path,
    include_references: bool,
    include_open_questions: bool,
    title: str,
    brd_sections_path: Path | None,
) -> None:
    try:
        from reportlab.lib.pagesizes import LETTER
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            PageBreak,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ModuleNotFoundError as e:
        raise SystemExit(
            "Missing dependency 'reportlab'. Install it with: pip install reportlab"
        ) from e

    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=LETTER,
        leftMargin=0.8 * inch,
        rightMargin=0.8 * inch,
        topMargin=0.8 * inch,
        bottomMargin=0.8 * inch,
        title=title,
        author="requirements2pdf",
    )

    styles = getSampleStyleSheet()
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    h3 = styles["Heading3"]
    body = styles["BodyText"]

    small = ParagraphStyle(
        name="Small",
        parent=body,
        fontSize=9,
        leading=11,
        spaceBefore=4,
        spaceAfter=6,
    )

    req_header = ParagraphStyle(
        name="ReqHeader",
        parent=h3,
        spaceBefore=10,
        spaceAfter=4,
    )

    story_style = ParagraphStyle(
        name="Story",
        parent=small,
        leftIndent=14,
        spaceBefore=2,
        spaceAfter=6,
    )

    story_kw = ParagraphStyle(
        name="StoryKW",
        parent=small,
        leftIndent=28,
        spaceBefore=1,
        spaceAfter=2,
    )

    mini_label = ParagraphStyle(
        name="MiniLabel",
        parent=small,
        fontSize=8,
        leading=10,
        spaceBefore=0,
        spaceAfter=0,
    )

    mini_value = ParagraphStyle(
        name="MiniValue",
        parent=small,
        fontSize=8,
        leading=10,
        spaceBefore=0,
        spaceAfter=0,
    )

    elements: list[Any] = []

    # Title page
    elements.append(Paragraph(_escape_for_paragraph(title), h1))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(
        Paragraph(
            _escape_for_paragraph(
                f"Generated: {datetime.now().isoformat(timespec='seconds')}"
            ),
            small,
        )
    )
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(
        Paragraph(
            _escape_for_paragraph(
                "This PDF is generated from canonical requirements JSON files. "
                "Statements are rendered as the primary source-of-truth summary for downstream analysis."
            ),
            small,
        )
    )
    elements.append(PageBreak())

    brd_cfg_path = brd_sections_path if brd_sections_path else _default_brd_sections_path()
    brd_cfg = _load_brd_sections(brd_cfg_path)
    sections_raw = brd_cfg.get("sections")
    sections: list[dict[str, Any]] = [s for s in sections_raw if isinstance(s, dict)] if isinstance(sections_raw, list) else []
    valid_section_ids = {str(s.get("id")) for s in sections if isinstance(s.get("id"), str)}
    unassigned_id = _safe_get(brd_cfg, ["assignmentPolicy", "unassignedSectionId"], "BRD-99")
    if not isinstance(unassigned_id, str) or unassigned_id not in valid_section_ids:
        unassigned_id = "BRD-99" if "BRD-99" in valid_section_ids else (next(iter(valid_section_ids)) if valid_section_ids else "BRD-99")

    assignment_policy = brd_cfg.get("assignmentPolicy") if isinstance(brd_cfg.get("assignmentPolicy"), dict) else {}

    # Collect doc metadata by sourceDocument.relativePath to support bibliography.
    doc_info_by_rel: dict[str, dict[str, Any]] = {}

    # Index: sectionId -> kind -> list[{req, docRel}]
    section_index: dict[str, dict[str, list[dict[str, Any]]]] = {sid: {} for sid in valid_section_ids}
    open_questions_by_doc: list[tuple[str, str, list[str]]] = []

    for path in requirement_files:
        data = _load_json(path)
        doc_title = _doc_title_from_json(data, fallback=path.name)
        doc_rel = _safe_get(data, ["sourceDocument", "relativePath"], None)
        doc_key = str(doc_rel).strip() if isinstance(doc_rel, str) and doc_rel.strip() else path.name

        confluence = _safe_get(data, ["sourceDocument", "confluence"], None)
        url = confluence.get("url") if isinstance(confluence, dict) else None

        doc_info_by_rel.setdefault(
            doc_key,
            {
                "title": doc_title,
                "relativePath": doc_key,
                "url": url,
            },
        )

        if include_open_questions:
            oq = data.get("openQuestions")
            if isinstance(oq, list):
                qs = [q.strip() for q in oq if isinstance(q, str) and q.strip()]
                if qs:
                    open_questions_by_doc.append((doc_key, doc_title, qs))

        reqs_raw = _as_list(data.get("requirements"))
        reqs: list[dict[str, Any]] = [r for r in reqs_raw if isinstance(r, dict)]
        for req in reqs:
            computed_sid = _assign_brd_section_id(
                req,
                sections=sections,
                assignment_policy=assignment_policy,
            )
            sid = _coerce_brd_section_id(
                computed_sid,
                valid_ids=valid_section_ids,
                unassigned_id=unassigned_id,
            )

            kind = req.get("kind")
            kind_key = str(kind).strip() if isinstance(kind, str) and kind.strip() else "Other"
            section_index.setdefault(sid, {}).setdefault(kind_key, []).append({"req": req, "docRel": doc_key})

    def _section_render_hints(section: dict[str, Any]) -> tuple[bool, bool]:
        hints = section.get("renderingHints")
        include_refs = True
        include_quotes = True
        if isinstance(hints, dict):
            if hints.get("includeReferences") is False:
                include_refs = False
            if hints.get("includeQuotes") is False:
                include_quotes = False
        return include_refs, include_quotes

    def _render_story_bdd_minitable(req: dict[str, Any]) -> Table:
        story_text = _format_story_summary(req.get("story"))
        bdd_text = _format_bdd_summary(req.get("bdd"))

        story_cell = Paragraph(
            _escape_join(story_text.splitlines()) if story_text != "—" else _escape_for_paragraph("—"),
            mini_value,
        )
        bdd_cell = Paragraph(
            _escape_join(bdd_text.splitlines()) if bdd_text != "—" else _escape_for_paragraph("—"),
            mini_value,
        )

        table_data = [
            [
                Paragraph(_escape_for_paragraph("Story"), mini_label),
                Paragraph(_escape_for_paragraph("BDD"), mini_label),
            ],
            [story_cell, bdd_cell],
        ]

        tbl = Table(
            table_data,
            colWidths=[3.35 * inch, 3.35 * inch],
        )
        tbl.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        return tbl

    # Build bibliography registry upfront for stable numbering.
    all_source_relpaths: set[str] = set()
    for sec_groups in section_index.values():
        for req_items in sec_groups.values():
            for item in req_items:
                req = item.get("req")
                doc_rel = item.get("docRel")
                if isinstance(req, dict):
                    refs = req.get("references")
                    if isinstance(refs, list):
                        for ref in refs:
                            if isinstance(ref, dict) and isinstance(ref.get("relativePath"), str) and ref.get("relativePath").strip():
                                all_source_relpaths.add(ref.get("relativePath").strip())
                    if isinstance(doc_rel, str) and doc_rel.strip():
                        all_source_relpaths.add(doc_rel.strip())

    bibliography_relpaths = sorted(all_source_relpaths)
    citation_number_by_rel = {rel: idx for idx, rel in enumerate(bibliography_relpaths, start=1)}

    def _format_citations(req: dict[str, Any], doc_rel: str | None) -> str:
        rels: list[str] = []
        refs = req.get("references")
        if isinstance(refs, list):
            for ref in refs:
                if not isinstance(ref, dict):
                    continue
                rel = ref.get("relativePath")
                if isinstance(rel, str) and rel.strip() and rel.strip() not in rels:
                    rels.append(rel.strip())
        if isinstance(doc_rel, str) and doc_rel.strip() and doc_rel.strip() not in rels:
            rels.append(doc_rel.strip())

        nums = [citation_number_by_rel.get(r) for r in rels]
        nums = [n for n in nums if isinstance(n, int)]
        return "".join(f"[{n}]" for n in sorted(set(nums)))

    # Render sections in the order defined by brd_sections.json
    for section in sections:
        sid = section.get("id")
        if not isinstance(sid, str) or sid not in valid_section_ids:
            continue

        sec_number = section.get("number")
        sec_title = section.get("title")
        sec_heading = f"{sec_number}. {sec_title}" if sec_number and sec_title else (sec_title or sid)
        elements.append(Paragraph(_escape_for_paragraph(str(sec_heading)), h1))

        purpose = section.get("purpose")
        if isinstance(purpose, str) and purpose.strip():
            elements.append(Paragraph(_escape_for_paragraph(purpose.strip()), small))
            elements.append(Spacer(1, 0.08 * inch))

        # Note: we always cite sources via [n] markers + bibliography.
        # includeReferences/includeQuotes hints only apply to any extra evidence blocks.

        kind_groups = section_index.get(sid, {})
        if not kind_groups:
            elements.append(Paragraph(_escape_for_paragraph("(No items)"), small))
            elements.append(PageBreak())
            continue

        # Flatten all requirement items under the BRD section.
        all_items: list[dict[str, Any]] = []
        for req_items in kind_groups.values():
            if isinstance(req_items, list):
                all_items.extend([it for it in req_items if isinstance(it, dict)])

        all_items.sort(key=lambda it: str(_safe_get(it.get("req") if isinstance(it, dict) else {}, ["id"], "")))

        for item in all_items:
                if not isinstance(item, dict):
                    continue
                req = item.get("req")
                doc_rel = item.get("docRel")
                if not isinstance(req, dict):
                    continue

                req_id = req.get("id", "")
                title_text = req.get("title")

                if isinstance(title_text, str) and title_text.strip():
                    elements.append(Paragraph(_escape_for_paragraph(title_text.strip()), req_header))

                statement = req.get("statement")
                if isinstance(statement, str) and statement.strip():
                    citations = _format_citations(req, doc_rel if isinstance(doc_rel, str) else None)
                    tag = f" [{str(req_id).strip()}]" if isinstance(req_id, str) and req_id.strip() else ""
                    text = statement.strip() + tag + (f" {citations}" if citations else "")
                    elements.append(Paragraph(_escape_for_paragraph(text), body))
                else:
                    # Fall back to story/bdd if statement missing
                    story = req.get("story")
                    bdd = req.get("bdd")
                    if isinstance(story, dict):
                        as_a = story.get("asA")
                        i_want = story.get("iWant")
                        so_that = story.get("soThat")
                        parts = []
                        if as_a and i_want:
                            parts.append(f"As {as_a}, I want {i_want}.")
                        if so_that:
                            parts.append(f"So that {so_that}.")
                        if parts:
                            citations = _format_citations(req, doc_rel if isinstance(doc_rel, str) else None)
                            tag = f" [{str(req_id).strip()}]" if isinstance(req_id, str) and req_id.strip() else ""
                            text = " ".join(parts) + tag + (f" {citations}" if citations else "")
                            elements.append(Paragraph(_escape_for_paragraph(text), body))
                    if isinstance(bdd, dict):
                        feature = bdd.get("feature")
                        scenario = bdd.get("scenario")
                        if feature:
                            elements.append(Paragraph(_escape_for_paragraph(f"Feature: {feature}"), small))
                        if scenario:
                            elements.append(Paragraph(_escape_for_paragraph(f"Scenario: {scenario}"), small))

                # Mini table summary (smaller font) after each requirement.
                elements.append(Spacer(1, 0.04 * inch))
                elements.append(_render_story_bdd_minitable(req))
                elements.append(Spacer(1, 0.08 * inch))

                elements.append(Spacer(1, 0.08 * inch))

        elements.append(PageBreak())

    if include_open_questions and open_questions_by_doc:
        elements.append(Paragraph(_escape_for_paragraph("Open questions (by source document)"), h1))
        elements.append(Spacer(1, 0.1 * inch))
        for _, doc_title, qs in sorted(open_questions_by_doc, key=lambda x: x[0]):
            elements.append(Paragraph(_escape_for_paragraph(str(doc_title)), h2))
            for q in qs:
                elements.append(Paragraph(_escape_for_paragraph("• " + q), body))
            elements.append(Spacer(1, 0.12 * inch))

    # Bibliography
    elements.append(PageBreak())
    elements.append(Paragraph(_escape_for_paragraph("Bibliography"), h1))
    elements.append(Spacer(1, 0.1 * inch))
    for rel in bibliography_relpaths:
        num = citation_number_by_rel.get(rel)
        info = doc_info_by_rel.get(rel, {})
        title_txt = info.get("title") if isinstance(info, dict) else None
        url_txt = info.get("url") if isinstance(info, dict) else None

        bits: list[str] = []
        if isinstance(title_txt, str) and title_txt.strip():
            bits.append(title_txt.strip())
        bits.append(rel)
        if isinstance(url_txt, str) and url_txt.strip():
            bits.append(url_txt.strip())

        line = f"[{num}] " + " — ".join(bits)
        elements.append(Paragraph(_escape_for_paragraph(line), small))

    doc.build(elements)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a single PDF from canonical requirements JSON files.",
    )

    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[2]),
        help="Repository root (default: inferred from this script location)",
    )

    parser.add_argument(
        "--input-dir",
        default=None,
        help=(
            "Directory containing canonical requirements JSON files. "
            "Default: <ai-agile-root>/<GeneratedMaterials.folder>/canonical-requirements"
        ),
    )

    parser.add_argument(
        "--glob",
        default="*.requirements.json",
        help="Glob pattern to match input files (default: *.requirements.json)",
    )

    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Output PDF path. Default: <ai-agile-root>/<GeneratedMaterials.folder>/canonical-requirements.pdf"
        ),
    )

    parser.add_argument(
        "--title",
        default="Canonical Requirements",
        help="PDF title (default: Canonical Requirements)",
    )

    parser.add_argument(
        "--include-references",
        action="store_true",
        default=False,
        help="Include references/quotes/locators in the PDF (default: false)",
    )

    parser.add_argument(
        "--include-open-questions",
        action="store_true",
        default=False,
        help="Include openQuestions sections (default: false)",
    )

    parser.add_argument(
        "--brd-sections",
        default=None,
        help=(
            "Path to brd_sections.json (default: dev-instructions/scripts/brd_sections.json next to this script)"
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()

    folders = resolve_folders(repo_root)

    input_dir = (
        Path(args.input_dir).resolve()
        if args.input_dir
        else (folders.generated_materials / "canonical-requirements")
    )

    output_pdf = (
        Path(args.output).resolve()
        if args.output
        else (folders.generated_materials / "canonical-requirements.pdf")
    )

    files = iter_requirement_files(input_dir, args.glob)

    build_pdf(
        requirement_files=files,
        output_pdf=output_pdf,
        include_references=bool(args.include_references),
        include_open_questions=bool(args.include_open_questions),
        title=str(args.title),
        brd_sections_path=(Path(args.brd_sections).resolve() if args.brd_sections else None),
    )

    print(f"Wrote PDF: {output_pdf}")


if __name__ == "__main__":
    main()
