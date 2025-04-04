# Compositing Utilities

A collection of tools used for production with the Nuke compositing DCC

## Utilities

- g_write_node: a consolidated in/out node for reading and writing images formats. It also sources database entries for the working context to allow quick access buttons to open shot pages on the Shotgrid production management website

- g_shot_hierarchy_system: a comprehensive shot-hierarchy system that utilises ShotGrid's database and API to plot and cross-reference shot data entries, with event triggers that update colour-coded shot types and connections, reflecting any changes back to the database for alignment. It provides a visual, intuitive way for leads and supervisors to quickly compare and apply shot hierarchy structures for shot production, circumventing the latency involved with manual database updates on the website. And example of the mpco tool can be viewed here: https://vimeo.com/manage/videos/1072364893

- g_aov_recombination: Compact node setup for extracting AOVs from a multi-layer EXR, recombining them, and offering individual slider controls per AOV to adjust intensity or merge behaviour, enabling efficient and precise compositing control.

- g_create_light_rig: Small node to allow the user to create new set asset instances to connect with the shot hierarchy tool for assignemnt to the Shotgrid database

  ![Hierarchy Node -Shot](https://github.com/user-attachments/assets/7f09c798-b9f7-4e2b-8c02-880016e12efe)
  ![Hierarcyh Node - Set](https://github.com/user-attachments/assets/58eefbb7-1101-4f00-93a7-97d3e26699da)
  ![Hierarchy Node Structure](https://github.com/user-attachments/assets/483fc75d-f25d-4222-b995-0c580059b9b0)


## Requirements

- Python
- ShotGrid API + key
- gfoundation (Giant proprietary API)
