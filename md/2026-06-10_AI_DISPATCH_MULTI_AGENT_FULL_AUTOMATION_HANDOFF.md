# 2026-06-10 AI Dispatch 多 Agent 全自動化 Handoff

## 目的

本文件用於換分頁 / 新聊天視窗延續執行，整理本輪在 E500 Linux 主機上完成的 ChatGPT → GitHub → E500 → AGY / Codex CLI / Claude Code 多 Agent 自動化流程。

核心成果：

- 已建立並驗證 `ai-dispatch-handoff-private` 任務交換區。
- 已讓 `run-tasks-multi-agent.sh` 能依序呼叫 AGY、Codex、Claude。
- 已修掉 stdin 被 CLI 吃掉、AGY 環境寫入、AGY 卡住 timeout、fail-fast deps skip 等問題。
- 已完成 SmartBook SQLite / MySQL 相容性自動化修補一輪。
- t1 AGY、t2 Codex、t3 Claude 已順利跑通，並通過 `pnpm build`。

---

## 一、目前主機與目錄

### E500 主機主要路徑

```bash
~/project/ai-dispatch-handoff-private
~/project/ai-dispatch
~/project/smartbook-lite-rc1
~/project/smartbook-lite-rc1-ai-dispatch-test
```

### 1. GitHub 任務交換 repo

```bash
~/project/ai-dispatch-handoff-private
```

Remote：

```bash
https://github.com/b827262-cell/ai-dispatch-handoff-private.git
```

主要檔案：

```text
README.md
scripts/run-tasks-multi-agent.sh
examples/tasks.multi-agent.example.json
tasks/current/tasks.json
latest/e500/HANDOFF_LATEST.md
```

### 2. 本機 runner 工作目錄

```bash
~/project/ai-dispatch
```

主要檔案：

```text
run-tasks-multi-agent.sh
logs/
```

這個目錄主要作為本機 runner / log / diff 備份使用，不一定是 git repo。

### 3. SmartBook 原始主目錄

```bash
~/project/smartbook-lite-rc1
```

注意：此目錄本身可能 dirty，不建議直接用來跑 multi-agent。

### 4. SmartBook 乾淨測試 worktree

```bash
~/project/smartbook-lite-rc1-ai-dispatch-test
```

分支：

```bash
auto/dispatch-test-20260610-135519
```

目前 multi-agent 測試都在此 worktree 執行。

---

## 二、本次自動化任務定位

本輪不是做 MySQL / SQLite 資料同步。

不是：

```text
MySQL 資料複製到 SQLite ❌
SQLite 資料同步回 MySQL ❌
```

而是：

```text
SmartBook MySQL / SQLite 程式碼相容性修補與驗證 ✅
```

具體目標：

```text
找出 SmartBook 程式碼中 MySQL-only 或 SQLite 不相容之處，
用最小 patch 修正，
保留 MySQL 原本語意不被破壞，
並用 pnpm build 驗證。
```

---

## 三、multi-agent 任務分工

任務檔：

```bash
~/project/ai-dispatch-handoff-private/examples/tasks.multi-agent.example.json
```

角色分工：

```text
t1 agy：
分析 server/routers/smartBookRouter.ts 的 SQLite migration 風險。

t2 codex：
依 t1 分析，對 server/routers/smartBookRouter.ts 做最小相容修補，並跑 pnpm build。

t3 claude：
檢查 server/stats.ts 的 SQLite stats / fallback 邏輯，並跑 pnpm build。
```

---

## 四、runner 已完成修補

### 1. 修 stdin isolation

原始問題：

```bash
done < <(jq -c '.tasks[]' "$TASKS")
```

AGY / Codex / Claude 可能吃掉 runner stdin，導致 t1 跑完後 t2/t3 不執行。

已在各 CLI 呼叫後加入：

```bash
</dev/null
```

結果：t1 / t2 / t3 可以正確依序執行。

