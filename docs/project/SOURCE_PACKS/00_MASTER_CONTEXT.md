# 00_MASTER_CONTEXT

Last Updated: 2026-06-08
Purpose: Single authoritative context for all AI tools.

# Raw Report Format Rule

Authoritative for: ChatGPT, Claude Code, Codex CLI, Gemini CLI, AGY.
On any conflict, 00_MASTER_CONTEXT wins.

## Why this rule exists

SOURCE_PACKS are built mechanically. The build script uses no LLM and does not summarize semantically. It extracts the `## Current Truth` section from each raw report and rolls it into fixed source packs. Full detail stays in RAW_REPORTS.

## Required sections near the top of every AI-generated report

Every report MUST contain these exact level-2 headings:

```markdown
## Current Truth
- Verified conclusions only, usually 3-8 bullets.
- Verified PASS / FAIL states.
- No long logs.
- No speculation unless explicitly marked unverified.

## Next Actions
- The next executable steps.
- Name the owner/tool when useful: Codex, Claude Code, ChatGPT, AGY.
- Include validation command or acceptance criteria when possible.
```

## Heading format is strict

Valid:
- `## Current Truth`

Invalid:
- `### Current Truth`
- `## current truth`
- `## Current Truth:`
- `##Current Truth`

`## TL;DR` is accepted as the only alias.

## What happens if a report omits Current Truth

It is still indexed in `14_ARCHIVE_INDEX.md`, but its conclusions are not inlined into any source pack.

## Do NOT

- Do NOT rely on LLM compression during hook execution.
- Do NOT place secrets, tokens, `.env` values, API keys, or credentials in raw reports.
- Do NOT treat source packs as the only archive. Raw reports are the permanent record.

## Build-system invariants

1. Secret guard uses strict key-shape patterns only. It must not fail on educational words such as `.env`, `token`, `API key`, or `credential`.
2. Do not paste a full live-matching fake secret example into this file. Use a throwaway validation file only, then delete it.
3. Heading must be exact: `## Current Truth`.
4. Single push entry point: only `~/Project-md-backup/scripts/md-autopush-hook.sh` may run build, healthcheck, commit, and push.

