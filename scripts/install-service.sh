#!/bin/bash
# 御膳房 - systemd 服务安装脚本
# 安装并启用开机自启

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SERVICE_DIR="$PROJECT_DIR/scripts"

echo "=== 御膳房服务安装 ==="

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

# 复制 service 文件
echo "安装 systemd 服务文件..."
cp "$SERVICE_DIR/yushanfang-backend.service" /etc/systemd/system/
cp "$SERVICE_DIR/yushanfang-frontend.service" /etc/systemd/system/

# 重新加载 systemd
systemctl daemon-reload

# 启用并启动服务
echo "启用服务开机自启..."
systemctl enable yushanfang-backend.service
systemctl enable yushanfang-frontend.service

echo "启动服务..."
systemctl start yushanfang-backend.service
systemctl start yushanfang-frontend.service

sleep 3

# 检查状态
echo ""
echo "=== 服务状态 ==="
systemctl status yushanfang-backend.service --no-pager || true
echo ""
systemctl status yushanfang-frontend.service --no-pager || true

echo ""
echo "✅ 安装完成"
echo "管理命令："
echo "  sudo systemctl start/stop/restart yushanfang-backend"
echo "  sudo systemctl start/stop/restart yushanfang-frontend"
echo "  sudo journalctl -u yushanfang-backend -f  # 查看日志"
