#!/bin/bash
# 御膳房 - systemd 服务安装脚本
# 安装并启用开机自启
# 前端由 nginx 提供静态文件（构建后），nginx 默认开机自启

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SERVICE_DIR="$PROJECT_DIR/scripts"

echo "=== 御膳房服务安装 ==="

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

# 构建前端（生成静态文件）
echo "构建前端..."
cd "$PROJECT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    npm install --no-audit --no-fund
fi
npm run build:h5

# 配置 nginx
echo "配置 nginx..."
if [ -f "/etc/nginx/sites-available/yushanfang" ]; then
    cp "/etc/nginx/sites-available/yushanfang" "/etc/nginx/sites-available/yushanfang.bak"
fi
cat > /etc/nginx/sites-available/yushanfang <<'NGINX'
server {
    listen 80;
    server_name _;

    root /home/ubuntu/yushanfang/frontend/dist/build/h5;
    index index.html;

    # 前端 H5 - 静态文件
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 后端文档
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000;
    }

    # PWA 文件
    location /static/manifest.webmanifest {
        add_header Content-Type application/manifest+json;
    }

    location /static/sw.js {
        add_header Content-Type application/javascript;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/yushanfang /etc/nginx/sites-enabled/yushanfang
# 移除其他站点避免冲突
rm -f /etc/nginx/sites-enabled/opencode /etc/nginx/sites-enabled/workbench 2>/dev/null || true
nginx -t && systemctl reload nginx

# 安装后端 systemd 服务
echo "安装后端 systemd 服务..."
cp "$SERVICE_DIR/yushanfang-backend.service" /etc/systemd/system/

# 重新加载 systemd
systemctl daemon-reload

# 启用并启动服务
echo "启用服务开机自启..."
systemctl enable yushanfang-backend.service
systemctl start yushanfang-backend.service

sleep 3

# 检查状态
echo ""
echo "=== 服务状态 ==="
systemctl status yushanfang-backend.service --no-pager || true

echo ""
echo "✅ 安装完成"
echo "服务地址：http://$(hostname -I | awk '{print $1}')/（需在云安全组开放 80 端口）"
echo "管理命令："
echo "  sudo systemctl start/stop/restart yushanfang-backend"
echo "  sudo journalctl -u yushanfang-backend -f  # 查看日志"
