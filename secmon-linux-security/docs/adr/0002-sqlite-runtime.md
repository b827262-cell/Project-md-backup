# ADR-0002: SQLite WAL with application migrations

- Status: accepted
- Date: 2026-07-10

SecMon P0 uses SQLite in WAL mode with `foreign_keys=ON`, `synchronous=NORMAL`,
and a five-second busy timeout. Migrations are ordered SQL files applied by the
standard-library runner in `database/migrate.py`.
