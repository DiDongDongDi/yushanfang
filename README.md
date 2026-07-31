# 御膳房 - 智能点菜小程序

御膳房是一款智能点菜小程序，支持 AI 推荐今日菜品、AI 生成菜品三个部分（买菜清单、备菜步骤、烹饪做法），并将多道菜的流程智能整合，生成可勾选的烹饪步骤清单，支持倒计时功能。

## 功能特性

- 🤖 **AI 推荐**：根据你的饮食偏好推荐今天想吃什么
- 🍽️ **点菜系统**：
  - 直接输入任意菜名点菜
  - 从历史做过的菜中选择
  - AI 推荐菜品一键点菜
  - 每个菜支持添加图片
- 👤 **用户系统**：
  - 手机号 + 验证码注册/登录
  - 微信登录（小程序端）
- 📋 **AI 菜谱生成**：为每道菜生成
  - 需要买的菜（食材清单）
  - 具体的备菜步骤
  - 具体的做法
- 🔄 **多菜流程整合**：将多道菜的三个部分分别整合，交给 AI 优化买菜、备菜和做菜流程
- ✅ **步骤清单**：将本次做饭生成一道道步骤，支持勾选完成
- ⏱️ **倒计时**：每个步骤支持根据 AI 提供的时间开启倒计时
- 💾 **数据存储**：所有数据存储到 MySQL 数据库
- 🔧 **自定义 AI**：支持任何 OpenAI 兼容的 AI 服务（自定义 BaseURL、API Key、模型 ID）
- 📱 **PWA 支持**：前端支持 PWA，可安装到桌面

## 技术架构

### 前端 (uni-app + Vue 3)
一套代码可同时编译为微信小程序和 H5 网页，H5 支持 PWA

### 后端 (Python + FastAPI)
- FastAPI：高性能 Web 框架
- SQLAlchemy：ORM 数据库操作
- MySQL：数据存储
- JWT：用户认证
- 支持任何 OpenAI 兼容的 AI API

## 快速开始

### 一键启动（推荐）

```bash
# 克隆项目
git clone https://github.com/DiDongDongDi/yushanfang.git
cd yushanfang

# 一键启动所有服务（自动初始化数据库、启动后端和前端）
bash start.sh
```

访问：
- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 手动启动

#### 后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 初始化数据库（自动创建）
bash ../scripts/init_db.sh

# 启动后端
cp .env.example .env  # 可选：配置 AI API Key
uvicorn app.main:app --reload
```

#### 前端

```bash
cd frontend
npm install
npm run dev:h5      # H5 开发
npm run dev:mp-weixin  # 微信小程序开发
```

### 配置 AI 服务

支持任何 OpenAI 兼容的 AI 服务（通义千问、OpenAI、DeepSeek 等）：

**方式一：通过 API 配置（推荐）**

启动后访问：前端 → 个人中心 → AI 设置

**方式二：环境变量**

编辑 `backend/.env`：
```
AI_BASE_URL=https://your-ai-api.com/v1
AI_API_KEY=your-api-key
AI_MODEL=model-name
```

## 开机自启（生产部署）

```bash
# 安装 systemd 服务（开机自启）
sudo bash scripts/install-service.sh

# 管理服务
sudo systemctl start/stop/restart yushanfang-backend
sudo systemctl start/stop/restart yushanfang-frontend
sudo journalctl -u yushanfang-backend -f  # 查看日志
```

## PWA 支持

前端已支持 PWA（Progressive Web App）：
- 可安装到桌面/手机主屏幕
- 支持离线访问（缓存静态资源）
- 类原生应用体验

构建 H5 后，静态文件位于 `frontend/dist/build/h5/`，可直接部署到任何 Web 服务器。

## 项目结构

```
yushanfang/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── models/       # 数据库模型
│   │   ├── routers/      # API 路由
│   │   ├── services/     # 业务逻辑
│   │   ├── schemas/      # 数据校验
│   │   └── core/         # 配置、认证
│   └── ...
├── frontend/             # uni-app 前端
│   ├── src/
│   │   ├── pages/        # 页面
│   │   ├── api/          # API 调用
│   │   └── static/       # 静态资源（含 PWA 文件）
│   └── ...
├── scripts/              # 脚本
│   ├── init_db.sh        # 数据库初始化
│   ├── install-service.sh # systemd 服务安装
│   └── *.service         # systemd 服务文件
├── start.sh              # 一键启动脚本
└── README.md
```

## License

MIT
