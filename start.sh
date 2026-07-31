#!/bin/bash
# 御膳房 - 一键启动脚本
# 启动 MySQL、后端、前端

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "=== 御膳房启动脚本 ==="

# 1. 启动 MySQL
echo "[1/4] 启动 MySQL..."
if ! mysqladmin ping -h localhost --silent 2>/dev/null; then
    sudo service mysql start 2>/dev/null || sudo systemctl start mysql
    sleep 3
fi
echo "✅ MySQL 已启动"

# 2. 初始化数据库
echo "[2/4] 初始化数据库..."
bash "$PROJECT_DIR/scripts/init_db.sh"

# 3. 启动后端
echo "[3/4] 启动后端..."
cd "$BACKEND_DIR"
if [ ! -d ".venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -q -r requirements.txt
else
    source .venv/bin/activate
fi

# 确保 .env 存在
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

# 启动 uvicorn（后台运行）
pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 1
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/yushanfang-backend.log 2>&1 &
echo "✅ 后端已启动 (http://localhost:8000)"

# 4. 启动前端（H5 开发模式）
echo "[4/4] 启动前端..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install --no-audit --no-fund
fi

# 构建 H5 并 serve，或开发模式
pkill -f "vite.*yushanfang" 2>/dev/null || true
sleep 1
nohup npm run dev:h5 > /tmp/yushanfang-frontend.log 2>&1 &
echo "✅ 前端已启动 (http://localhost:5173)"

echo ""
echo "=== 启动完成 ==="
echo "后端: http://localhost:8000"
echo "前端: http://localhost:5173"
echo "日志: /tmp/yushanfang-backend.log /tmp/yushanfang-frontend.log"
