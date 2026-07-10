# ADR-0004: Password hashes and role-based authorization

- Status: accepted
- Date: 2026-07-10

The users table stores only password hashes. Authentication and session/token
details are deferred to P4, while the schema reserves `admin`, `analyst`, and
`viewer` roles. Authorization must be enforced server-side.
