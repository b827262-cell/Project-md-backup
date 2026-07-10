# SecMon MVP 實作與部署計畫

## 1. MVP 範圍

第一階段目標是在單台 Ubuntu 24.04 Linux 主機上完成可驗證的資安偵測閉環：

```text
日誌來源 → 事件解析 → SQLite → 攻擊者彙總 → Web 查詢 → 人工封鎖 → 稽核紀錄
```

第一版不追求完整 SIEM，而是先完成下列必要能力：

1. SSH 失敗登入與無效帳號偵測。
2. Nginx 敏感路徑、掃描與常見 Web 攻擊特徵偵測。
3. Suricata EVE JSON 告警匯入。
4. 攻擊 IP、事件次數、最後出現時間與威脅分數彙總。
5. Web Dashboard、攻擊者、事件、封鎖及白名單頁面。
6. 以 nftables 執行人工限時封鎖。
7. 所有管理操作保存 audit log。

## 2. 建議專案結構

```text
secmon/
├── backend/
│   ├── app.py
│   ├── api/
│   │   ├── dashboard.py
│   │   ├── attackers.py
│   │   ├── events.py
│   │   ├── alerts.py
│   │   ├── blocks.py
│   │   └── admin.py
│   ├── collectors/
│   │   ├── ssh_journal.py
│   │   ├── nginx_file.py
│   │   ├── suricata_file.py
│   │   └── crowdsec.py
│   ├── parsers/
│   │   ├── ssh.py
│   │   ├── nginx.py
│   │   └── suricata.py
│   ├── services/
│   │   ├── event_service.py
│   │   ├── threat_engine.py
│   │   ├── allowlist.py
│   │   ├── blocker.py
│   │   └── audit.py
│   ├── repositories/
│   └── security/
├── frontend/
├── database/
│   ├── schema.sql
│   ├── seed.sql
│   └── migrations/
├── scripts/
│   ├── backup.sh
│   ├── cleanup.sh
│   └── healthcheck.sh
├── systemd/
│   ├── secmon-api.service
│   ├── secmon-collector.service
│   ├── secmon-expiry.service
│   └── secmon-expiry.timer
├── config/
├── tests/
└── docs/
```

## 3. 元件責任

### Collector

- 以唯讀方式取得來源資料。
- 保存 offset、cursor 或最後讀取位置。
- Collector 重啟後能繼續讀取，不遺失也不大量重複。
- 將原始資料交給 Parser，不直接進行封鎖。

### Parser

輸出統一事件：

```json
{
  "detected_at": "2026-07-10T06:23:11Z",
  "sensor_host": "secmon-server",
  "source_type": "ssh",
  "src_ip": "185.220.101.42",
  "src_port": 51234,
  "dst_ip": "10.0.0.12",
  "dst_port": 22,
  "protocol": "tcp",
  "attack_type": "invalid_user",
  "severity": 3,
  "signature": "SSH invalid user",
  "username": "admin",
  "raw_log": "..."
}
```

Parser 必須：

- 驗證 IP 與 Port。
- 限制單筆原始日誌長度。
- 對格式不符事件記錄解析錯誤，不讓 Collector 崩潰。
- 不執行 shell 指令。

### Threat Engine

- 產生 `event_key` 並去重。
- 更新 `attackers` 彙總。
- 依規則的時間窗口統計事件。
- 建立告警與調整攻擊者狀態。
- 封鎖前檢查白名單及安全保護清單。

### Blocker

- 接受已驗證的 IP、原因與期限。
- 使用 nftables set，不為每個 IP 建立獨立 rule。
- 寫入封鎖歷史及同步狀態。
- 定期解除到期 IP。
- 對 nftables 失敗進行重試與告警。

## 4. SSH 偵測

### 來源

```bash
journalctl -u ssh.service -o json --follow
```

建議使用 systemd journal cursor 保存讀取位置，不以時間字串作為唯一進度依據。

### 基本事件

- `Failed password`
- `Invalid user`
- `authentication failure`
- 同 IP 短時間大量嘗試不同帳號

