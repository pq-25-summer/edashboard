# 软件工程课看板系统

一个用于分析和查看学员们学习情况的看板系统。

## 项目概述

本系统通过分析各个小组的GitHub项目进度，包括学员们的代码提交、issue、文档等工作来评估工作的贡献和质量。

## 技术架构

### 后端 (Python)
- **FastAPI** - Web框架
- **psycopg3** - PostgreSQL数据库驱动
- **pydantic** - 数据验证
- **GitHub API** - 获取项目数据

### 前端 (React)
- **React** - UI框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **React Bootstrap** - UI组件库
- **ECharts for React** - 数据可视化

### 基础设施
- **PostgreSQL** - 数据库
- **Kubernetes** - 容器编排（替代docker-compose）

## 项目结构

```
edashboard/
├── backend/           # Python FastAPI后端
├── frontend/          # React TypeScript前端
├── k8s/              # Kubernetes配置文件
├── docs/             # 项目文档
└── README.md         # 项目说明
```

## 快速开始

### 环境配置

#### 开发环境
1. **快速配置（推荐）**：
```bash
cd scripts
python setup_env.py
```

2. **手动配置**：
```bash
cd backend
cp env.example .env
# 编辑 .env 文件，配置GitHub token等环境变量
```

详细配置说明请参考 [环境配置文档](docs/environment-setup.md)

#### 生产环境
参考 `k8s/README.md` 进行Kubernetes部署。

### 后端开发
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

## 功能特性

- GitHub项目数据同步
- 学员学习进度分析
- 代码提交统计
- Issue和PR分析
- 可视化数据展示 