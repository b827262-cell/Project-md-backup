# ADR-0001: UTC timestamps and stable event identifiers

- Status: accepted
- Date: 2026-07-10

Persist timestamps as UTC ISO 8601 values with a `Z` suffix. The UI may render
Asia/Taipei for users, but API and database values remain UTC. Every normalized
event receives a deterministic `event_key`; the database unique constraint is
the final deduplication boundary.

This keeps ordering unambiguous across collectors and makes replay/recovery
safe without trusting local server time zones.
