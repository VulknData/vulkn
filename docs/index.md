# VULKИ Documentation

## Welcome to VULKИ

!!! note
    VULKИ 19.0.0 is a Proof Of Concept release. APIs will change in the coming releases as Vulkn reaches stability.


VULKИ (Vulkn) is a specialized, environmentally friendly, eco-system for manipulating and managing large volumes of data at petabyte scale.

Vulkn is underpinned by the high-performance Open Source OLAP database, Yandex ClickHouse. Rather than re-invent the wheel (or mask the amazing technology that is ClickHouse), Vulkn focuses on the areas of DataOps, simplification and automation. Users can easily extend Vulkn, and the SQL layer, with their own SQL clauses and functions via Python as well as use Python bindings to work with ClickHouse in much the same way they would other modern data systems, specifically those based on functional programming.

## Love your Data. Love the Environment.

Today, data centres/servers consume more than 17% of all global electricity with projections in excess of 20% by the mid-2020s. A significant portion of this can be directly attributed to data transmission, processing and presentation operations found within 'modern' BigData architectures.

Whilst current CPUs, GPUs and memory modules are capable of processing and moving gigabytes of data per second across a single core, many of the popular tools and libraries for managing large, petabyte scale data sets make poor use of these capabilities. There are some commercial systems although few, if any, Open Source systems that push current chip architectures to deliver at peak energy efficiency.

Despite some commitment to renewables; data centres, hyperscalers and telecommunications companies are unseating oil, coal and gas companies as some of the chief polluters and energy consumers on our planet. This is unacceptable and unethical.

## What sorts of computing problems does Vulkn solve?

Vulkn itself does very little - it aims to expose the true power of ClickHouse that would otherwise require non-trivial scaffolding. That being said Vulkn is targeting:

- Online Analytical Processing (OLAP)
- Time-Series analytics
- Log processing / event analytics
- Data ingestion and management within ClickHouse
- General ClickHouse accessibility and usability

## Features

- Python client interfaces for ClickHouse
* Python API for DBMS management
* Python DataFrame interface with Pandas integration
* Python datatype bindings including Python operators, arrays, dictionaries and functions
* Reader interface for loading external data with type inference
* Folios and Workspaces - re-usable dynamic and static ClickHouse environments
* SQL Engine with AST rewriting capabilities
* SQL Extension framework for extending the ClickHouse SQL/dialect