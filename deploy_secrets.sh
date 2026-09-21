#!/usr/bin/env bash
# ==============================================================================
# 安全密鑰與環境變數部署腳本 (deploy_secrets.sh)
# 資安規範：
# 1. read -s 靜默輸入，不回顯、不留痕於歷史紀錄與日誌
# 2. 自動檢查並補齊 .gitignore 保護 .env
# 3. 本機 .env 強制 chmod 600
# 4. gcloud compute scp (IAP Tunnel) 安全傳輸至 GCP VM
# 5. 遠端 VM .env 同步強制 chmod 600
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_ENV="$SCRIPT_DIR/.env"
GITIGNORE="$SCRIPT_DIR/.gitignore"

GCP_PROJECT="project-3edbf8fb-2987-474a-944"
GCP_ZONE="us-central1-a"
GCP_INSTANCE="hybrid-cloud-node"
REMOTE_ENV="~/github-daily-agent/.env"

echo "================================================================================"
echo "🔒 [Security Check] 啟動安全環境變數部署流程"
echo "================================================================================"

# ------------------------------------------------------------------------------
# 步驟 1: 檢查並確保 .gitignore 包含 .env
# ------------------------------------------------------------------------------
echo "[1/5] 檢查 .gitignore 設定..."
if [ ! -f "$GITIGNORE" ]; then
    echo ".env" > "$GITIGNORE"
    echo ".env.*" >> "$GITIGNORE"
    echo "!.env.example" >> "$GITIGNORE"
    echo "[✓] 已建立 .gitignore 並加入 .env"
else
    if ! grep -qE "^\.env$" "$GITIGNORE"; then
        echo -e "\n# Secrets" >> "$GITIGNORE"
        echo ".env" >> "$GITIGNORE"
        echo ".env.*" >> "$GITIGNORE"
        echo "!.env.example" >> "$GITIGNORE"
        echo "[✓] 已自動將 .env 加入現有 .gitignore"
    else
        echo "[✓] .gitignore 已安全包含 .env"
    fi
fi

# ------------------------------------------------------------------------------
# 步驟 2: 互動式安全讀取 GEMINI_API_KEY (無回顯、不留痕)
# ------------------------------------------------------------------------------
echo ""
echo "[2/5] 請輸入 GEMINI_API_KEY (密碼模式：輸入時不會顯示任何字元，避免被旁人或錄影窺探)"
read -s -p "🔑 請貼上您的 GEMINI_API_KEY: " RAW_GEMINI_KEY
echo ""

if [ -z "$RAW_GEMINI_KEY" ]; then
    echo "[!] 輸入為空，終止部署流程。"
    exit 1
fi

# 驗證格式（去除前後空白）
GEMINI_KEY="$(echo "$RAW_GEMINI_KEY" | xargs)"
unset RAW_GEMINI_KEY

# ------------------------------------------------------------------------------
# 步驟 3: 寫入本機 .env 並立刻設定 chmod 600
# ------------------------------------------------------------------------------
echo "[3/5] 更新本機 .env 並鎖定檔案權限..."
if [ ! -f "$LOCAL_ENV" ]; then
    if [ -f "$SCRIPT_DIR/.env.example" ]; then
        cp "$SCRIPT_DIR/.env.example" "$LOCAL_ENV"
    else
        touch "$LOCAL_ENV"
    fi
fi

# 替換或新增 GEMINI_API_KEY
if grep -q "^GEMINI_API_KEY=" "$LOCAL_ENV"; then
    # 使用 awk / sed 安全置換，避免特定符號跳脫問題
    awk -v key="$GEMINI_KEY" 'BEGIN{FS=OFS="="} /^GEMINI_API_KEY=/{$2=key} {print}' "$LOCAL_ENV" > "$LOCAL_ENV.tmp" && mv "$LOCAL_ENV.tmp" "$LOCAL_ENV"
else
    echo "GEMINI_API_KEY=$GEMINI_KEY" >> "$LOCAL_ENV"
fi

# 立即銷毀記憶體中的變數
unset GEMINI_KEY

# 強制將本機 .env 設定為 600 權限 (僅擁有者可讀寫)
chmod 600 "$LOCAL_ENV"
echo "[✓] 本機 .env 已設定為權限 600:"
ls -la "$LOCAL_ENV"

# ------------------------------------------------------------------------------
# 步驟 4: 安全傳輸至 GCP VM (透過 IAP 隧道加密傳輸)
# ------------------------------------------------------------------------------
echo ""
echo "[4/5] 透過 gcloud IAP 隧道安全傳輸 .env 至 GCP VM ($GCP_INSTANCE)..."

SSH_ARGS=()
if [ -f "$HOME/.ssh/gcp_auto_key" ]; then
    SSH_ARGS+=(--ssh-key-file="$HOME/.ssh/gcp_auto_key")
fi

gcloud compute scp "$LOCAL_ENV" "$GCP_INSTANCE:$REMOTE_ENV" \
    --project="$GCP_PROJECT" \
    --zone="$GCP_ZONE" \
    --tunnel-through-iap \
    "${SSH_ARGS[@]}"

echo "[✓] 遠端檔案傳輸完成。"

# ------------------------------------------------------------------------------
# 步驟 5: 透過 gcloud ssh 將遠端 VM 上的 .env 權限同樣設為 600
# ------------------------------------------------------------------------------
echo ""
echo "[5/5] 設定遠端 VM 上的 .env 檔案權限為 600..."

gcloud compute ssh "$GCP_INSTANCE" \
    --project="$GCP_PROJECT" \
    --zone="$GCP_ZONE" \
    --tunnel-through-iap \
    "${SSH_ARGS[@]}" \
    --command="chmod 600 $REMOTE_ENV && echo '[✓] 遠端權限驗證成功:' && ls -la $REMOTE_ENV"

echo ""
echo "================================================================================"
echo "🎉 [Success] 安全部署全部完成！"
echo "本機與遠端 VM 均已配置最新金鑰，權限已安全鎖定為 600，且完全受 .gitignore 保護。"
echo "================================================================================"
