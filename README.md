# EnterpriseQA

一个适合入门学习的企业内部知识库问答 Agent 示例项目，采用 Flask + Vue3 + MySQL8 + LangChain + Ollama + Chroma。

## 项目结构

- `Server`：后端 Flask 服务、SQL 脚本、样例文档、向量索引目录
- `Client/enterprise-qa-web`：前端 Vue3 管理后台与问答界面

## 后端启动步骤

1. 进入 `Server`
2. 创建并激活 Python 虚拟环境
3. 安装依赖：`pip install -r requirements.txt`
4. 复制 `.env.example` 为 `.env`，按本地 MySQL / Ollama 实际情况修改
5. 在 MySQL 中依次执行：
   - `Server/sql/schema.sql`
   - `Server/sql/seed.sql`
6. 确保本地已启动 Ollama，并已拉取：
   - `qwen3:4b`
   - `qwen3-embedding:4b`
7. 首次导入测试数据后，执行向量重建：
   - `python scripts/rebuild_vectors.py`
8. 启动后端：
   - `python run.py`

默认服务地址：`http://127.0.0.1:5000`

## 前端启动步骤

1. 进入 `Client/enterprise-qa-web`
2. 安装依赖：`npm install`
3. 启动开发服务：`npm run dev`

默认前端地址：`http://127.0.0.1:5173`

## 默认测试账号

- 管理员：`admin / 123456`
- 普通用户：`zhangsan / 123456`
- 普通用户：`lisi / 123456`

密码按需求使用 MD5 存储，仅适合教学演示。

## 当前能力

- JWT 登录鉴权
- 管理员与普通用户角色区分
- 知识库创建
- 文档上传、切片、向量化与重建索引
- 基于 LangChain + Ollama + Chroma 的 RAG 问答
- 会话历史记录
- 管理后台统计卡片与 ECharts 图表
