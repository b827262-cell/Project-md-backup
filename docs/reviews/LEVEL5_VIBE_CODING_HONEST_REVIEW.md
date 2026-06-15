---
date: 2026-06-15
version: 2026.06.15-1517
source: claude.ai chat
status: Current Truth
---

# Level 5 Vibe Coding 觀念誠實審視

> 審視角度:資深 AI 工程顧問 / 軟體架構師 / 技術審查者
> 立場:高標準、誠實、可落地,不迎合。
> 日期:2026-06-15

---

## 核心結論

這套東西的骨架是對的,但有一個內在矛盾:在 C-3 題已點出「Reviewer / Security / QA Agent 可能只是形式化」這個病,而整套七角色架構正是這個病的高發區。**診斷出了病,卻把病設計進了結構裡。**

---

## A. 正確性檢查

### 真正正確、且是 Level 5 核心
- 「AI 開發不是聊天,而是流程工程」——唯一真正的分水嶺,其餘九條都是它的展開。
- **需求契約化(PRD 即驗收合約)**——ROI 最高的一條。只能留一條就留這條。
- Context Engineering / 明確邊界——正確且被低估。
- 「驗收看證據不看畫面」——正確。
- 「人負責目標與風險」的分工精神——正確。

### 太理想化 / 口號成分高
- **「沒有 PRD,不開工」**:對探索性任務是錯的。正確版本是分級——高風險/不可逆任務強制 PRD;探索性任務允許先 spike、事後補規格。
- **「同一個 AI 不應同時當作者與審查者」**:方向對,但獨立性的本質是**資訊獨立與誘因獨立**,不是物理上換一隻模型。同模型開全新 context + 對抗性指令可拿到 ~80% 價值。換七隻模型邊際遞減,成本/延遲/交接噪音遞增。
- **「模型不是重點,流程才是重點」**:半對。流程降低**變異**,但不能取代**理解**。講過頭會變成「把理解外包掉」的藉口。

### 需要更精準定義
- Reviewer Agent「找風險」——找什麼?LLM 抓得到 lint 級、明顯邏輯級;抓不到權限邏輯錯、業務邏輯漏洞、競態。
- 「test 通過」——哪一層的 test?(見 D 節)

---

## B. 工程實務檢查

這份文件的「預設體型」是一個真正的團隊,對小專案明顯過重。

| 規模 | 一定不能省 | 可以砍 |
|---|---|---|
| 一人開發 | PRD(哪怕三行)、Git diff review、邊界限制、backup-before-migration、build+**runtime smoke** | 多 agent 分工、release note 流程、獨立 Security Agent;Reviewer 用「換 context 自審」 |
| 2–3 人 | 上述 + 真人 code review(高風險路徑)、PR 流程、audit log | 七角色拆分仍嫌重;PM/Architect/QA 合併成「規格+風險」一步 |
| 正式團隊 | 全部 + observability、incident runbook、on-call、migration 排演 | 幾乎不能砍,靠 risk-tiering 控成本 |

正式產品不能省的四項:可回滾的 migration 策略、權限/auth 的**人工**審查、backup **且驗證過 restore**、上線後錯誤可觀測。

**成本維度在整份文件幾乎缺席**:對 🟢 低風險任務還跑七角色鏈,經濟上荒謬。記憶裡的 🔴🟡🟢 risk-tiered routing 才是讓這套落地的關鍵,但在文件裡被埋得太淺。

---

## C. AI Agent 實務檢查

多 agent 只在兩個邊界上有效:**人/AI 邊界**與**作者/審查邊界**。其餘拆分多在製造「看起來專業、沒人驗證」的文件。

### 何時多 agent 反成噪音
- 任務小、風險低:鏈越長,交接出錯點越多,品質提升趨近於零。
- 下游 agent 沒有獨立事實來源去否決上游時,它只會複述,不會挑戰。

### 怎麼避免形式化(最該解的題)
1. **給獨立事實來源**,不要只餵上游產出。Security Agent 要直接讀 schema、auth middleware 原始碼。
2. **要求可否證的具體斷言**,不收「LGTM / 看起來安全」。強制格式:「第 X 行 `requireAdmin` 在 Y 路由缺失」。
3. **LLM 的 security review 是 filter,不是 gate。** 它會幻覺式批准。auth 邏輯、權限邊界、不可逆操作必須真人簽核。信任「AI 安全閘門」的安全框架還不到 production 級。
4. **AI 寫的測試會測「程式現在做了什麼」,不是「應該做什麼」**——同源、假信心。關鍵路徑驗收測試要真人寫,或用對抗性框架另開 context 生成。

### Agent 交接文件
最小可用:`{變更檔案清單, 變更意圖, 已知風險, 未覆蓋的測試, 需人工確認項}`。**「未覆蓋/不確定」欄位強制填**,否則大家只填「已完成」就死於形式化。

---

## D. Production 風險檢查

這份流程**還不足以支撐正式上線**。

