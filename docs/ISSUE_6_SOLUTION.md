# Issue 6 解决方案报告

## 📋 Issue 描述

**Issue #6: 分离后台任务**

要求：
1. 将后端模块的定时任务去掉，不再使用schedule。它会阻塞访问。
2. 提供命令行入口，运行通过单独的python程序执行同步和分析任务，每个任务应有一个单独的执行脚本，我注意到原本github_sync.py有这个能力。
3. 为整个项目提供一个k8s编排，允许在本地的k8s环境完整的运行开发模式的后台任务、后端和前端以及数据库，这样我们可以建立一个一体化的开发用沙盒。
4. 在开发工作中，可以独立的执行单独的后台任务，更利于开发调试。

## ✅ 解决方案

### 1. 移除定时任务调度器

#### 1.1 修改主应用 (`backend/main.py`)

**移除调度器相关代码：**
- 删除 `start_background_scheduler` 和 `stop_background_scheduler` 调用
- 移除 `scheduler` 模块的导入
- 简化应用启动流程

#### 1.2 清理API路由中的分析逻辑

**修复analytics路由 (`backend/app/routers/analytics.py`):**
- 移除所有API端点中的 `analyzer.analyze_all_projects()` 调用
- 改为从数据库读取预计算的数据
- 添加提示信息，引导用户使用独立脚本

**修复project_status路由 (`backend/app/routers/project_status.py`):**
- 移除手动分析端点 `/analyze`
- 移除仓库更新端点 `/update-repos`
- 移除同步端点 `/sync`
- 移除分析专用端点 `/analysis-only`
- 移除调度器状态端点 `/scheduler/status`
- 所有端点返回400错误，提示使用独立脚本

#### 1.3 保留调度器模块 (`backend/app/scheduler.py`)

**保留但禁用自动启动：**
- 保留调度器代码以便将来需要时使用
- 移除自动启动逻辑
- 保留手动执行功能

### 2. 创建独立的命令行脚本

#### 2.1 数据同步脚本 (`scripts/sync_data.py`)

**功能特性：**
- 同步GitHub项目数据（提交、Issue）
- 更新本地仓库
- 分析项目状态
- 保存数据到数据库

**使用方法：**
```bash
cd scripts
python sync_data.py
```

#### 2.2 项目分析脚本 (`scripts/analyze_projects.py`)

**功能特性：**
- 仅执行项目状态分析
- 不更新本地仓库
- 生成分析报告
- 保存结果到数据库

**使用方法：**
```bash
cd scripts
python analyze_projects.py
```

#### 2.3 仓库更新脚本 (`scripts/update_repos.py`)

**功能特性：**
- 仅更新本地Git仓库
- 拉取最新代码
- 不执行分析任务

**使用方法：**
```bash
cd scripts
python update_repos.py
```

### 3. Kubernetes编排配置

#### 3.1 开发环境编排 (`k8s/dev-environment.yaml`)

**包含组件：**
- PostgreSQL数据库
- 后端API服务
- 前端Web服务
- 后台任务CronJob

#### 3.2 数据库配置 (`k8s/postgres-dev.yaml`)

**开发环境数据库：**
- 持久化存储
- 开发用配置
- 数据初始化

#### 3.3 服务编排 (`k8s/services-dev.yaml`)

**服务配置：**
- 后端API服务
- 前端Web服务
- 数据库服务
- 内部通信

### 4. 独立任务执行

#### 4.1 命令行工具 (`scripts/cli.py`)

**统一命令行接口：**
```bash
# 执行完整同步
python cli.py sync

# 仅执行分析
python cli.py analyze

# 仅更新仓库
python cli.py update

# 查看状态
python cli.py status
```

#### 4.2 任务状态管理

**状态跟踪：**
- 记录任务执行时间
- 保存执行结果
- 错误日志记录
- 性能监控

## 🚀 实现细节

### 1. 修改主应用启动

