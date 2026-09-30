---
paths:
  - "tests/**"
---

# Tests

- pytest, Arrange / Act / Assert, one behaviour per test, names that state the behaviour
  (`test_single_dwelling_filter_excludes_mixed_mutations`).
- Test boundaries (e.g. 2,999 / 3,000 / 30,000 / 30,001 €/m²), not only typical values.
- Use small hand-built fixtures (`tests/fixtures/`), never the real multi-MB DVF file.
- Swap dependencies with `app.dependency_overrides` and pytest fixtures, not with
  monkeypatching module globals.
- Tests that need a database run against real PostgreSQL + PostGIS, never SQLite (no
  PostGIS, different SQL behaviour).
