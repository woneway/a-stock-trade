#!/bin/bash
# 监听 docs/chat 目录变化

WATCH_DIR="/Users/lianwu/ai/projects/a-stock-trade/docs/chat"
LOG_FILE="/Users/lianwu/ai/projects/a-stock-trade/docs/chat/monitor.log"

echo "开始监听 chat 目录..."

# 记录上次状态
LAST_FILES=$(ls -la "$WATCH_DIR/requests/" "$WATCH_DIR/responses/" 2>/dev/null | md5)

while true; do
    sleep 3

    # 检查 requests 目录新文件
    CURRENT_FILES=$(ls -la "$WATCH_DIR/requests/" "$WATCH_DIR/responses/" 2>/dev/null | md5)

    if [ "$CURRENT_FILES" != "$LAST_FILES" ]; then
        echo "$(date): 检测到变化" | tee -a "$LOG_FILE"

        # 检查新请求
        NEW_REQUESTS=$(ls -t "$WATCH_DIR/requests/" 2>/dev/null | head -3)
        if [ -n "$NEW_REQUESTS" ]; then
            echo "新请求: $NEW_REQUESTS" >> "$LOG_FILE"
            echo "REQUESTS_CHANGED" > /tmp/chat_flag
        fi

        # 检查新响应
        NEW_RESPONSES=$(ls -t "$WATCH_DIR/responses/" 2>/dev/null | head -3)
        if [ -n "$NEW_RESPONSES" ]; then
            echo "新响应: $NEW_RESPONSES" >> "$LOG_FILE"
            echo "RESPONSES_CHANGED" >> /tmp/chat_flag
        fi

        LAST_FILES="$CURRENT_FILES"
    fi
done