```python
# backend/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    await init_db()
    
    # Issue 6: 移除定时任务调度器，避免阻塞API访问
    # 后台任务现在通过独立的命令行脚本执行
    
    yield
    
    # 清理工作
    pass
```

### 2. 清理API路由分析逻辑

```python
# backend/app/routers/analytics.py
@router.get("/dashboard")
async def get_dashboard_data():
    """获取仪表板数据"""
    try:
        # Issue 6: 从数据库读取数据，不执行实时分析
        # 项目分析数据应该通过独立脚本预先计算并存储到数据库
        
        # 从数据库获取学生和项目信息
        async with db.get_db() as conn:
            # 获取项目统计
            project_count = await conn.fetchval("SELECT COUNT(*) FROM projects")
            # ... 其他数据库查询
```

### 3. 移除分析端点

```python
# backend/app/routers/project_status.py
@router.post("/analyze")
async def analyze_projects():
    """手动触发项目分析 - Issue 6: 已移除，请使用独立脚本"""
    raise HTTPException(
        status_code=400, 
        detail="此功能已移除。请使用独立脚本: python scripts/analyze_projects.py"
    )
```

### 4. 独立脚本结构

```
scripts/
├── sync_data.py          # 完整数据同步
├── analyze_projects.py   # 项目分析
├── update_repos.py       # 仓库更新
├── cli.py               # 统一命令行工具
├── test_issue6.py       # Issue 6实现测试
├── test_api_clean.py    # API清理测试
└── utils.py             # 共享工具函数
```

### 5. Kubernetes开发环境

```yaml
# k8s/dev-environment.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: edashboard-dev

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-dev
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend-dev
  template:
    metadata:
      labels:
        app: backend-dev
    spec:
      containers:
      - name: backend
        image: edashboard-backend:dev
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "postgresql://postgres:password@postgres-dev:5432/edashboard"
```

## 📊 使用流程

### 1. 开发环境启动

```bash
# 启动后端服务（不再包含分析逻辑）
cd backend
uvicorn main:app --reload

# 启动前端服务
cd frontend
npm run dev
```

### 2. 独立任务执行

```bash
# 执行完整同步
python scripts/sync_data.py

# 仅分析项目
python scripts/analyze_projects.py

# 使用统一CLI
python scripts/cli.py sync
```

### 3. 验证API清理

```bash
# 测试API是否不再执行分析
python scripts/test_api_clean.py

# 测试Issue 6实现
python scripts/test_issue6.py
```

### 4. Kubernetes开发环境

```bash
# 启动Kubernetes开发环境
kubectl apply -f k8s/dev-environment.yaml

# 检查服务状态
kubectl get pods -n edashboard-dev
```

### 5. 服务访问

```bash
# 后端API
curl http://localhost:8000/health

# 前端界面
open http://localhost:3000
```

## 🔧 配置说明

### 环境变量

```env
# 数据库配置
DATABASE_URL=postgresql://postgres:password@localhost:5432/edashboard

# GitHub配置
GITHUB_TOKEN=your_github_token_here

# 本地仓库配置
LOCAL_REPOS_DIR=/path/to/repos
```

### Kubernetes配置

```bash
# 创建命名空间
kubectl create namespace edashboard-dev

# 应用配置
kubectl apply -f k8s/

# 查看日志
kubectl logs -f deployment/backend-dev -n edashboard-dev
```

## 📝 总结

我们成功实现了Issue 6的所有要求：

1. ✅ **移除定时任务**: 不再使用schedule，避免阻塞API访问
2. ✅ **独立脚本**: 创建了多个独立的命令行脚本
3. ✅ **Kubernetes编排**: 提供完整的开发环境编排
4. ✅ **独立执行**: 支持单独执行后台任务，便于开发调试

### 主要改进

- **性能提升**: 移除阻塞的定时任务，API响应更快
- **开发便利**: 独立的脚本便于调试和测试
- **环境统一**: Kubernetes编排提供一致的开发环境
- **灵活性**: 支持按需执行不同任务

该解决方案为软件工程课看板系统提供了更好的开发体验和部署灵活性。 