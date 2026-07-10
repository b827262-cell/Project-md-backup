# SecMon Phase Issue 與 AI 分派索引

## 1. 使用方式

本文件是 SecMon 執行入口。每個 Phase 先閱讀對應 Issue，再依 AI 任務書執行：

- GPT-5.6：`AGENT_ASSIGNMENT_GPT56.md`
- AGY（Gemini 3.5 Flash）：`AGENT_ASSIGNMENT_AGY.md`
- 交接規則：`AI_HANDOFF_AND_RELEASE_GATES.md`
- 全排程：`PROJECT_PLAN_AND_SCHEDULE.md`

## 2. Phase Issues

| Phase | 日期 | Implementation / Main Owner | Verification / Fix Owner | GitHub Issue |
|---|---|---|---|---|
| P0 規格與骨架 | 2026-07-10～07-12 | GPT-5.6 | AGY Gate | [#1](https://github.com/b827262-cell/Project-md-backup/issues/1) |
| P1 SQLite 與 SSH | 2026-07-13～07-19 | GPT-5.6 | AGY Gate | [#2](https://github.com/b827262-cell/Project-md-backup/issues/2) |
| P2 Nginx／Suricata／API | 2026-07-20～07-26 | GPT-5.6 | AGY Gate | [#3](https://github.com/b827262-cell/Project-md-backup/issues/3) |
| P3 前台整合 | 2026-07-27～08-02 | AGY | GPT-5.6 API 修復 | [#4](https://github.com/b827262-cell/Project-md-backup/issues/4) |
| P4 封鎖／RBAC／稽核 | 2026-08-03～08-09 | GPT-5.6 | AGY Security Gate | [#5](https://github.com/b827262-cell/Project-md-backup/issues/5) |
| P5 試營運／Release | 2026-08-10～08-16 | AGY Gate | GPT-5.6 修復 | [#6](https://github.com/b827262-cell/Project-md-backup/issues/6) |

## 3. 執行順序

```text
Issue #1 P0
   ↓ PASS
Issue #2 P1
   ↓ PASS
Issue #3 P2
   ↓ PASS
Issue #4 P3
   ↓ PASS
Issue #5 P4
   ↓ PASS
Issue #6 P5
   ↓
人類專案負責人決定正式部署與是否啟用自動封鎖
```

未通過目前 Phase Gate 時，不應直接開始下一個 Phase 的高風險工作。

## 4. 分派說明

GPT-5.6 與 AGY 是 AI 工作角色，不是此 repository 中可指派的 GitHub 使用者。因此：

- Issue 標題使用 `[GPT-5.6]`、`[AGY]` 或箭頭表示執行與驗證順序。
- Issue body 明確記錄 Owner。
- 不使用虛假的 GitHub assignee。
- 人類專案負責人可在實際執行時將 Issue 指派給操作該 AI 的帳號。

## 5. 每個 Issue 的最低完成條件

- [ ] Implementation 完成並提交
- [ ] 自測證據完整
- [ ] Handoff 完整
- [ ] AGY 獨立驗證
- [ ] Blocker／High 缺陷關閉
- [ ] Release Gate 通過
- [ ] 文件同步

## 6. 最終決策邊界

AGY 可做 Release Gate 判定，但以下動作必須由人類專案負責人核准：

- 正式環境部署
- 變更公司防火牆
- 啟用自動封鎖
- 接受未修復的重大剩餘風險
- 使用真實公司網段、客戶資料或正式帳號進行測試
