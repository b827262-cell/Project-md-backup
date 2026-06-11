# 08_TEST_COMMANDS_SMOKE

Last Updated: 2026-06-11
Source Pack Version: auto-generated (mechanical, no-LLM)
Purpose: Build + smoke test commands
Read This When: running validation

> Auto-bundled from RAW_REPORTS. Full detail lives in GitHub; this pack
> holds only each report's `## Current Truth` section + an index.

## Current Truth

### PHASE_2D_E_RC1_RUNTIME_GATE_SMOKE_TEST.md


- RC1_STUDENT_RUNTIME_GATE = PASS
- SQLITE_TABLE_COUNT = 76
- SQLITE_SCHEMA_IMPORT_OK = YES
- SQLITE_PUSH_SMOKE = PASS
- RC1_INSERT_SELECT_SMOKE = PASS (16/16 tables)
- PROVIDER_MODE_SMOKE = PASS (isSqliteMode=true, 16/16 tables present with rows)
- PNPM_BUILD = PASS (5 pre-existing warnings, no errors)
- SQLITE_LEFTOVERS = 0 (Phase 2D-E temporary smoke artifacts only)
- PUSH_METHOD = direct drizzle-kit CLI with `--url=/tmp/phase2d-e-rc1-smoke.db --force`
- FORMAL_DB_TOUCHED = NO
- No schema / router / client / db.ts changes in this phase

---

## Related Raw Reports

- `docs/project/RAW_REPORTS/SQLITE_RC1/SQLITE_SMOKE_TEST_REPORT.md`
- `docs/project/RAW_REPORTS/SQLITE_RC1/PHASE_2D_E_RC1_RUNTIME_GATE_SMOKE_TEST.md`

## Next Actions

