
# Source Material Review

## Canonical Inventory

### Data Governance Metadata Repository
- **Category**: Technical Component
- **Name**: Data Governance Metadata Repository
- **Full Context**: The Data Governance Metadata Repository is responsible for storing all Data Governance Metadata Model within a single location for use by other components. It includes the complete Data Governance Metadata Data Model, supporting centralized, auditable, and version-controlled metadata management. (Source: DataModel-205422624-Practical Data- Data Governance At Scale - Data Governance Metadata Repository & Data Model.md)
- **Description**: Centralized store for all data governance metadata, supporting other capabilities.
- **Sources**: DataModel-205422624-Practical Data- Data Governance At Scale - Data Governance Metadata Repository & Data Model.md (About this Document)
- **Conflicts**: None

### Data Inventory Capability
- **Category**: Capability
- **Name**: Data Inventory Capability
- **Full Context**: The Data Inventory Capability enables the collection and management of the technical and business inventory data elements across the organisation. Data Inventory information forms the most fundamental information collated about the data storage and flows within the organization, and serves as the basis for all other aspects of data governance, including Lineage and Quality. (Source: DataModel-202833967-Practical Data- Data Governance At Scale - Data Inventory Capability and Metadata Store.md)
- **Description**: Enables collection and management of inventory data elements.
- **Sources**: DataModel-202833967-Practical Data- Data Governance At Scale - Data Inventory Capability and Metadata Store.md (About)
- **Conflicts**: None

### Attribute
- **Category**: Data Element
- **Name**: Attribute
- **Full Context**: An attribute is the lowest level of a technical hierarchy, which represents the point at which data values are stored and managed. (Source: DataModel-202833967-Practical Data- Data Governance At Scale - Data Inventory Capability and Metadata Store.md)
- **Description**: The lowest level of a technical data management hierarchy.
- **Sources**: DataModel-202833967-Practical Data- Data Governance At Scale - Data Inventory Capability and Metadata Store.md (Technical Data Inventory Model Design)
- **Conflicts**: None

### Data Quality Correlation Engine Component
- **Category**: Technical Component
- **Name**: Data Quality Correlation Engine Component
- **Full Context**: The Data Quality Correlation Engine Component acts as a central hub for consuming live data quality issues as they are published by various data quality assessment engines across the enterprise. Its primary function is to evaluate incoming issues and, based on predefined rules or AI, determine the required exception-management work to resolve them and initiate the appropriate downstream processes. (Source: DataModel-272957441-Practical Data- Data Governance at Scale - Data Quality Correlation Engine Component.md)
- **Description**: Central hub for evaluating and managing data quality issues and exception workflows.
- **Sources**: DataModel-272957441-Practical Data- Data Governance at Scale - Data Quality Correlation Engine Component.md (Overview)
- **Conflicts**: None

### Data Lineage Capability
- **Category**: Capability
- **Name**: Data Lineage Capability
- **Full Context**: The Data Lineage Capability enables the organization to understand how data flows throughout the enterprise to deliver business value outputs. Technical Lineage is defined as the data dependency between one data element in a data flow and its dependencies, managed at the lowest level of technical data element (attribute). (Source: DataModel-199491586-Practical Data- Data Governance at Scale - Data Lineage Capability & Metadata Store.md)
- **Description**: Enables understanding and management of data flow and dependencies across the enterprise.
- **Sources**: DataModel-199491586-Practical Data- Data Governance at Scale - Data Lineage Capability & Metadata Store.md (Overview)
- **Conflicts**: None

### Data Quality Capability
- **Category**: Capability
- **Name**: Data Quality Capability
- **Full Context**: The Data Quality capability enables the evaluation and recording of the current data quality performance of live data against the latest data quality requirements. Resulting data quality issues are tracked as work items in the work queues. The data quality capability is authoritative for generating and managing Data Quality Issues. (Source: DataModel-216301569-Practical Data- Data Governance at Scale - Data Quality Capability & Metadata Store.md)
- **Description**: Enables evaluation, tracking, and management of data quality across the organization.
- **Sources**: DataModel-216301569-Practical Data- Data Governance at Scale - Data Quality Capability & Metadata Store.md (About this Document)
- **Conflicts**: None

### Naming Conventions
- **Category**: Convention
- **Name**: Unique ID and Node Naming Conventions
- **Full Context**: The project employs a context-based naming standard for unique sample IDs to represent sample data governance metadata. Node and relationship IDs follow a structured convention based on type and subtype, e.g., INVENTORYATTRIBUTEATTATT000000001. (Source: DataModel-202735632-Practical Data- Data Governance at Scale - Conventions.md)
- **Description**: Standardized naming conventions for unique IDs and nodes across all metadata.
- **Sources**: DataModel-202735632-Practical Data- Data Governance at Scale - Conventions.md (Conventions)
- **Conflicts**: None

## Summary
- Total items: 7
- Conflict count: 0
- Sources analyzed: All .md files in ai-agile/02_generated_materials
- Notes: Naming conventions for technical components and data elements standardized to match majority usage in the source materials. No conflicts or ambiguities detected between documents. All items are traceable to their source files and sections.

## Validation Status
- Completeness check: Passed
- Traceability check: Passed
- Issues found: None
