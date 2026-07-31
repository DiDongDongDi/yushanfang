# 御膳房 - 开发计划

## 项目概述

御膳房是一款智能点菜小程序，核心价值是让用户"今天吃什么"由 AI 推荐，并由 AI 帮用户把多道菜的买菜、备菜、做菜流程智能整合，做饭更高效。

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | uni-app (Vue 3) | 一套代码编译微信小程序 + H5 |
| 后端 | Python + FastAPI | 高性能异步 Web 框架 |
| 数据库 | MySQL | 关系型数据库 |
| AI | 通义千问 API | 国产 AI，国内稳定访问 |
| 认证 | JWT | 手机号验证码 + 微信登录 |

## 功能模块

### 1. 用户系统
- 手机号 + 验证码注册/登录
- 微信登录（小程序端，wx.login 获取 code，后端换取 openid）
- JWT Token 认证
- 用户信息管理

### 2. 菜品管理
- 添加/编辑菜品（名称、描述、图片）
- 菜品历史记录（做过的菜）
- AI 推荐菜品

### 3. AI 菜谱生成
每道菜生成三个部分：
- 需要买的菜（食材清单）
- 具体的备菜步骤
- 具体的做法

### 4. 多菜流程整合
将本次做饭的多道菜按三个部分分别整合，交给 AI 优化：
- 整合所有菜的买菜清单，去重合并
- 整合所有菜的备菜步骤，优化流程
- 整合所有菜的做法，统一操作流程

### 5. 烹饪步骤管理
- 生成一道道步骤清单
- 支持勾选完成
- 每个步骤带 AI 推荐时间，支持倒计时

## 数据库设计

### users（用户表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 用户ID |
| phone | VARCHAR | 手机号 |
| wechat_openid | VARCHAR | 微信 openid |
| nickname | VARCHAR | 昵称 |
| avatar | VARCHAR | 头像URL |
| created_at | DATETIME | 创建时间 |

### dishes（菜品表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 菜品ID |
| user_id | INT FK | 所属用户 |
| name | VARCHAR | 菜名 |
| image | VARCHAR | 图片URL |
| description | TEXT | 描述 |
| created_at | DATETIME | 创建时间 |

### cooking_records（烹饪记录表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 记录ID |
| user_id | INT FK | 所属用户 |
| dishes_json | JSON | 本次做的菜列表 |
| buy_list | TEXT | AI 优化后的买菜清单 |
| prep_steps | TEXT | AI 优化后的备菜步骤 |
| cook_steps | TEXT | AI 优化后的做法步骤 |
| status | VARCHAR | 状态（进行中/完成） |
| created_at | DATETIME | 创建时间 |

### cooking_steps（烹饪步骤表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 步骤ID |
| record_id | INT FK | 所属烹饪记录 |
| title | VARCHAR | 步骤标题 |
| detail | TEXT | 步骤详情 |
| timer_minutes | INT | 建议时间（分钟） |
| is_done | BOOL | 是否完成 |
| sort_order | INT | 排序 |
| created_at | DATETIME | 创建时间 |

## API 设计

### 认证
- `POST /api/auth/send-code` - 发送验证码
- `POST /api/auth/login` - 手机号登录
- `POST /api/auth/wechat-login` - 微信登录

### 用户
- `GET /api/users/me` - 获取当前用户信息
- `PUT /api/users/me` - 更新用户信息

### 菜品
- `POST /api/dishes` - 添加菜品
- `GET /api/dishes` - 获取菜品列表（含历史）
- `GET /api/dishes/{id}` - 获取菜品详情
- `PUT /api/dishes/{id}` - 编辑菜品
- `DELETE /api/dishes/{id}` - 删除菜品

### AI
- `POST /api/ai/recommend` - AI 推荐今日菜品
- `POST /api/ai/generate-recipe` - AI 生成菜谱（三部分）
- `POST /api/ai/optimize-plan` - AI 整合多菜流程

### 烹饪记录
- `POST /api/cooking-records` - 创建烹饪记录
- `GET /api/cooking-records` - 获取烹饪记录列表
- `GET /api/cooking-records/{id}` - 获取记录详情
- `PUT /api/cooking-steps/{id}` - 更新步骤状态（勾选/倒计时）

## 前端页面

1. **首页** - AI 推荐、今日菜品、历史点菜
2. **点菜页** - 搜索/输入菜名、历史菜品选择、AI 推荐一键点菜
3. **菜品详情** - 菜名、图片、AI 生成的三部分内容
4. **烹饪流程页** - 步骤清单、勾选、倒计时
5. **登录页** - 手机号验证码登录/注册
6. **个人中心** - 用户信息、历史记录

## 开发里程碑

### M1: 项目初始化
- [x] Git 仓库初始化
- [x] 项目文档
- [ ] GitHub 公开仓库

### M2: 后端开发
- [ ] FastAPI 项目骨架
- [ ] 数据库模型
- [ ] 认证系统
- [ ] 菜品 CRUD
- [ ] AI 集成（通义千问）
- [ ] 烹饪记录管理

### M3: 前端开发
- [ ] uni-app 项目初始化
- [ ] 登录/注册页
- [ ] 首页
- [ ] 点菜页
- [ ] 菜品详情
- [ ] 烹饪流程页
- [ ] 个人中心

### M4: 联调与部署
- [ ] 前后端联调
- [ ] 微信开发者工具调试
- [ ] 部署文档

## 部署说明

- 后端：可部署到阿里云/腾讯云服务器
- 前端：uni-app 编译后上传微信审核发布
- 数据库：MySQL（云数据库或自建）
- AI：需开通阿里云通义千问 API 获取 API Key
