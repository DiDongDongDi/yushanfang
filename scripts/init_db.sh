#!/bin/bash
# 御膳房 - 数据库初始化脚本
# 自动创建数据库和用户

set -e

DB_NAME="yushanfang"
DB_USER="yushanfang"
DB_PASS="yushanfang123"
DB_ROOT_PASS="${MYSQL_ROOT_PASSWORD:-}"

echo "=== 御膳房数据库初始化 ==="

# 检查 MySQL 是否运行
if ! mysqladmin ping -h localhost --silent 2>/dev/null; then
    echo "MySQL 未运行，正在启动..."
    sudo service mysql start 2>/dev/null || sudo systemctl start mysql
    sleep 3
fi

# 创建数据库和用户
echo "创建数据库和用户..."
if [ -z "$DB_ROOT_PASS" ]; then
    sudo mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF
else
    mysql -u root -p"${DB_ROOT_PASS}" <<EOF
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF
fi

echo "✅ 数据库初始化完成"
echo "   数据库: ${DB_NAME}"
echo "   用户: ${DB_USER}"
echo "   密码: ${DB_PASS}"