### 最大缺口:Migration 安全
文件只說「先提出計畫,不得直接執行」——太輕。Migration 是 AI 造成**不可逆**災難的頭號現場,必須:可逆(或 expand→migrate→contract)、先備份再執行、在 staging/資料副本排演過。

### 親身案例(可直接教學)
Drizzle `.defaultNow()` 在 SQLite emit `(now())` 會炸,grep 審計給假 all-clear,`pnpm build` 過了也不代表 runtime 安全。但文件的「技術驗收」欄寫的正是 `build 通過 / lint 通過 / test 通過 / 無 TS error`——**這四項全綠時,那個 bug 一樣會在 production 第一次 INSERT 炸。框架在這格寫的,正是自己被燒過的假信心陷阱。**

修法:**verify 欄位必須是 runtime smoke insert/select,不是 type-check。**

### 還缺的 Production 必備項

| 缺項 | 為什麼非有不可 |
|---|---|
| Observability | 結構化 log + 錯誤率 metric + 至少一條告警。否則「監控」只是口號 |
| Backup + 驗證過的 restore | 有備份不算數,**還原演練過**才算數。對 SQLite 遷移尤其致命 |
| Incident response / runbook | 出事時固定動作:誰、怎麼回滾、怎麼通知 |
| 供應鏈 | AI 會幻覺出不存在的 npm 套件(slopsquatting),新增依賴要審 |
| Secret 生命週期 | 不只「別放前端」,還有輪替、外洩後撤換 |

### SLO / error budget:現在不要
closed beta、單台 1GB VPS 上它是 cargo-culting Google SRE。先有 backup-restore 演練和一條告警,遠比 SLO 重要。

### 部署情境差異
- **Firebase**:風險中心是 security rules。控管 = rules 測試 + emulator。
- **Vercel**:無狀態好回滾(改 alias),風險在 env vars 與 serverless secret 注入。
- **VPS / Docker(你的情境)**:回滾最難、狀態在你身上。image tag 不用 `latest`、compose 版本化、process 級健康檢查、**DB 在主機 → migration 與 backup 是最高風險**。

---

## E. 個人能力評估

定位:**orchestration / tooling 已是紮實的 Level 4+**(多 agent dispatcher、AUTO_SOURCE_PACK、flock 序列化、Stop hook `decision:block`、語言分層治理)。短板不在「會不會調度 AI」。

### 離 Level 5 還缺
1. Runtime 驗證的深度(不是 build,是真的跑起來測)。
2. Production 可觀測性與事故處理。
3. 「何時不用重流程」的判斷——成熟度體現在減法。

### 最該先補三項
1. **Runtime / migration 驗證**:smoke insert/select 進 verify;migration 先在資料副本排演。與 SQLite P0 同一件事,槓桿最大。
2. **Observability + restore 演練**:一條錯誤率告警 + 一次真的還原 backup。
3. **治理減法**:砍掉產生「文件劇場」的 agent,留作者/審查、人/AI 兩個有獨立事實來源的邊界。

### 不用急著補
更多 agent、更多模型、更多治理 MD、SLO/error budget 形式化——已過剩。

### 當講師 / AI PM 顧問
最大職業風險是**教成儀式**。checklist 在沒有疤痕的人手上,只會教出「照拜流程、照樣上線漏洞」的學生。你的不對稱優勢是踩過真坑(grep 假 all-clear、build≠runtime)。教學核心應是**讓學生看見失敗模式與判斷**,能 demo 真實 before/after、回滾、事故,比任何完整框架值錢。

---

## F. 評分(1–10,不灌水)

| 項目 | 分數 | 理由 |
|---|---|---|
| 觀念完整度 | 7.5 | 覆蓋大半地圖,缺 observability / IR / migration 安全 / 成本維度 |
| 工程落地性 | 6 | 原文照做偏重;成敗繫於被埋淺的 risk-tiering,絕對化鐵律扣分 |
| Production 安全性 | 5.5 | auth/secret/audit 直覺好,但「LLM 當安全閘門」不安全、migration 安全太薄、無 restore 演練 |
| 小型團隊實用性 | 5 | 不大砍就過重;為真團隊設計的體型 |
| 職訓可教性 | 7 | 結構好教,有「教成儀式」風險 |
| 到 Level 5 可行性 | 8 | 很近;調度功底已具備,缺口具體可解 |

---

## 一句誠實總結

**最大價值**:把「AI 寫程式」正確重構成「流程工程」,且 PRD 契約化、邊界控制、證據式驗收三招是真功夫。

**最大盲點**:這套東西能製造出「可控」的**感覺**,不一定帶來「可控」的**實質**——agent 與治理文件加得越多,把「儀式」誤認成「安全」的表面積越大。自己的疤痕(grep 假 all-clear、build 過了 runtime 照炸)正是鐵證:**任何沒有錨定在 runtime 證據上的流程與自動化,都會對你說謊。**

**下一步最該做的一件事**:把 verify 從 type-check 升級成 **runtime smoke(insert/select)**,並做**一次真正的 backup → restore 演練**。先讓流程說真話,再談擴張。
