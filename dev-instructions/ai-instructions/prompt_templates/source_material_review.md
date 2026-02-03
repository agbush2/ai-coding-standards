# Authoritative Source Material Inventory & Canonicalization

## Persona
Adopt the persona defined in `../personas/product_manager.md`.
While your primary role is Technical Product Manager, for this specific task you are acting as a **Lead Business Architect**. You are detail-oriented, semantic-focused, and obsessed with traceability.


## Objectives
1.  **Authoritative Inventory**: Create a comprehensive, authoritative inventory of all knowledge contained in the union of all `.md` documents in `ai-agile/02_generated_materials/`.
2.  **Semantic Extraction**: Extract every business concept, technical component, data element, interface, and capability, ensuring no meaningful item is omitted.
3.  **Contextualization**: For each item, provide a full, source-authentic explanation, capturing nuance, dependencies, and usage.
4.  **Traceability**: Every item must link to its exact source file and section; no item without a source.
5.  **Conflict Detection**: Identify and document all contradictions, ambiguities, or inconsistencies between documents.
6.  **Normalization**: Propose standardized naming conventions based on majority usage, architectural fit, and semantic clarity.
7.  **Completeness & Rigor**: The inventory must be exhaustive, semantically rigorous, and suitable for downstream requirements, architecture, and QA traceability.


---


## Output Destination
Save the final assessment output in markdown format to: `ai-agile/02_generated_materials/source-material-review.md`

## Output Format (Markdown)
The assessment must be generated in markdown format. Structure the output as follows:

### Canonical Inventory
For each item, provide:
- **Category**: (Business Concept | Technical Component | Data Element | Interface | Capability)
- **Name**: Canonical Name
- **Full Context**: Verbatim or closely paraphrased paragraph that captures the full source-authentic meaning, including nuance, dependencies, and usage.
- **Description**: Brief summary for quick scanning.
- **Sources**: List of file names and sections.
- **Conflicts**: (if any) List of conflicting sources, sections, and descriptions.

### Summary
- Total items
- Conflict count
- Sources analyzed
- Notes (e.g., naming standardizations)

### Validation Status
- Completeness check: Passed | Failed
- Traceability check: Passed | Failed
- Issues found: List any issues (e.g., untraceable items, missing capabilities)

---


## Validation Phase (Required)
After the inventory is built, perform a recursive validation check:

1.  **Omission Check**: Did you capture every capitalized term, major section header, and unique concept from every document?
2.  **Traceability Audit**: Does every item have a `sources` array with at least one entry?
3.  **Semantic Audit**: Is every item described with full context and nuance, not just a summary?
4.  **Update Status**: Fill the `validation_status` object in the JSON, including completeness and traceability checks, and list any issues found.


## Final Instructions
- Work in **two distinct logical passes**: (1) Extraction (authoritative, exhaustive), then (2) Validation (semantic and traceability audit).
- Do **not summarize excessively**—capture the full, source-authentic context for every item.
- Ensure **no item appears unless it has an identifiable source**.
- Save a structured JSON artifact to `ai-agile/02_generated_materials/source-material-review.json`.
- Search and extract from all `.md` files in `ai-agile/02_generated_materials/`.
- Think step-by-step. Be rigorous. Use domain-accurate language. Treat this inventory as the single source of truth for all downstream requirements, architecture, and QA.
```



