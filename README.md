# Review Backend

基于 FastAPI + PostgreSQL + Redis 构建的资讯平台后端服务，面向“新闻浏览、用户互动、后台运营分析”场景设计。项目覆盖用户端与管理端两条业务链路，不仅实现了常规内容查询，还补充了登录留痕、收藏排行、连续登录统计，以及基于 Qwen embedding 的个性化推荐等更贴近真实业务的数据能力。

## 项目定位

这个项目是一个强调“业务闭环 + 工程化落地”的异步后端服务：

- 面向资讯类产品，完成了分类浏览、详情查询、收藏、历史记录、个人中心等用户功能。
- 额外实现了后台管理接口，支持用户分页查询、新闻检索、连续登录统计、收藏排行等运营分析能力。
- 引入 PostgreSQL、Redis、Alembic、Docker Compose，具备基础的可部署性和可扩展性。
- 新增 AI 个性化推荐能力，可基于用户浏览历史与收藏行为生成更贴近兴趣的新闻流。

## 项目亮点

- 异步后端架构：使用 FastAPI + SQLAlchemy AsyncSession + asyncpg，面向高并发 I/O 场景设计，接口层与数据访问层分离清晰。
- 用户行为闭环：从注册登录、个人信息维护，到浏览历史、收藏管理，再到新闻详情阅读与相关推荐，形成完整用户路径。
- AI 推荐更贴近资讯业务：基于新闻标题、摘要、正文生成 embedding，结合用户最近浏览与收藏行为构建兴趣画像，输出个性化推荐结果。
- 数据统计能力更贴近真实业务：
  - 通过 `user_login_log` 记录用户每日登录行为，为连续登录统计提供可靠数据基础。
  - 管理端使用 PostgreSQL 窗口函数统计“连续登录 N 天用户”，不是简单计数，更能体现 SQL 分析能力。
  - 基于收藏表聚合实现“新闻收藏排行榜”，可直接支撑运营看板类需求。
- 缓存优化：新闻分类和新闻列表接入 Redis 缓存，减少热点查询对数据库的压力。
- 服务端 Token 管理：用户端与管理端均采用数据库持久化 Token，而不是纯前端自持 JWT，便于统一控制会话有效期与失效策略。
- 幂等与约束意识：
  - 收藏表使用联合唯一约束，避免重复收藏。
  - 浏览历史对同一新闻采用“更新最近浏览时间”策略，减少脏数据堆积。
  - 登录日志按“用户 + 日期”去重，既保留统计价值，也避免重复插入。
- 工程化能力完整：提供 Alembic 数据迁移、`.env` 配置、Dockerfile、`docker-compose.yml`，支持本地开发和容器化部署。

## 核心功能

### 用户端

- 用户注册、登录、获取个人信息
- 修改昵称、头像、性别、简介、手机号
- 修改密码
- 新闻分类列表、新闻分页列表、新闻详情
- 详情页自动增加浏览量，并返回同分类相关推荐
- AI 个性化推荐列表，根据历史记录和收藏行为推荐新闻
- 收藏检查、添加收藏、取消收藏、收藏列表、清空收藏
- 浏览历史新增、分页查询、删除单条、清空历史

### 管理端

- 管理员登录
- 用户分页查询，支持关键字搜索
- 新闻分页查询，支持关键字和分类筛选
- 连续登录用户统计
- 新闻收藏排行榜
## 技术栈

| 类别 | 技术选型 |
| --- | --- |
| Web 框架 | FastAPI |
| 数据库 | PostgreSQL |
| ORM | SQLAlchemy 2.x |
| 数据迁移 | Alembic |
| 缓存 | Redis |
| 数据校验 | Pydantic v2 |
| AI 能力 | Qwen Embedding（DashScope Compatible Mode） |
| HTTP 客户端 | httpx |
| 鉴权 | 基于数据库持久化 Token 的服务端鉴权 |
| 容器化 | Docker + Docker Compose |

## 目录结构

