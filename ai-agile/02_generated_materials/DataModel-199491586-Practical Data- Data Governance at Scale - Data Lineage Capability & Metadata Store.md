---
source: https://maoperatingsystem.atlassian.net/spaces/DataModel/pages/199491586/Practical+Data+Data+Governance+at+Scale+-+Data+Lineage+Capability+Metadata+Store
confluence_id: 199491586
space: DataModel
version: 41
retrieved: 2026-01-23T12:36:26.804850
format: xhtml
content_hash: 631e48e21d875baf3c276a0c78d067d5
macro_structured_macro: 2
macro_image: 0
macro_link: 6
---

# Practical Data: Data Governance at Scale - Data Lineage Capability & Metadata Store

## About this Document

This document forms part of a series proposing a target reference architecture for Data Governance at scale for large organizations with highly fragmented business processes and data flows, such as large financial institutions with multiple business lines, individual product-aligned platforms, and centralized functions like finance and risk management.  This document provides a deeper dive into one of the architectural components within the architecture.  Links to other documents in this series can also be found below.

This document specifically focuses on the Data Lineage Capability and Metadata Store components.

## Table of Contents

This section lists information contained in this document

## Data Governance at Scale

This section provides lists of other documents within this series

## Data Lineage Capability & Metadata Store

### Overview

The Data Lineage Capabilities and Data Lineage metadata combined enable the organization to understand how data flows throughout the enterprise to deliver business value outputs.

In this reference architecture, we define Technical Lineage as the data dependency between one data element in a data flow and its dependencies.  For example, attribute A in system A depends on the combination of Attribute B in system 2 and attribute C in system 3.   As such, we define the direction of the relationship as being from the downstream attribute to the upstream attribute.   Lineage can exist between systems as well as within a system. Lineage is managed at the lowest level of technical data element, as defined in the Data Inventory model, i.e., an attribute. See Practical Data: Data Governance At Scale - Data Inventory Capability and Metadata Store

We define Business Lineage as the data dependency between logical business definitions of data. Again, at the lowest level of the business data element hierarchy described in the Data Inventory Model.

### Assumptions

Listed below are the series of input assumptions that led to the proposed reference architecture design included in this document.

1. Data Inventory information, which describes the list of physical and business attributes, is stored within the metadata repository component. See Data Inventory for the design of the technical and business hierarchy of data elements (i.e., system->scheme->catalog->attribute, etc.).
2. By definition, data lineage information only describes the flow of data within systems and across system boundaries. Although the data inventory discovery process may identify additional attributes (and associated schemas and systems, etc.) as dependencies that need to be added to the Inventory for future inventory discovery.
3. Technical lineage is defined as the relationship between two lowest-level attributes in the data inventory. Higher-level (i.e., system-to-system dependencies) can then be implied.
4. It may not always be possible to automatically discover technical lineage.  A method will be required to enable system applications to contribute lineage information manually.
5. Business lineage is defined as the associated (implied) lineage of the business data inventory.  Note that the business view can also "prioritize" technical lineage branches to represent the criticality of certain data flows.
6. By definition, Data Inventory processes DO NOT have access to data content - only schema and structural information.  Data Profiling and other Capabilities have access to data content.
### Architecture

## Data Lineage Metadata

### Lineage Data Model Design

Note: Data model designs are included for illustration purposes only and are styled as a graph database with nodes and relationships. This is provided for convenience only, to define a reference architecture for data governance at scale, and does not necessitate a specific data storage method, database technology, or implementation design. See Practical Data: Data Governance at Scale - Conventions

#### Technical Lineage Data Model Design

Three basic scenarios to model data lineage between attributes.

1. Pass-through- In pass-through situations, the downstream from the node is a replica of the upstream "to" attribute.
2. Simple Transformation- In simple transformation situations, the downstream attribute is derived based on the transformation of asingleupstream attribute
3. Complex Transformations- In complex transformation situations, the downstream attribute is derived based on the transformation oftwo or moreupstream attributes. In this situation, it is necessary to introduce a new node element to the data design to capture the data transformation rule.  It is an implementation decision to include this extra node for the other two scenarios.
Data Model Diagram

##### Node Elements

Listed below are the minimum elements required to be stored as part of the data governance metadata node record.

###### NodeType = LINEAGE, NodeSubType = TRANSFORM

Element | Element Description | Example Value
--- | --- | ---
nodeID | The unique ID of the node | LIN000000001
nodeType | The type of node - in this case, LINEAGE | LINEAGE
nodeSubType | The subtype of the node - in this case, TRANSFORM | TRANSFORM
nodeName | The name of the node - in this case, it should be a sensible technical summary of the transformation rule | Convert from ISO2 to ISO3 Country Codes
nodeSpecification | The detailed specification of the node, in this case, the technical data transformation rule for complex data | See example below.
```
 ISO3 lookup table (partial sample, extend as needed)
ISO2_TO_ISO3 = {
    "US": "USA",
    "CA": "CAN",
    "GB": "GBR",
    "FR": "FRA",
    "DE": "DEU",
    # Add more codes as needed
}

def iso2_to_iso3(iso2_code: str) -> str:
    """
    Convert ISO2 country code to ISO3 using a lookup table.
    Args:
        iso2_code (str): Two-letter ISO2 country code (case-insensitive).
    Returns:
        str: ISO3 country code if found, else None.
    """
    if not iso2_code:
        return None
    return ISO2_TO_ISO3.get(iso2_code.upper())]]>
```
##### Relationship Elements

