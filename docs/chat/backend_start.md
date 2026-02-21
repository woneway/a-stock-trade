# 后端启动监听

在**后端终端**执行以下命令：

```bash
# 启动监听（后台运行）
bash /Users/lianwu/ai/projects/a-stock-trade/docs/chat/monitor.sh &

# 或者前台运行查看日志
tail -f /Users/lianwu/ai/projects/a-stock-trade/docs/chat/monitor.log
```

---

## 检查新消息

```bash
# 查看标记文件
cat /tmp/chat_flag

# 查看请求目录
ls -la /Users/lianwu/ai/projects/a-stock-trade/docs/chat/requests/

# 查看响应目录
ls -la /Users/lianwu/ai/projects/a-stock-trade/docs/chat/responses/
```

---

## 告诉 AI 有新消息

直接说：**"检查新请求"**