```text
review_backend/
├─ routers/        # 路由层，按业务模块拆分接口
├─ crud/           # 数据访问层，封装数据库查询与写入逻辑
├─ models/         # SQLAlchemy ORM 模型
├─ schemas/        # Pydantic 请求/响应模型
├─ conf/           # 数据库、Redis、环境配置
├─ cache/          # 缓存读写封装
├─ utils/          # 鉴权、密码加密、统一响应等通用工具
├─ alembic/        # 数据库迁移脚本
├─ main.py         # 应用入口
├─ Dockerfile
├─ docker-compose.yml
└─ requirements.txt
```

## 接口概览

### 用户相关

- `POST /api/user/register` 用户注册
- `POST /api/user/login` 用户登录
- `GET /api/user/info` 获取当前用户信息
- `PUT /api/user/update` 更新用户信息
- `PUT /api/user/password` 修改密码

### 新闻相关

- `GET /api/news/categories` 获取分类
- `GET /api/news/list` 获取新闻分页列表
- `GET /api/news/detail` 获取新闻详情与相关推荐
- `GET /api/news/recommend` 获取个性化推荐列表

### 收藏相关

- `GET /api/favorite/check` 检查是否已收藏
- `POST /api/favorite/add` 添加收藏
- `DELETE /api/favorite/remove` 取消收藏
- `GET /api/favorite/list` 获取收藏列表
- `DELETE /api/favorite/clear` 清空收藏

### 历史记录

- `POST /api/history/add` 新增浏览历史
- `GET /api/history/list` 获取历史记录
- `DELETE /api/history/delete/{history_id}` 删除单条历史
- `DELETE /api/history/clear` 清空历史

### 管理端

- `POST /api/admin/login` 管理员登录
- `GET /api/admin/users` 分页查询用户
- `GET /api/admin/news` 分页查询新闻
- `GET /api/admin/users/login-streak` 查询连续登录用户
- `GET /api/admin/news/favorite-ranking` 查询新闻收藏排行

## 设计说明

### 1. 分层结构清晰

项目采用 `routers -> crud -> models/schemas` 的分层方式：

- `routers` 负责参数接收、鉴权依赖注入和响应组织
- `crud` 负责具体 SQL/ORM 查询逻辑
- `models` 负责数据库建模
- `schemas` 负责输入输出数据校验

这种拆分方式便于后续继续接入服务层、单元测试和更多业务模块。

### 2. 数据分析能力不是“写接口壳子”

连续登录统计不是简单 `count(*)`，而是通过窗口函数识别同一用户的连续日期区间，再筛出满足阈值的用户。这个实现更接近真实业务统计场景，能体现 SQL 能力和数据建模意识。

### 3. 缓存策略聚焦热点读请求

当前已对以下接口增加 Redis 缓存：

- 新闻分类列表
- 按分类分页查询新闻列表

缓存 Key 设计中包含分类和分页维度，兼顾命中率与数据隔离。

### 4. 会话设计偏服务端可控

项目没有直接使用 JWT，而是将 Token 持久化到数据库：

- 用户端对应 `user_token`
- 管理端对应 `admin_token`

这种方式虽然比纯 JWT 多一次查询，但在实习项目或中后台项目场景下更容易实现会话失效控制、过期管理和多角色隔离。

### 5. AI 推荐能力采用“可降级”设计

推荐服务优先使用 Qwen embedding 对新闻内容向量化，再结合用户历史记录与收藏行为生成兴趣画像，按语义相似度、分类偏好、热度、新鲜度进行混合排序。

- 当 `QWEN_API_KEY` 已配置且网络可达时，接口返回 AI 个性化推荐结果。
- 当未配置 Key、外部网络不可达或第三方调用失败时，接口自动退化为“行为偏好 + 热度/发布时间”的规则推荐，不会影响基础功能可用性。
- 新闻 embedding 会缓存到 `news_embedding` 表，避免重复请求大模型接口。
## 本地启动

### 运行环境

- Python 3.10+
- PostgreSQL 16+
- Redis 7+

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

项目当前默认从 `.venv/.env` 读取配置，因此需要先准备该文件：

