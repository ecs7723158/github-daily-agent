# 🚀 Autonomous GitHub Daily Sideproject Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![GCP Always Free](https://img.shields.io/badge/GCP-Always%20Free%20Tier-4285F4.svg?logo=google-cloud&logoColor=white)](https://cloud.google.com/free)
[![Kubernetes Ready](https://img.shields.io/badge/Kubernetes-Cloud%20Native-326CE5.svg?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Zero Disk GitOps](https://img.shields.io/badge/GitOps-Zero%20Clone%20Overhead-F05032.svg?logo=git&logoColor=white)](https://git-scm.com/)

每天中午 12:00 (Asia/Taipei) 自動巡邏開源技術雷達，即時鎖定 **GitHub Trending 當日星星數漲幅最大的 Top 5 專案**，涵蓋 **AI 生態系 (LLM / Agent / Reasoning / Vision)、Kubernetes (K8s) 與 DevOps**。  
全自動完成**深度架構剖析 (RESEARCH_NOTES.md)**、**無磁碟克隆負擔的遠端 Fork & Branch Commit**、**自動建立 Tracking Issue**，並同步至**本地 Obsidian Vault** 與**雲端 Notion 知識庫**。

---

## 🏗️ 系統架構拓撲圖 (End-to-End System Architecture)

```mermaid
graph TB
    subgraph DataSources["🌐 趨勢情報與候選池 (Trend Intelligence)"]
        GH_Trend["GitHub Trending Daily<br/>(即時解析每日星星暴增榜)"]
        GH_API["GitHub Search API<br/>(AI, K8s, DevOps 領域檢索)"]
        HF_API["Hugging Face API<br/>(熱門模型與 Spaces)"]
    end

    subgraph CoreEngine["⚙️ 核心自動化大腦 (Daily Sideproject Agent)"]
        Scraper["1. 趨勢抓取模組 (TrendScraper)<br/>多源聚合、去重、中繼資料擴展"]
        Analyzer["2. 分析決策模組 (ProjectAnalyzer)<br/>雙軌權重計分 + 星星暴增破格機制 (>=300)"]
        LLM_Fallback{"架構剖析引擎選擇"}
        Gemini["Gemini API 深度推論<br/>(1.5 Flash / 2.5 Flash)"]
        ExpertEngine["專家架構模板引擎<br/>(K8s Spec, GitOps, MCP Agent 拓撲)"]
    end

    subgraph GitOps["🐙 自動化 Git 模組 (GitAutomator)"]
        Fork["REST API Remote Fork<br/>(免 Clone 本地磁碟 0 耗損)"]
        Branch["建立研究分支<br/>research/arch-analysis-YYYYMMDD"]
        Commit["遠端 Commit RESEARCH_NOTES.md<br/>(目標導向 Commit 訊息)"]
        Issue["自動建立研究追蹤 Issue<br/>(Issue #ID 關聯記錄)"]
    end

    subgraph KnowledgeSync["📚 雙向知識庫同步 (KnowledgeSyncer)"]
        Obsidian["Obsidian Vault 同步<br/>YAML Frontmatter + 技術架構拆解"]
        Notion["Notion 雲端資料庫同步<br/>分批 Block 寫入與屬性標記"]
    end

    GH_Trend --> Scraper
    GH_API --> Scraper
    HF_API --> Scraper

    Scraper --> Analyzer
    Analyzer --> LLM_Fallback
    LLM_Fallback -- "API 金鑰可用" --> Gemini
    LLM_Fallback -- "額度不足 / 降級" --> ExpertEngine

    Gemini --> GitOps
    ExpertEngine --> GitOps

    GitOps --> Fork --> Branch --> Commit --> Issue
    Commit --> KnowledgeSync
    KnowledgeSync --> Obsidian
    KnowledgeSync --> Notion
```

---

## 🔒 零信任安全架構 (Zero-Trust Security Framework)

本專案實施嚴格的安全防護生命週期，防止任何 API 金鑰（Gemini API Key、GitHub Token、Notion Key）外洩至代碼庫或命令日誌中。

```mermaid
sequenceDiagram
    autonumber
    actor Developer as 開發者 (MacBook)
    participant Script as deploy_secrets.sh
    participant LocalEnv as 本機 .env (chmod 600)
    participant IAP as GCP IAP 隧道
    participant RemoteVM as GCP VM (hybrid-cloud-node)

    Developer->>Script: 啟動安全部署腳本
    Script->>Script: 驗證 .gitignore 是否包含 .env
    Script->>Developer: read -s 提示輸入 GEMINI_API_KEY (密碼無顯模式)
    Developer-->>Script: 貼上金鑰 (不留存於 shell history)
    Script->>LocalEnv: 寫入本機 .env 並執行 chmod 600
    Note over LocalEnv: 僅目前使用者可讀寫，防禦本機側錄
    Script->>IAP: 透過 gcloud compute scp 走 IAP 加密通道傳輸
    IAP->>RemoteVM: 寫入 ~/github-daily-agent/.env
    Script->>RemoteVM: 透過 gcloud ssh 強制設定遠端 .env 為 chmod 600
    Script-->>Developer: 安全部署完成 (零外洩、零歷史記錄)
```

### 資安規範五大保證
1. **輸入無顯性**：採用 Bash `read -s`，輸入金鑰時不產生任何字符反射。
2. **本機最小權限**：本機 `.env` 檔案強制鎖定為 `600` (`-rw-------`)。
3. **雲端跳板隔離**：GCP VM 不開放外部公網 IP，僅透過 Google Identity-Aware Proxy (IAP) 安全隧道進行加密傳輸。
4. **遠端權限防禦**：VM 端 `.env` 檔案同樣強制鎖定為 `600`。
5. **代碼防護機制**：`.gitignore` 內建完整排除規則（排除 `.env*`、`*.pem`、`*.key`、`*serviceaccount*.json`、`*.log`）。

---

## 📊 決策矩陣與評分邏輯 (Decision Matrix & Viral Boost)

```mermaid
flowchart TD
    Start["候選專案流入 (GitHub Trending + Search + HuggingFace)"] --> PreCheck{"是否符合 GitHub 開源專案?"}
    PreCheck -- 否 --> Skip["跳過 HuggingFace 純 Model 資產"]
    PreCheck -- 是 --> CalcScore["計算領域得分 (Domain Weights)"]

    subgraph Weights["領域加權權重 (Domain Matrix)"]
        W1["AI Ecosystem (3.8x)<br/>LLM, Agent, DeepSeek, Claude, vLLM, ComfyUI"]
        W2["Kubernetes (3.5x)<br/>Helm, Operator, CRD, Cilium, Istio, CNI"]
        W3["DevOps (3.2x)<br/>CI/CD, Terraform, ArgoCD, Prometheus, Docker"]
    end

    CalcScore --> BoostCheck{"檢查今日星數漲幅 (stars_today)"}
    BoostCheck -- "stars_today >= 300" --> ViralBoost["🔥 注入爆款加速器 (+25.0 突破加分)"]
    BoostCheck -- "stars_today < 300" --> PopBoost["標準對數熱度加分"]

    ViralBoost --> RankFormula["最終排序權重: (stars_today * 2) + TotalScore"]
    PopBoost --> RankFormula

    RankFormula --> TopK["選取 Top 5 優勝專案"]
    TopK --> Tagging{"領域精確標籤判別"}
    Tagging -- "命中 AI 關鍵字" --> TagAI["ai_ecosystem"]
    Tagging -- "命中 K8s 關鍵字" --> TagK8s["k8s"]
    Tagging -- "命中 DevOps 關鍵字" --> TagDevOps["devops"]
    Tagging -- "跨領域爆款神作" --> TagViral["viral_trending"]
```

---

## ☁️ GCP 混合雲永久免費 VM 部署 (hybrid-cloud-node)

本系統部署於 Google Cloud Platform 官方 **Always Free Tier** 之虛擬機器中，實現 **$0/月** 的全天候無人值守運作。

| 項目 | 配置規格 |
|---|---|
| **機器類型** | `e2-micro` (2 vCPUs, 1 GB 記憶體) |
| **部署地區** | `us-central1-a` (包含在 GCP 免費額度內) |
| **磁碟規格** | 30 GB 標準 Persistent Disk (免費額度支援至 30GB) |
| **作業系統** | Ubuntu 22.04 LTS |
| **時區配置** | `Asia/Taipei` (CST, UTC+8) |
| **網路存取** | Google Cloud IAP 專屬通道 (無公網 IP 曝露，極致資安) |

### 遠端 VM Crontab 自動排程
每日中午 12:00 準時自動執行：
```cron
# GCP VM 每日中午 12:00 自動執行
0 12 * * * /home/yi-fanshan/github-daily-agent/run_daily.sh
```

---

## 📈 GCP 服務可視化與可觀測性指南 (Observability & Visualization)

針對 GCP 基礎設施與自動化工作流程的可視化，推薦採用以下最佳實踐：

### 1. 雲端架構圖自動化生成 (Architecture as Code)
* **[Diagrams (Python Library)](https://diagrams.mingrammer.com/)**：
  強烈推薦採用「架構即代碼 (Diagrams-as-Code)」。直接透過 Python 撰寫架構宣告，能在每次 CI/CD 或版本發布時自動渲染出清晰高畫質的 SVG/PNG 拓撲圖。
* **[Hava.io](https://www.hava.io) / [Lucidscale](https://lucid.co/lucidscale)**：
  透過 GCP Service Account API 自動探測真實運行的雲端資源，自動繪製即時拓撲並追蹤架構變更歷程。

### 2. 指標監控：Google Cloud Monitoring vs. Prometheus vs. Grafana

> [!CAUTION]
> **重要架構避坑提醒 (OOM Prevention)**：  
> 當前 GCP 節點為 `e2-micro` (1 GB RAM)。**嚴禁在 VM 本機同時自建運行 Prometheus Server 與 Grafana 實例**，否則極易導致記憶體耗盡 (OOM) 造成 VM 當機！

| 方案維度 | 方案 A：GCP 原生 Cloud Monitoring | 方案 B：Google Managed Prometheus (GMP) | 方案 C：Grafana Cloud 外部整合 |
|---|---|---|---|
| **記憶體負載** | 幾乎為 0 (由 GCP 底層收集) | 超輕量 (僅代管採集) | 0 (使用 Grafana 託管 SaaS) |
| **費用** | **免費** (涵蓋在 GCP 基本配額內) | 基本指標免費 | **免費** (Grafana Free 10k 序列) |
| **配置難度** | ⭐ (開箱即用) | ⭐⭐⭐ (需配置 PromQL) | ⭐⭐ (設定 GCP 服務帳號 Data Source) |
| **視覺化效果** | 實用簡潔，內建 VM 監控看板 | 依賴外部查詢介面 | **極度精美，深色系儀表板首選** |

**💡 推薦落地策略**：
1. **短期最速**：直接於 GCP Console 啟用 **Cloud Monitoring Dashboard**，追蹤 `e2-micro` 的 CPU 峰值、記憶體使用率與磁碟 IO。
2. **長期極致**：註冊 **Grafana Cloud (永久免費額度)**，安裝官方 `Google Cloud Monitoring` 資料源插件，直接在遠端 Grafana 匯入炫砲的 GCP 監控儀表板，完全不佔用 VM 寶貴的 1GB 記憶體！

---

## 📂 專案檔案清單

```text
github-daily-agent/
├── daily_sideproject_agent.py   # 核心工作流引擎 (5 大模組、Top 5 批次處理)
├── deploy_secrets.sh            # 安全環境變數部署腳本 (read -s, chmod 600, IAP 傳輸)
├── run_daily.sh                 # 自動化執行 Entrypoint (排程與日誌導流)
├── .env.example                 # 環境變數範本
├── .gitignore                   # 安全防護忽略清單 (已阻絕所有金鑰與日誌)
├── requirements.txt             # Python 輕量依賴 (requests, urllib3)
└── knowledge_base/
    └── obsidian/                # 本地 Obsidian Vault 產出資料夾
```

---

## 🧪 本地與遠端測試指令

### 1. 乾跑測試 (Dry-Run Mode)
不對 GitHub 與 Notion 產生任何副作用，僅在本地生成 Obsidian 報告與日誌：
```bash
./run_daily.sh --dry-run
```

### 2. 強制測試指定專案
```bash
python3 daily_sideproject_agent.py --force-repo "anthropics/financial-services" --dry-run
```

### 3. 一鍵安全部署至 GCP VM
```bash
./deploy_secrets.sh
```

---

## 📜 授權協議 (License)

本專案基於 [MIT License](LICENSE) 規範開源發布。
