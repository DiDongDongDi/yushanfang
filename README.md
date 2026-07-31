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

## 技术架构

### 前端 (uni-app + Vue 3)
一套代码可同时编译为微信小程序和 H5 网页

### 后端 (Python + FastAPI)
- FastAPI：高性能 Web 框架
- SQLAlchemy：ORM 数据库操作
- MySQL：数据存储
- JWT：用户认证
- 通义千问 API：AI 能力

## 项目结构

```
yushanfang/
├── frontend/              # uni-app 前端
│   ├── pages/             # 页面
│   ├── components/        # 组件
│   ├── store/             # 状态管理
│   ├── api/               # API 调用
│   └── ...
├── backend/               # FastAPI 后端
│   ├── app/
│   │   ├── models/        # 数据库模型
│   │   ├── routers/       # API 路由
│   │   ├── services/      # 业务逻辑
│   │   ├── schemas/       # 数据校验
│   │   └── core/          # 配置、认证
│   └── ...
└── README.md
```

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev:h5      # H5 开发
npm run dev:mp-weixin  # 微信小程序开发
```

## License

MIT