相關 commit：

```text
c1c994e fix runner stdin isolation for agent CLIs
```

---

### 2. AGY 從 gemini alias 改為真正呼叫 agy

本機 AGY CLI：

```bash
command -v agy
# /home/b827262/.local/bin/agy

agy --version
# 1.0.6
```

runner 已將：

```bash
gemini|agy|google) bin=gemini ;;
```

改為：

```bash
gemini|google) bin=gemini ;;
agy)           bin=agy ;;
```

AGY task 也改成：

```json
"agent": "agy"
```

相關 commit：

```text
a515970 switch analysis agent from gemini to agy CLI
```

---

### 3. 修 AGY writable HOME / XDG 問題

AGY 初始失敗錯誤：

```text
Failed to redirect output for CLI: creating log file:
open /home/b827262/.gemini/antigravity-cli/log/cli-xxxx.log:
read-only file system

socket: operation not permitted
```

已新增 `run_agy()`，使用獨立 writable base：

```bash
AGY_PREFLIGHT="${AGY_PREFLIGHT:-0}"
RUNNER_HOME="${HOME}"

run_agy() {
  local prompt="$1" model="${2:-}"
  local agy_base="${AGY_BASE_DIR:-$RUNNER_HOME/.cache/ai-dispatch/agy}"
  mkdir -p \
    "$agy_base/home" \
    "$agy_base/config" \
    "$agy_base/cache" \
    "$agy_base/state" \
    "$agy_base/tmp"

  env \
    HOME="$agy_base/home" \
    XDG_CONFIG_HOME="$agy_base/config" \
    XDG_CACHE_HOME="$agy_base/cache" \
    XDG_STATE_HOME="$agy_base/state" \
    TMPDIR="$agy_base/tmp" \
    agy ${model:+--model "$model"} -p "$prompt" </dev/null 2>&1
}
```

AGY 支援 `--model`，不支援短版 `-m`。

---

### 4. 新增 AGY preflight

AGY preflight 可用：

```bash
AGY_PREFLIGHT=1
```

流程：

```text
先執行 agy --version
再執行 run_agy "只回覆 OK"
通過後才進正式 t1 AGY 分析
```

---

### 5. 修 fail-fast 與 deps skip

已修正 `run_agent()`，agent 非零退出時不會被誤判 pass。

目前正確行為：

```text
t1 agy fail
→ t2 codex skip
→ t3 claude skip
```

---

### 6. 新增 AGY_TIMEOUT

問題：AGY preflight 可以成功，但 t1 分析大型 `smartBookRouter.ts` 時可能卡住。

已加入：

```bash
AGY_TIMEOUT="${AGY_TIMEOUT:-180}"
```

並在 `run_agy()` 中使用：

```bash
timeout --foreground "${AGY_TIMEOUT}s" env \
  HOME="$agy_base/home" \
  XDG_CONFIG_HOME="$agy_base/config" \
  XDG_CACHE_HOME="$agy_base/cache" \
  XDG_STATE_HOME="$agy_base/state" \
  TMPDIR="$agy_base/tmp" \
  agy ${model:+--model "$model"} -p "$prompt" </dev/null 2>&1
```

已完成語法檢查：

```bash
bash -n ~/project/ai-dispatch/run-tasks-multi-agent.sh
bash -n ~/project/ai-dispatch-handoff-private/scripts/run-tasks-multi-agent.sh
```

結果：syntax OK。

建議 commit 訊息：

```bash
git commit -m "fix: add timeout guard for agy runner"
```

---

## 五、測試 worktree 環境修復

### 原問題

Codex t2 第一次失敗不是程式錯，而是測試 worktree 沒有 node_modules：

```text
sh: 1: vite: not found
WARN Local package.json exists, but node_modules missing
```

### 已修復

在：

```bash
~/project/smartbook-lite-rc1-ai-dispatch-test
```

執行：

```bash
pnpm install --frozen-lockfile
```