### 初始規則

| 規則 | 時間窗口 | 次數 | 結果 |
|---|---:|---:|---|
| 無效帳號嘗試 | 10 分鐘 | 5 | 建立中風險告警 |
| SSH 暴力破解 | 10 分鐘 | 10 | 建立高風險告警 |
| 持續暴力破解 | 1 小時 | 30 | 建議封鎖 4 小時 |

MVP 初期只顯示建議封鎖，由 Analyst 人工確認。

## 5. Nginx 偵測

### 來源

```text
/var/log/nginx/access.log
```

正式環境建議使用 JSON access log，避免 Combined Log Format 中引號、空白及代理欄位造成解析錯誤。

### 基本特徵

- `/.env`
- `/wp-login.php`
- `/xmlrpc.php`
- `/phpmyadmin`
- `/vendor/phpunit`
- `/cgi-bin/`
- `../`、`%2e%2e`
- `/etc/passwd`
- 常見 SQL Injection pattern

注意：單一 404 不等同攻擊。規則需同時考慮頻率、敏感路徑及狀態碼。

若位於 Cloudflare、Load Balancer 或 Reverse Proxy 後方，僅可信任明確設定的代理網段提供 Real IP Header。

## 6. Suricata 匯入

### 來源

```text
/var/log/suricata/eve.json
```

只處理 `event_type = alert` 的 MVP 告警，保存：

- timestamp
- src_ip / src_port
- dest_ip / dest_port
- proto
- alert.signature
- alert.category
- alert.severity
- flow_id

Suricata severity 與 SecMon severity 的映射需集中管理，不應散落在 Parser 中。

## 7. nftables 設計

建立專用 table 與 set：

```nft
 table inet secmon {
     set blocked_ipv4 {
         type ipv4_addr
         flags timeout
     }

     set blocked_ipv6 {
         type ipv6_addr
         flags timeout
     }

     chain input {
         type filter hook input priority filter; policy accept;
         ip saddr @blocked_ipv4 drop
         ip6 saddr @blocked_ipv6 drop
     }
 }
```

實際部署前必須確認不與既有 firewalld、ufw、Docker 或公司 nftables 規則衝突。

禁止提供任意 shell 字串給 Blocker。建議優先使用 Python netlink library；若使用受控 helper，sudoers 僅允許固定 executable，不允許 `sh -c`。

## 8. 白名單與保護清單

部署前至少加入：

- `127.0.0.0/8`
- `::1/128`
- 公司內部網段
- 公司 VPN 出口
- 維運人員固定 IP
- 監控與備份主機
- Reverse Proxy / Load Balancer
- 預設閘道及 DNS 等必要基礎設施

白名單需同時支援 IPv4、IPv6 與 CIDR。

## 9. systemd 服務

### API

```ini
[Unit]
Description=SecMon API
After=network.target

[Service]
User=secmon
Group=secmon
WorkingDirectory=/opt/secmon
EnvironmentFile=/etc/secmon/secmon.env
ExecStart=/opt/secmon/.venv/bin/uvicorn backend.app:app --host 127.0.0.1 --port 8080
Restart=on-failure
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/secmon /var/log/secmon

[Install]
WantedBy=multi-user.target
```

### Collector

Collector 需額外取得 journal 或日誌檔案讀取權限，但不應取得 nftables 修改權限。

### 到期解除 Timer

每分鐘檢查 `blocked_ips.active = 1` 且已到期紀錄，先同步 nftables，再更新資料庫。

## 10. API 安全

- API 僅綁定 localhost，由 Nginx TLS reverse proxy 對外提供。
- 使用公司內部帳號、OIDC 或至少安全 Session 認證。
- 密碼使用 Argon2id 或 bcrypt。
- 登入、封鎖、白名單及設定 API 實施 rate limiting。
- 使用 RBAC 檢查每個管理操作。
- 對所有輸入使用 schema validation。
- 原始日誌、URL 與 User-Agent 顯示前進行 escaping。
- CSV 匯出對 `=`, `+`, `-`, `@` 開頭的欄位做公式注入防護。
- 不在日誌中記錄密碼、Session、Token 或完整 Authorization Header。

