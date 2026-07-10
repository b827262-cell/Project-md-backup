# ADR-0003: FastAPI-compatible backend boundary

- Status: accepted
- Date: 2026-07-10

The backend is organized around an API package and typed settings so the P2
HTTP layer can use FastAPI without moving domain code. P0 does not add a web
server dependency yet; this avoids presenting an empty endpoint surface as an
implemented API.