結果：成功。

確認 vite：

```bash
test -x node_modules/.bin/vite && echo "vite OK" || echo "vite missing"
```

結果：

```text
vite OK
```

### build 驗證

執行：

```bash
pnpm build
```

結果：成功。

已知 warning：專案既有重複物件鍵名警告，不影響 build：

```text
getCategoryExamSources
searchExamSources
addCategoryExamSource
removeCategoryExamSource
viewQA
```

---

## 六、本輪 full pipeline 執行結果

執行命令：

```bash
cd ~/project/smartbook-lite-rc1-ai-dispatch-test

AGY_TIMEOUT=60 \
AGY_PREFLIGHT=1 \
RETRIES=1 \
GEMINI_EDIT=0 \
~/project/ai-dispatch/run-tasks-multi-agent.sh \
~/project/ai-dispatch-handoff-private/examples/tasks.multi-agent.example.json
```

中間曾發現 60 秒對 AGY t1 大型分析不足：

```text
AGY preflight ✅
t1 AGY 60 秒 timeout ❌
```

後續 Antigravity / multi-agent 再執行後，最終回報：

```text
t3 Claude 任務已順利完成
pnpm build 驗證通過
smartBookRouter.ts 與 stats.ts 變更已備份至 ~/project/ai-dispatch/logs/
```

目前可視為：

```text
AGY t1 分析 ✅
Codex t2 修 smartBookRouter.ts ✅
Claude t3 檢查 / 修 stats.ts ✅
pnpm build ✅
```

---

## 七、目前程式變更摘要

### Git status 摘要

```text
M  server/routers/smartBookRouter.ts
M  server/stats.ts
?? .agent-notes/
?? tmp_t3.json
```

### diff stat

```text
server/routers/smartBookRouter.ts：23 行新增，3 行刪除
server/stats.ts：28 行新增，11 行刪除
```

---

## 八、server/routers/smartBookRouter.ts 修改內容

由 t2 Codex 修改。

核心變更：

```text
將 SQLite 專用或 MySQL-only 的 INSERT IGNORE 邏輯改寫為：
先 select 檢查 (bookId, question) 是否存在，
若不存在才執行 insert。
```

目的：

```text
避免 INSERT IGNORE / OR IGNORE 在跨資料庫 ORM 或不同 dialect 中造成相容性風險。
保留原本「已存在就略過」的語意。
```

注意事項：

```text
select-before-insert 在高併發下不是完全 atomic。
若資料表已有 unique constraint，低頻建議問題快取場景可接受。
若未來此處變高頻寫入，應改成 dialect-aware upsert 或 transaction/unique constraint 保護。
```

---

## 九、server/stats.ts 修改內容

由 t3 Claude 修改。

核心變更：

```text
1. 將 adminStatsTimestamp 改成 statsTimestamp。
2. 新增 statsDate() 統一處理 SQLite / MySQL timestamp 差異。
3. 修復 getUserStats 在 SQLite 下 gte(col, Date) 可能造成 better-sqlite3 崩潰的問題。
4. 修復前端週 / 日圖表因把 SQLite 秒數 timestamp 當毫秒處理，導致資料落到 1970 年的問題。
```

Claude 判斷：

```text
getUserStats 在 SQLite 模式下必定崩潰，已修正。
stats.ts 原本一律從 ../drizzle/schema 取 MySQL 定義，導致 SQLite gte(col, Date) 拋錯。
new Date(conv.createdAt) 若遇 SQLite 秒數 timestamp，會造成圖表日期落到 1970 年。
```

---

## 十、Claude 刻意未修的既有 bug

`t3` 發現但未修改：

```text
getUserStats 中 studyMinutes 統計語法有誤。
MySQL / SQLite 兩種 DB 可能都回傳 0。
```

這是既有業務邏輯 bug，不屬於本輪 SQLite 相容性最小修補範圍。

正確處理方式：

