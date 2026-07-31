#!/bin/bash
# 御膳房 - 一键启动脚本
# 启动 MySQL、后端、前端

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "=== 御膳房启动脚本 ==="

# 0. 确保 MySQL 运行
echo "[0/4] 检查 MySQL..."
if ! mysqladmin ping -h localhost --silent 2>/dev/null; then
    echo "启动 MySQL..."
    sudo service mysql start 2>/dev/null || sudo systemctl start mysql
    sleep 3
fi
echo "✅ MySQL 运行中"

# 1. 初始化数据库
echo "[1/4] 初始化数据库..."
bash "$PROJECT_DIR/scripts/init_db.sh" > /dev/null

# 2. 启动后端
echo "[2/4] 启动后端..."
cd "$BACKEND_DIR"
[ ! -d ".venv" ] && python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null

pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/yushanfang-backend.log 2>&1 &
echo "✅ 后端启动中 (http://localhost:8000)"

# 3. 启动前端
echo "[3/4] 启动前端..."
cd "$FRONTEND_DIR"
[ ! -d "node_modules" ] && npm install --no-audit --no-fund 2>/dev/null

pkill -f "vite.*yushanfang" 2>/dev/null || true
sleep 1
npm run dev:h5 > /tmp/yushanfang-frontend.log 2>&1 &
echo "✅ 前端启动中 (http://localhost:5173)"

echo ""
echo "=== 启动完成 ==="
echo "后端: http://localhost:8000 (日志: /tmp/yushanfang-backend.log)"
echo "前端: http://localhost:5173 (日志: /tmp/yushanfang-frontend.log)"
echo ""
echo "等待服务就绪..."
sleep 5
curl -s http://localhost:8000/ > /dev/null && echo "✅ 后端已就绪" || echo "❌ 后端未就绪"
curl -s http://localhost:5173/ > /dev/null && echo "✅ 前端已就绪" || echo "❌ 前端未就绪"
