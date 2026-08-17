# 📰 头条新闻系统（ai_toutiao）—— 移动端资讯后端

**FastAPI + SQLAlchemy + MySQL + Redis + Vue3 全栈资讯应用**：后端以 Router-CRUD-Model 三层架构提供 RESTful API，用 Redis 旁路缓存缓解首页高频查询压力，并基于 SSE 流式封装通义千问 AI 问答；前端基于 Vue 3 + Vant 提供多分类新闻浏览、收藏/历史云端同步与 AI 对话。

![FastAPI](https://img.shields.io/badge/FastAPI-0.125-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-异步-D71F00?logo=sqlalchemy&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8%2B-4479A1?logo=mysql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7%2B-DC382D?logo=redis&logoColor=white)
![Vue](https://img.shields.io/badge/Vue-3-4FC08D?logo=vuedotjs&logoColor=white)

---

## 1. 项目解决什么问题

- **信息获取不便**：为用户提供分类清晰、实时更新的新闻资讯浏览体验，覆盖头条、社会、国内、国际、娱乐、体育、军事、科技、财经等多个频道。
- **阅读体验单一**：支持浅色/深色/蓝色/绿色多种主题，适配不同场景和偏好的阅读需求。
- **缺乏智能辅助**：内置 AI 问答功能，用户可以直接向 AI 提问，获取新闻相关的深度解读或任意问题的智能回答。
- **跨设备数据同步**：登录后收藏和历史记录与后端同步，更换设备不丢失个人数据。

---

## 🏗️ 系统架构

```mermaid
flowchart LR
    subgraph Frontend[前端 xwzx-news]
        Vue[Vue 3 + Vant + Pinia]
    end

    subgraph Backend[后端 toutiao_backend FastAPI]
        Router[Router 路由层<br/>news / user / favorite / history / ai]
        CRUD[CRUD 数据访问层<br/>SQLAlchemy 异步 ORM]
        Model[Model 模型层<br/>用户 / Token / 新闻 / 收藏 / 历史]
        Cache[Redis 旁路缓存<br/>分类 1h / 列表 60s]
        AI[AI SSE 代理<br/>StreamingResponse]
    end

    subgraph Data[存储与外部]
        MySQL[(MySQL 8)]
        Redis[(Redis)]
        LLM[通义千问<br/>DashScope]
    end

    Vue -->|HTTP JSON| Router
    Vue -->|SSE 流式| AI
    Router --> CRUD --> Model --> MySQL
    Router --> Cache --> Redis
    AI -->|httpx 异步代理| LLM
    LLM -->|逐 token| AI
```

## 2. 主要功能

### 📱 新闻浏览
- 多分类 Tab 切换（头条、社会、国内、国际、娱乐、体育、军事、科技、财经）
- 下拉刷新 + 无限滚动加载更多
- 新闻详情页：标题、作者、发布时间、阅读量、封面图、正文、相关推荐
- 分类网格页，快速跳转任意频道

### 🤖 AI 智能问答
- 基于阿里云 DashScope（通义千问 qwen3-max-preview）大模型，由后端 SSE 代理转发（API Key 只保存在服务端）
- 支持 SSE 流式输出，打字机效果实时展示
- Markdown 渲染，支持代码块、列表、链接等富文本
- 多轮对话上下文记忆

### 👤 用户系统
- 注册 / 登录（Token 数据库会话认证，7 天过期）
- 个人信息管理（头像、用户名、个人简介）
- 密码修改

### ⭐ 收藏 & 历史
- 新闻收藏 / 取消收藏（API 同步 + 本地持久化）
- 浏览历史自动记录（支持逐条删除、一键清空）
- 登录后数据与后端同步，未登录时使用本地存储

### 🎨 主题 & 语言
- 4 套主题：浅色模式、深色模式、蓝色主题、绿色主题
- 中 / 英双语切换（vue-i18n）
- 设置即时生效，主题和语言偏好持久化

---

## 3. 安装方法

### 环境要求

- **Node.js** >= 18
- **包管理器**：npm / yarn / pnpm

### 前端安装

```bash
# 进入项目目录
cd xwzx-news

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 后端 API

后端代码位于本仓库 `toutiao_backend/` 目录（FastAPI + SQLAlchemy + MySQL + Redis），默认地址为 `http://127.0.0.1:8000`。

**后端特性**：

- **三层架构**：Router-CRUD-Model 分层，路由层只做参数校验与响应，数据访问集中在 CRUD 层，外键约束保证引用完整性
- **Redis 旁路缓存**：首页高频查询走缓存（分类 1h / 列表 60s 差异化过期），缓存未命中自动回源数据库
- **SSE 流式 AI 问答**：后端基于 StreamingResponse 透传 DashScope 流式响应，逐字下发解决同步接口首包延迟（TTFB）过高问题，API Key 只保存在服务端
- **认证与接口健壮性**：bcrypt 密码哈希 + Token 数据库会话（7 天过期）；统一响应体（code/message/data）与全局异常处理器，保证接口返回格式一致、异常可追踪

```bash
cd toutiao_backend
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
# 需本地 MySQL(3306)/Redis(6379)；启动时自动建表
.venv/Scripts/python -m uvicorn main:app --reload
```

> 首次启动前需创建数据库（建表由应用启动时自动完成）：
>
> ```sql
> CREATE DATABASE news_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
> ```
>
> 数据库连接默认 `mysql+aiomysql://root:root@localhost:3306/news_app`，可通过环境变量 `DATABASE_URL` 覆盖。

> 如需修改后端地址，可在 `src/config/api.js` 中修改 `baseURL`。

API 接口列表：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/news/categories` | 获取新闻分类 |
| GET | `/api/news/list` | 获取新闻列表（分页） |
| GET | `/api/news/detail` | 获取新闻详情 |
| POST | `/api/user/login` | 用户登录 |
| POST | `/api/user/register` | 用户注册 |
| GET | `/api/user/info` | 获取用户信息 |
| PUT | `/api/user/update` | 更新个人信息 |
| PUT | `/api/user/password` | 修改密码 |
| POST | `/api/favorite/add` | 添加收藏 |
| DELETE | `/api/favorite/remove` | 取消收藏 |
| GET | `/api/favorite/list` | 收藏列表 |
| GET | `/api/favorite/check` | 检查收藏状态 |
| DELETE | `/api/favorite/clear` | 清空收藏 |
| POST | `/api/history/add` | 添加浏览历史 |
| GET | `/api/history/list` | 浏览历史列表 |
| DELETE | `/api/history/clear` | 清空历史 |
| DELETE | `/api/history/delete/:id` | 删除单条历史 |
| POST | `/api/ai/chat` | AI 问答（SSE 流式，服务端代理 DashScope） |

### AI 问答配置

AI 问答由**后端代理**转发至阿里云 DashScope（通义千问），前端只需指向后端 `/api/ai/chat`，**API Key 只保存在服务端**，不再暴露给前端。

后端启动前需配置环境变量（参考 `toutiao_backend/.env.example`）：

| 环境变量 | 必填 | 说明 |
|------|------|------|
| `DASHSCOPE_API_KEY` | ✅ | 阿里云百炼平台的 API Key |
| `DASHSCOPE_MODEL` | ❌ | 模型名，默认 `qwen3-max-preview` |

```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY="sk-xxxx"

# 或在 toutiao_backend/ 下创建 .env 文件（已被 .gitignore 忽略）
DASHSCOPE_API_KEY=sk-xxxx
```

---

## 4. 使用方法

### 启动开发服务器

```bash
cd xwzx-news
npm run dev
```

浏览器访问 `http://localhost:5173`（默认端口）。

### 构建生产版本

```bash
npm run build     # 输出到 dist/ 目录
npm run preview   # 本地预览构建结果
```

### 页面导航

| 路由 | 页面 | 说明 |
|------|------|------|
| `/home` | 首页 | 新闻列表 + 分类切换 |
| `/category` | 全部分类 | 网格展示所有分类 |
| `/news/detail/:id` | 新闻详情 | 文章正文 + 收藏 + 相关推荐 |
| `/aichat` | AI 问答 | 与 AI 实时对话 |
| `/my` | 我的 | 个人中心入口 |
| `/login` | 登录 | 用户登录 |
| `/register` | 注册 | 用户注册 |
| `/profile` | 个人信息 | 修改头像、简介、密码 |
| `/favorite` | 我的收藏 | 收藏列表管理 |
| `/history` | 浏览历史 | 历史记录管理 |
| `/settings` | 设置 | 主题切换、语言切换 |

### 底部导航栏

- **首页**：浏览新闻
- **AI 问答**：智能对话
- **我的**：个人中心

---

## 5. 输入输出示例

### 5.1 新闻列表 API 响应

**请求：**
```
GET http://127.0.0.1:8000/api/news/list?categoryId=1&page=1&pageSize=10
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 1,
        "title": "国内油价迎来年内最大降幅",
        "description": "据国家发改委消息，自2026年8月11日24时起，国内汽、柴油价格每吨分别降低340元和330元...",
        "image": "https://example.com/images/oil-price.jpg",
        "author": "新华社",
        "publishTime": "2026-08-11 10:30:00",
        "categoryId": 3,
        "views": 12850
      }
    ],
    "total": 100
  }
}
```

### 5.2 新闻详情 API 响应

**请求：**
```
GET http://127.0.0.1:8000/api/news/detail?id=1
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "title": "国内油价迎来年内最大降幅",
    "author": "新华社",
    "publishTime": "2026-08-11 10:30:00",
    "views": 12850,
    "image": "https://example.com/images/oil-price.jpg",
    "content": "据国家发改委消息...\n\n专家表示，此次油价下调幅度超出市场预期...\n\n对于普通车主来说，加满一箱油将少花约17元...",
    "relatedNews": [
      {
        "id": 15,
        "title": "国际原油价格持续走低",
        "image": "https://example.com/images/oil-global.jpg"
      }
    ]
  }
}
```

### 5.3 AI 问答交互示例

**用户输入：**
> 今天的头条新闻是什么？

**AI 流式输出：**
```
根据当前可获取的信息，我无法直接获取实时新闻。
不过，您可以在应用的"首页"标签下查看最新的头条新闻。

如果您对某条新闻有疑问，或者想了解特定话题的
更多背景信息，请随时告诉我，我很乐意帮助您分析！
```

**用户输入：**
> 用 Python 写一个快速排序

**AI 流式输出（Markdown 渲染）：**
```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

# 示例
print(quicksort([3, 6, 8, 10, 1, 2, 1]))
# 输出: [1, 1, 2, 3, 6, 8, 10]
```

### 5.4 用户登录

**请求：**
```
POST http://127.0.0.1:8000/api/user/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "userInfo": {
      "id": 1,
      "username": "your_username",
      "bio": "这是我的个人简介"
    },
    "token": "53ce8881-9daa-4216-9b38-15590870ae44"
  }
}
```

### 5.5 界面截图说明

| 功能 | 描述 |
|------|------|
| 首页 | 顶部固定导航栏 + 分类 Tab + 新闻列表（左文右图），支持下拉刷新和上拉加载更多 |
| 分类页 | 3 列网格布局，展示所有新闻频道，点击跳转至对应分类列表 |
| 新闻详情 | 标题 + 收藏按钮 + 作者/时间/阅读量 + 封面图 + 正文段落 + 相关推荐 |
| AI 问答 | 聊天气泡式界面，用户消息蓝色靠右，AI 消息灰色靠左，支持 Markdown 渲染 |
| 个人中心 | 头像 + 用户名 + 简介 + 收藏/历史/设置入口，未登录时显示登录/注册按钮 |
| 设置 | 主题选择弹窗（四色圆形预览）+ 语言切换（中/英单选列表） |

---

## 技术栈

| 类别 | 技术 |
|------|------|
| 框架 | Vue 3（Composition API） |
| 构建工具 | Vite 7 |
| 路由 | Vue Router 4 |
| 状态管理 | Pinia 3 + pinia-plugin-persistedstate |
| UI 组件库 | Vant 4 |
| HTTP 请求 | Axios |
| 国际化 | vue-i18n 9 |
| Markdown | marked + DOMPurify |
| 后端框架 | FastAPI + SQLAlchemy 异步 ORM + Pydantic |
| 数据库 | MySQL 8（aiomysql 异步驱动） |
| 缓存 | Redis（旁路缓存模式，差异化过期策略） |
| AI 接口 | 阿里云 DashScope（兼容 OpenAI 格式，httpx 异步代理 + SSE 流式透传） |

---

## 项目结构

```
xwzx-news/
├── index.html                 # 入口 HTML
├── package.json               # 项目依赖
├── vite.config.js             # Vite 配置
├── public/
│   └── vite.svg               # 网站图标
└── src/
    ├── main.js                # 应用入口（注册插件、组件）
    ├── App.vue                # 根组件（路由视图 + keep-alive）
    ├── style.css              # 全局样式 + CSS 变量 + 动画
    ├── config/
    │   └── api.js             # API 地址 & AI 配置
    ├── router/
    │   └── index.js           # 路由配置（11 条路由）
    ├── store/
    │   ├── index.js           # Pinia 实例（持久化插件）
    │   ├── user.js            # 用户状态（登录/注册/信息/密码）
    │   ├── theme.js           # 主题状态（4 套主题切换）
    │   ├── language.js        # 语言状态（中/英）
    │   └── modules/
    │       ├── news.js        # 新闻状态（列表/详情/分类）
    │       ├── favorite.js    # 收藏状态（增删查改/API同步）
    │       └── history.js     # 历史状态（记录/清空/API同步）
    ├── views/
    │   ├── Home.vue           # 首页（分类Tab + 新闻列表）
    │   ├── Category.vue       # 全部分类页
    │   ├── NewsDetail.vue     # 新闻详情页
    │   ├── AIChat.vue         # AI 问答页（SSE 流式聊天）
    │   ├── Login.vue          # 登录页
    │   ├── Register.vue       # 注册页
    │   ├── My.vue             # 个人中心
    │   ├── Profile.vue        # 个人信息（修改简介/密码）
    │   ├── Favorite.vue       # 收藏列表
    │   ├── History.vue        # 浏览历史
    │   └── Settings.vue       # 设置（主题/语言切换）
    ├── components/
    │   ├── TabBar.vue         # 底部导航栏
    │   └── NewsItem.vue       # 新闻列表卡片
    └── i18n/
        ├── index.js           # i18n 实例配置
        └── locales/
            ├── zh-CN.js       # 中文语言包
            └── en-US.js       # 英文语言包
```

```
toutiao_backend/
├── main.py                  # FastAPI 入口（lifespan 自动建表、全局异常处理器）
├── config/
│   └── db_conf.py           # SQLAlchemy 异步引擎 + 会话工厂
├── routers/                 # 路由层（news / user / favorite / history / ai）
├── crud/                    # CRUD 层（数据库操作封装）
├── models/                  # 模型层（ORM：用户 / Token / 新闻 / 收藏 / 历史）
├── schemas/                 # Pydantic 请求/响应模型
└── utils/                   # 统一响应体 / 异常处理 / Redis 缓存 / bcrypt / DashScope 客户端
```

---

## License

MIT