```text
另開下一輪任務。
不要混入本次 SQLite compatibility commit。
```

---

## 十一、Agent 筆記與備份

`.agent-notes/` 目前有：

```text
t1-analysis.md      約 4.4 KB
t1-stats-fix.md     約 2.6 KB
```

已知備份位置：

```bash
~/project/ai-dispatch/logs/
```

先前已備份：

```text
dispatch_interrupted_20260610_144658.diff
agent-notes_interrupted_20260610_144821/
```

目前最新 smartBookRouter.ts / stats.ts 變更也已由 Antigravity 回報備份至：

```bash
~/project/ai-dispatch/logs/
```

---

## 十二、換分頁後優先執行步驟

### Step 1：先確認狀態

```bash
cd ~/project/smartbook-lite-rc1-ai-dispatch-test

git status --short
git diff --stat
git diff -- server/routers/smartBookRouter.ts server/stats.ts
```

預期只應該看到：

```text
M server/routers/smartBookRouter.ts
M server/stats.ts
```

如果還有：

```text
?? .agent-notes/
?? tmp_t3.json
```

先不要 commit。

---

### Step 2：清掉不該 commit 的暫存檔

```bash
cd ~/project/smartbook-lite-rc1-ai-dispatch-test

rm -f tmp_t3.json

mkdir -p ~/project/ai-dispatch/logs/agent-notes_final_$(date +%Y%m%d_%H%M%S)
cp -a .agent-notes/* ~/project/ai-dispatch/logs/agent-notes_final_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
rm -rf .agent-notes

git status --short
git diff --stat
```

理想狀態：

```text
M server/routers/smartBookRouter.ts
M server/stats.ts
```

---

### Step 3：再次 build 驗證

```bash
cd ~/project/smartbook-lite-rc1-ai-dispatch-test

pnpm build
```

成功後再往下。

---

### Step 4：補 SQLite runtime smoke

`pnpm build` 只能代表 TypeScript / bundling OK，不能完全代表 SQLite runtime OK。

先查 package scripts：

```bash
cat package.json | grep -n "sqlite\|db:"
```

若存在 fresh sqlite schema script，可跑：

```bash
SMOKE_DB="/tmp/smartbook-ai-dispatch-smoke-$(date +%s).db"

DATABASE_PROVIDER=sqlite \
SQLITE_PATH="$SMOKE_DB" \
pnpm run db:sqlite:push:fresh
```

如果 script 不存在，不要硬改；先回報 package scripts。

---

### Step 5：備份最終 diff

```bash
cd ~/project/smartbook-lite-rc1-ai-dispatch-test

mkdir -p ~/project/ai-dispatch/logs

git diff -- server/routers/smartBookRouter.ts server/stats.ts \
  > ~/project/ai-dispatch/logs/final_sqlite_compat_patch_$(date +%Y%m%d_%H%M%S).diff
```

---

### Step 6：commit 到測試分支

前提：

```text
1. 只剩 server/routers/smartBookRouter.ts 與 server/stats.ts 修改。
2. pnpm build 通過。
3. SQLite smoke 至少已嘗試，若無 script 要記錄原因。
4. .agent-notes/ 與 tmp_t3.json 不可 commit。
```

commit：

```bash
cd ~/project/smartbook-lite-rc1-ai-dispatch-test

git add server/routers/smartBookRouter.ts server/stats.ts
git commit -m "fix: improve sqlite compatibility for smartbook stats"
```

push：

```bash
git push -u origin "$(git branch --show-current)"
```

先不要直接 merge 到 `release/vps-lite`。

---

## 十三、下一個建議任務：驗收 / 報告，不急著修 studyMinutes

下一輪不建議馬上修 `studyMinutes`。

建議先跑 verify-only 任務，整理報告：

