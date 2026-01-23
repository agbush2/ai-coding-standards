# Authoritative Source Material Inventory & Canonicalization

## Persona
Adopt the persona defined in `../personas/product_manager.md`.
While your primary role is Technical Product Manager, for this specific task you are acting as a **Lead Business Architect**. You are detail-oriented, semantic-focused, and obsessed with traceability.


## Objectives
1.  **Authoritative Inventory**: Create a comprehensive, authoritative inventory of all knowledge contained in the union of all documents in `agile-ai/source-material/`.
2.  **Semantic Extraction**: Extract every business concept, technical component, data element, interface, and capability, ensuring no meaningful item is omitted.
3.  **Contextualization**: For each item, provide a full, source-authentic explanation, capturing nuance, dependencies, and usage.
4.  **Traceability**: Every item must link to its exact source file and section; no item without a source.
5.  **Conflict Detection**: Identify and document all contradictions, ambiguities, or inconsistencies between documents.
6.  **Normalization**: Propose standardized naming conventions based on majority usage, architectural fit, and semantic clarity.
7.  **Completeness & Rigor**: The inventory must be exhaustive, semantically rigorous, and suitable for downstream requirements, architecture, and QA traceability.


---


## Output Destination
Save the final JSON output to: `ai-agile/02_generated_materials/source-material-review.json`

## Output Format (Strict JSON Schema)
```json
{
  "canonical_inventory": [
    {
      "category": "Business Concept | Technical Component | Data Element | Interface | Capability",
      "name": "Canonical Name",
      "full_context": "Verbatim or closely paraphrased paragraph that captures the full source-authentic meaning of this concept, including nuance, dependencies, and usage.",
      "description": "Brief summary of the concept or component for quick scanning.",
      "sources": [
        {
          "file_name": "source_doc1.pdf",
          "section": "Section 3.2 - Platform Overview"
        },
        {
          "file_name": "source_doc2.docx",
          "section": "4.1 Capabilities"
        }
      ],
      "conflicts": [
        {
          "conflicting_source": "source_doc3.xlsx",
          "conflicting_section": "Definitions tab",
          "conflict_description": "Defines term as 'Integration Service Layer', which contradicts the use of 'Platform API Layer' in two other documents."
        }
      ]
    }
  ],
  "summary": {
    "total_items": 97,
    "conflict_count": 12,
    "sources_analyzed": ["source_doc1.pdf", "source_doc2.docx", "source_doc3.xlsx"],
    "notes": "All references to 'tenant' and 'client' were standardized as 'tenant' based on 3:1 usage ratio."
  },
  "validation_status": {
    "completeness_check": "Passed | Failed",
    "traceability_check": "Passed | Failed",
    "issues_found": [
      "Untraceable item: 'CustomerProfile'",
      "2 capabilities not captured from source_doc3.xlsx"
    ]
  }
}
```

---


## Validation Phase (Required)
After the JSON is built, perform a recursive validation check:

1.  **Omission Check**: Did you capture every capitalized term, major section header, and unique concept from every document?
2.  **Traceability Audit**: Does every item have a `sources` array with at least one entry?
3.  **Semantic Audit**: Is every item described with full context and nuance, not just a summary?
4.  **Update Status**: Fill the `validation_status` object in the JSON, including completeness and traceability checks, and list any issues found.


## Final Instructions
- Work in **two distinct logical passes**: (1) Extraction (authoritative, exhaustive), then (2) Validation (semantic and traceability audit).
- Do **not summarize excessively**—capture the full, source-authentic context for every item.
- Ensure **no item appears unless it has an identifiable source**.
- Save your output to `agile-ai/source-material/source-material-review.json`
- Think step-by-step. Be rigorous. Use domain-accurate language. Treat this inventory as the single source of truth for all downstream requirements, architecture, and QA.
```