```bash
mkdir -p .venv
cp .env.example .venv/.env
```

如果你在 Windows PowerShell 中执行，可以使用：

```powershell
New-Item -ItemType Directory -Path .venv -Force
Copy-Item .env.example .venv/.env
```

然后按需修改数据库与 Redis 连接串，默认示例为：

```env
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:123456@localhost:5432/review_backend
REDIS_URL=redis://localhost:6379/0
```

如果你要启用 AI 推荐，还需要补充 Qwen 相关配置：

```env
QWEN_API_KEY=your_dashscope_api_key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_EMBEDDING_MODEL=text-embedding-v4
AI_RECOMMENDATION_CANDIDATE_LIMIT=60
AI_RECOMMENDATION_PROFILE_HISTORY_LIMIT=12
AI_RECOMMENDATION_PROFILE_FAVORITE_LIMIT=12
AI_RECOMMENDATION_EMBEDDING_DIMENSIONS=1024
AI_RECOMMENDATION_REQUEST_TIMEOUT=30
```

### 3. 执行数据库迁移

```bash
alembic upgrade head
```

本次新增推荐功能后，迁移会额外创建 `news_embedding` 表，用于缓存新闻向量。

### 4. 启动服务

```bash
uvicorn main:app --reload
```

启动后可访问：

- Swagger 文档：`http://127.0.0.1:8000/docs`
- 根路径测试：`http://127.0.0.1:8000/`

## Docker Compose 启动

项目已经提供容器化配置，可直接一键拉起应用、PostgreSQL 和 Redis：

```bash
docker-compose up --build
```

容器启动命令中会自动执行：

```bash
alembic upgrade head
```

适合演示部署能力或快速搭建联调环境。

如果需要在 Docker Compose 中启用 AI 推荐，请为 `app` 服务额外注入以下环境变量：

```yaml
QWEN_API_KEY: your_dashscope_api_key
QWEN_BASE_URL: https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_EMBEDDING_MODEL: text-embedding-v4
```

## AI 推荐接口说明

### 推荐逻辑

- 读取用户最近浏览历史与收藏记录，生成兴趣画像
- 为新闻内容构建 embedding，并缓存到数据库
- 按语义相似度、分类偏好、热度、发布时间综合排序
- 如果 AI 服务不可用，自动回退为规则推荐

### 请求示例

```http
GET /api/news/recommend?limit=10
Authorization: Bearer <user_token>
```

### 响应特点

- 每条推荐结果会返回 `score`
- 每条推荐结果会返回 `reason`，说明推荐原因
- 顶层会返回 `profileSource`，标识本次使用的是 `qwen_embedding` 还是回退策略

## 管理员初始化

仓库当前未内置管理员种子数据，首次启动后需要手动插入一条管理员记录。

可直接执行以下 SQL：

```sql
INSERT INTO admin (username, password, nickname, is_active, updated_time)
VALUES (
  'admin',
  '$2b$12$5wpBOAdJuc903GV1jZZHouY0.Smpzu6HOmkqrBSsyWUwVXIgxCZpm',
  '系统管理员',
  true,
  NOW()
);
```

对应登录信息为：

- 用户名：`admin`
- 密码：`Admin123456`

如果你想自定义密码，也可以使用项目中的 `utils/security.py` 生成 bcrypt 哈希后再写入数据库。



## 项目总结

这个项目的价值不只在于“把接口写出来”，而在于已经具备了一个中小型资讯平台后端的基础形态：

- 有清晰的数据模型与索引设计
- 有用户行为沉淀与运营统计能力
- 有缓存、迁移、容器化这些工程化能力
- 有继续往后台看板、推荐、埋点分析方向扩展的空间

如果你准备用它投暑期实习，这个项目比较适合被描述为：

> 基于 FastAPI / PostgreSQL / Redis 独立设计并开发资讯平台后端，完成用户端与管理端核心接口，落地登录留痕、连续登录统计、收藏排行、Redis 缓存、Alembic 迁移及 Docker Compose 部署。