## 11. 開發階段

### Phase 0：基礎骨架

- 建立 repository 結構。
- 建立 SQLite schema 與 migration 機制。
- 建立設定載入、結構化日誌與健康檢查。
- 建立 CI：lint、type check、unit test。

### Phase 1：SSH 到 SQLite

- 實作 SSH Collector 與 Parser。
- 實作事件去重及 attackers UPSERT。
- 完成 CLI 攻擊 IP 排名。
- 建立測試 fixture，禁止以真實攻擊公共 IP 作為必要測試資料。

### Phase 2：Web 查詢

- 實作 Dashboard、Attackers、Events API。
- 建立 React Dashboard、攻擊者列表與事件頁。
- 加入分頁、篩選、錯誤狀態與 loading state。

### Phase 3：Nginx 與 Suricata

- 實作 JSON Nginx Parser。
- 實作 Suricata EVE Parser。
- 加入來源健康狀態與解析錯誤統計。

### Phase 4：封鎖與稽核

- 建立 nftables 專用 set。
- 實作人工限時封鎖與解除。
- 實作白名單與安全保護清單。
- 建立 audit log。

### Phase 5：自動封鎖試運轉

- 先執行 dry-run，只顯示「若啟用將封鎖哪些 IP」。
- 至少觀察 7～14 天誤判率。
- 經公司核准後，僅對高可信規則開啟自動封鎖。

## 12. 測試策略

### Unit tests

- SSH、Nginx、Suricata 正常及異常格式。
- IPv4、IPv6、CIDR 驗證。
- event_key 穩定性與去重。
- threat score 與時間窗口。
- 白名單命中與未命中。

### Integration tests

- Collector 重啟後從 cursor 繼續。
- SQLite WAL 下 API 查詢與 Collector 寫入並行。
- 封鎖建立、到期與解除同步。
- 作用中封鎖唯一索引。
- audit log 完整性。

### Security tests

- XSS payload 出現在 URL、username、User-Agent、raw_log。
- SQL Injection query parameters。
- CSV formula injection。
- 未授權 Viewer 執行封鎖。
- 偽造 `X-Forwarded-For`。
- 惡意 IP 字串嘗試 shell injection。

## 13. MVP 驗收清單

- [ ] SSH 失敗登入能在 30 秒內出現在事件頁。
- [ ] 同一事件重讀不會重複累計。
- [ ] 攻擊者彙總與事件明細數量一致。
- [ ] Dashboard 可切換 1h、24h、7d。
- [ ] 可依 IP、類型、嚴重度及時間查詢。
- [ ] 白名單 IP 無法被人工或自動封鎖。
- [ ] 人工封鎖成功後 nftables 與 SQLite 狀態一致。
- [ ] 封鎖到期後能自動解除。
- [ ] 每次管理操作都有使用者、時間、來源 IP、舊值與新值。
- [ ] SQLite 可完成每日一致性備份與 quick_check。
- [ ] Collector、API、Suricata 任一異常可在健康頁辨識。

## 14. 建議上線順序

1. 測試環境只蒐集、不封鎖。
2. 確認 Real IP、時間、時區與來源解析正確。
3. 建立並審核白名單。
4. 上線人工封鎖。
5. 進行 dry-run 自動判定。
6. 只開啟高可信、低誤判的自動封鎖規則。
7. 建立備份、回復、解除誤封及緊急停用 SOP。

## 15. 未來演進

- 多台 Linux Agent 與中央接收 API。
- PostgreSQL、訊息佇列與高可用部署。
- GeoIP、ASN 與威脅情報 enrichment。
- Email、Slack、Telegram 通知。
- OIDC、LDAP、SSO。
- PDF 稽核報表。
- 與 Wazuh、OpenSearch、Grafana 或既有 SOC 平台整合。
