---
paths:
  - "src/immo_paris/db/**"
  - "migrations/**"
  - "compose.yaml"
---

# Database

- `db/models.py` is the source of truth of the schema. Any change to it needs a migration:
  follow the `new-migration` skill.
- Never edit a migration that has been applied outside your machine: write a new one.
- Money is `Numeric` / `Decimal`, never `float`.
- Coordinates are WGS 84 (SRID 4326) `geography`. `ST_MakePoint` takes
  **longitude first**, then latitude.
- Business invariants are enforced by the database too (`CHECK`, `UNIQUE`, `NOT NULL`),
  not only by the Python pipeline. Name constraints through the naming convention in
  `db/base.py`.
- Every index must serve a known API query; check new queries with `EXPLAIN ANALYZE`.
- Write whole-dataset loads as one transaction (replace a year atomically) and refresh
  materialized views with `REFRESH MATERIALIZED VIEW CONCURRENTLY` afterwards.
- Keep PostgreSQL + PostGIS versions aligned with the target Amazon RDS instance.