```json
{
  "tasks": [
    {
      "id": "v1",
      "agent": "codex",
      "file": "server/routers/smartBookRouter.ts",
      "deps": [],
      "task": "Review the current diff in server/routers/smartBookRouter.ts. Verify that the INSERT IGNORE replacement preserves MySQL behavior while avoiding SQLite-only incompatibility. Do not modify code unless a clear runtime bug is found. Run pnpm build."
    },
    {
      "id": "v2",
      "agent": "claude",
      "file": "server/stats.ts",
      "deps": [],
      "task": "Review the current diff in server/stats.ts. Focus on SQLite timestamp seconds vs MySQL Date/string compatibility in getUserStats and chart grouping. Do not fix unrelated studyMinutes bug. Run pnpm build."
    },
    {
      "id": "v3",
      "agent": "codex",
      "file": "server/stats.ts",
      "deps": ["v1", "v2"],
      "task": "Create a concise verification report in docs/project/sqlite/AI_DISPATCH_SQLITE_COMPAT_VERIFY.md summarizing changed files, build result, known non-goals, and follow-up issue for studyMinutes. Do not modify application logic."
    }
  ]
}
```

---

## 十四、Codex / Claude 權限選擇原則

### 可以選 1 Yes，但不要永久允許

```text
git status --short
git diff --stat
git diff file
bash -n script.sh
pnpm build
cat package.json | grep ...
tail/head log
```

### 需要小心，只能確認後一次性允許

```text
rm -rf .agent-notes
rm -f tmp_t3.json
git add / commit / push
pnpm install
```

### 不建議永久允許

```text
git push
git reset --hard
git clean -fd
rm -rf
sudo
docker compose down
kill -9
```

---

## 十五、目前結論

本輪已完成：

```text
ChatGPT 產生任務設計 ✅
GitHub ai-dispatch-handoff-private 作為任務交換區 ✅
E500 本機 runner 執行 ✅
AGY / Codex / Claude 多 Agent 串接 ✅
stdin isolation 修復 ✅
AGY writable HOME / XDG 修復 ✅
AGY_TIMEOUT timeout guard 修復 ✅
fail-fast deps skip 修復 ✅
node_modules / vite 環境修復 ✅
pnpm build 通過 ✅
SmartBook SQLite compatibility patch 產生 ✅
```

目前下一分頁最重要工作：

```text
1. 檢查 diff。
2. 清掉 .agent-notes 與 tmp_t3.json。
3. 再跑 pnpm build。
4. 補 SQLite runtime smoke。
5. 備份 final diff。
6. commit 測試分支。
7. push 並準備 PR。
8. studyMinutes 另開新任務，不混入本 commit。
```

---

## 十六、換分頁起始提示詞

可在新分頁直接貼以下提示詞：

```text
請接續 2026-06-10 AI Dispatch 多 Agent 全自動化流程。

目前 E500 上已完成：
- ai-dispatch-handoff-private 任務交換 repo
- run-tasks-multi-agent.sh 可呼叫 AGY / Codex / Claude
- 已修 stdin isolation、AGY writable HOME/XDG、AGY_TIMEOUT、fail-fast deps skip
- SmartBook 測試 worktree 已補 node_modules，vite OK，pnpm build OK
- multi-agent 已跑通 t1 AGY、t2 Codex、t3 Claude
- 目前變更集中在：
  - server/routers/smartBookRouter.ts
  - server/stats.ts
- 未追蹤檔可能有：
  - .agent-notes/
  - tmp_t3.json

請先不要 merge。
請依序協助我：
1. 檢查 git status / diff。
2. 清掉不該 commit 的 .agent-notes 與 tmp_t3.json，必要時先備份。
3. 再跑 pnpm build。
4. 補 SQLite runtime smoke。
5. 備份 final diff。
6. 若合理，只 commit server/routers/smartBookRouter.ts 與 server/stats.ts 到測試分支。
7. push 測試分支並準備 PR。
8. studyMinutes 既有 bug 另開任務，不混入本次 commit。
```