Listed below are the minimum elements required to be stored as part of a data governance metadata relationship record between two nodes.

###### RelType = LINEAGE, RelSubType=DEPENDS_ON

Element |  | Example Value
--- | --- | ---
relType | The type of relationship - in this case, LINEAGE | LINEAGE
relSubType | The subtype of relationship - in this case, DEPENDS_ON | DEPENDS_ON
relFrom | Lineage source node ID - i.e., the downstream node in the lineage flow | ATT000000001
relTo | Lineage dependency node ID - i.e., the upstream node in the lineage flow. | ATT000000002
relName | Relationship Name - in this case, a summary of the simple transformation rule | Convert from ISO2 to ISO3 Country Codes
relSpecification | The detailed specification of the relationship for passthrough and simple transformation situations, specified as technical transformation details. | See example below.
```
 ISO3 lookup table (partial sample, extend as needed)
ISO2_TO_ISO3 = {
    "US": "USA",
    "CA": "CAN",
    "GB": "GBR",
    "FR": "FRA",
    "DE": "DEU",
    # Add more codes as needed
}

def iso2_to_iso3(iso2_code: str) -> str:
    """
    Convert ISO2 country code to ISO3 using a lookup table.
    Args:
        iso2_code (str): Two-letter ISO2 country code (case-insensitive).
    Returns:
        str: ISO3 country code if found, else None.
    """
    if not iso2_code:
        return None
    return ISO2_TO_ISO3.get(iso2_code.upper())]]>
```
## Data Lineage (Discovery) Capability

The Data Lineage Capability consists of two parts

1. Data Lineage Engine, which schedules and collects all the information from the individual collectors
2. Data Lineage Connectors are responsible for providing various mechanisms for collecting lineage information through a scalable framework.
Definitionally, Lineage connectors are only intended to discover lineage information; however, they may also discover attributes that have yet to be identified through the Data Inventory process.   In these cases, the Data Lineage capability should forward these missing inventory items to the Data Inventory capability via the Orchestration capability for action. See Practical Data: Data Governance At Scale - Data Inventory Capability and Metadata Store

### Lineage Data Connectors

Data lineage discovery must be able to identify lineage information from various sources before contributing it to the data lineage metadata store within the Data Governance Metadata Repository.  This reference architecture design establishes an extensible "Connector" based framework where a variety of connectors can be added as needed to discovery the required lineage information.

As connectors will tend to be technology-aligned, it may be appropriate to couple Data Lineage collectors with Data Inventory connectors as a single instance per tech stack, i.e., a combined MSSQL Data Inventory and Data Lineage Connector.

#### Self-Service Connectors

Self-service connectors enable individuals to submit lineage information themselves, which, for one or more reasons, cannot be discovered automatically. Two

- API Base Self-Service Connector- The API Self-Service Connector enables users and systems to submit data lineage information via an API service. This allows business applications to self-register their lineage information and keep up with changes automatically,
- End User Self Service Connector- The End User Self Service Connector allows users to interact with a webpage to define lineage between attributes within the inventory, ideally through the single data governance Front End (See xxxxxx)
#### Out of the Box Automated Lineage Connectors

- Data Transformation Engine Lineage Connectors- Data Transformation Engine connectors enable automated discovery of lineage information from industry-standard data transformation and pipeline tools.  Examples include Airflow,
- Database Engine Lineage Connectors- Database Engine Connectors directly connect to the underlying database engines and utilize the configuration details within these to facilitate the automated discovery of lineage information from industry-standard database technologies. Examples include Oracle, MSSQL, etc
- Code Reader Lineage Connectors- Code Reader Lineage Connectors enable automated discovery of lineage information by interpreting source code repositories of applications to understand system interactions.
- 3rd Party Application Connectors- 3rd Party Application connectors directly integrate with specific 3rd party applications such as commercial CRM, ERP or other platforms, to utilize the internal configuration details of these platforms to facilitate automated discovery of lineage information.  Examples include Salesforce, SAP, Workday, Microsoft Dynamics, etc.
## Advanced Capabilities

The advanced capabilities are additional topics relating to data lineage that are not yet folded into the reference designs above. These are included for reference only in the latest trends and discussions topic relating to Data Lineage.

### Context-Aware Data Lineage

Context-aware data lineage is the latest iteration of data lineage capability in the data governance space. Data lineage traces a single understanding of the flow of data throughout an environment to establish a business output.   For simplicity, let's consider a single business outcome, and we aim to trace data lineage through the systems to a specific data element on the report.

"Traditional" data lineage takes a "column" based view of data lineage and performs well when all data in a column follows the same path to the endpoint destination.   However, in many large organizations, the path that data flows through an environment depends on the context of the data or a specific row in the report.  For example, if an exposures report includes data from two product lines, the exposures column in the report for product A could follow one path and the exposure column for product B another. Golden record data within reference data master data management platforms is often a combination of data from multiple sources, combined in real-time. This is another example of context-aware data lineage, where the current data content is also a result.

Context-aware lineage enables lineage graphs to consider the context of the output report recordsets, which is typically defined at a high-level organizational level. For example, context could be a combination of one or more of the products, regions, business lines, etc.

## Record Level Lineage (Data Tracing)
