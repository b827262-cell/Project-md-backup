# AI-SmartBook-R1 Project State - 202606

## Current Month
2026-06

## Main Code Repo
`b827262-cell/AI-SmartBook-R1`

## Markdown Backup Repo
`b827262-cell/Project-md-backup`

## Current Working Branch
`feat/student-category-cover-reader-chat`

## Current Known Status
Android Chrome mobile reader controls fix is complete. AGY acceptance and user acceptance are both complete. This task can be closed and moved to 1GB cloud computer update.

## Release Commit
`a04232f3037f3751c7a26e81a29de735875d88fb`

## Latest Verified Test Environment

- URL: `http://10.0.3.68:5173/books/book_d1ccf939-47de-479b-98e3-e64a412c2a8c`
- Browser: Android Chrome
- Screen: `412 x 892`
- Viewport: about `411 x 784`
- Pixel ratio: `1.75`
- Debug tool: Eruda `v3.4.3`

## Completed Features

1. Android mobile reader page jump input is available.
2. Current page / total page display is available.
3. Previous / next page controls are available.
4. Mobile reader control panel is visible as a two-row bottom action bar.
5. Existing buttons remain available: 返回 / 目錄 / 問AI / 筆記.
6. PDF display remains functional.

## Latest AGY Acceptance Report
`md/AI-SmartBook-R1/202606/agy-acceptance/a04232f3037f3751c7a26e81a29de735875d88fb.md`

## Latest Deployment Handoff
`md/AI-SmartBook-R1/202606/deployment/2026-06-18-1gb-cloud-update.md`

## Latest Next Task
Update the 1GB cloud computer to `AI-SmartBook-R1` commit `a04232f3037f3751c7a26e81a29de735875d88fb`, rebuild/restart the service, and run Android Chrome manual verification.

## Known Risks

1. 1GB RAM may require swap before `pnpm install` or `pnpm build`.
2. Pre-existing TypeScript typecheck errors were noted by Codex and should be handled separately.
3. The cloud server may still show old UI if the service/build process is not restarted after pull.

## Next Recommended Task
Deploy to the 1GB cloud computer and verify the reader page on Android Chrome after restart.
