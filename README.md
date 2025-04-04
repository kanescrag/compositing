# Compositing Utilities

A collection of tools used for production with the Nuke compositing DCC

## Utilities

- giant_write: a consolidated in/out node for reading and writing images formats. It also sources database entries for the working context to allow quick access buttons to open shot pages on the Shotgrid production management website

- cmp_mpco_node: a comprehensive shot-hierarchy system that utilises ShotGrid's database and API to plot and cross-reference shot data entries, with event triggers that update colour-coded shot types and connections, reflecting any changes back to the database for alignment. It provides a visual, intuitive way for leads and supervisors to quickly compare and apply shot hierarchy structures for shot production, circumventing the latency involved with manual database updates on the website.

## Requirements

- Python
- ShotGrid API + key
- gfoundation (Giant proprietary API)