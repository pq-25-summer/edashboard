# Issue 6 使用说明

## 概述

Issue 6 实现了后台任务的分离，移除了阻塞API访问的定时任务调度器，提供了独立的命令行脚本和Kubernetes编排，便于开发和调试。

## 主要改进

### 1. 移除定时任务调度器
- ✅ 不再使用 `schedule` 库，避免阻塞API访问
- ✅ API响应更快，用户体验更好
- ✅ 保留了调度器代码，便于将来需要时使用

### 2. 独立命令行脚本
- ✅ 每个任务都有独立的执行脚本
- ✅ 支持单独执行不同任务
- ✅ 便于开发和调试

### 3. Kubernetes编排
- ✅ 提供完整的开发环境
- ✅ 支持本地Kubernetes部署
- ✅ 一体化的开发沙盒

## 使用方法

### 1. 独立脚本使用

#### 1.1 完整数据同步
```bash
cd scripts
python sync_data.py
```
**功能**: 同步GitHub项目数据（提交、Issue）、更新本地仓库、分析项目状态

#### 1.2 仅执行项目分析
```bash
cd scripts
python analyze_projects.py
```
**功能**: 仅分析项目状态，不更新本地仓库

#### 1.3 仅更新仓库
```bash
cd scripts
python update_repos.py
```
**功能**: 仅更新本地Git仓库，拉取最新代码

#### 1.4 统一命令行工具
```bash
cd scripts

# 执行完整同步
python cli.py sync

# 仅执行分析
python cli.py analyze

# 仅更新仓库
python cli.py update

# 查看系统状态
python cli.py status

# 显示详细日志
python cli.py sync --verbose
```

### 2. Kubernetes开发环境

#### 2.1 环境准备
```bash
# 确保Kubernetes环境可用
kubectl version

# 创建命名空间
kubectl create namespace edashboard-dev
```

#### 2.2 配置GitHub Token
```bash
# 创建GitHub token的base64编码
echo -n "your_github_token_here" | base64

# 更新k8s/dev-environment.yaml中的github-secret-dev
# 将token字段设置为上面的base64编码
```

#### 2.3 构建Docker镜像
```bash
# 构建后端镜像
cd backend
docker build -t edashboard-backend:dev .

# 构建前端镜像
cd ../frontend
docker build -t edashboard-frontend:dev .
```

#### 2.4 部署开发环境
```bash
# 应用Kubernetes配置
kubectl apply -f k8s/dev-environment.yaml

# 检查部署状态
kubectl get pods -n edashboard-dev

# 查看服务状态
kubectl get services -n edashboard-dev
```

#### 2.5 访问服务
```bash
# 端口转发后端服务
kubectl port-forward service/backend-dev 8000:8000 -n edashboard-dev

# 端口转发前端服务
kubectl port-forward service/frontend-dev 3000:3000 -n edashboard-dev

# 访问前端界面
open http://localhost:3000

# 测试后端API
curl http://localhost:8000/health
```

### 3. 开发工作流

#### 3.1 日常开发
```bash
# 1. 启动后端服务（不包含定时任务）
cd backend
python main.py

# 2. 启动前端服务
cd frontend
npm run dev

# 3. 需要同步数据时，独立执行
cd scripts
python cli.py sync

# 4. 需要分析项目时，独立执行
python cli.py analyze
```

#### 3.2 调试特定任务
```bash
# 调试数据同步
python sync_data.py

# 调试项目分析
python analyze_projects.py

# 调试仓库更新
python update_repos.py

# 查看详细日志
python cli.py sync --verbose
```

#### 3.3 查看系统状态
```bash
# 查看数据统计
python cli.py status

# 查看日志文件
tail -f sync_data.log
tail -f analyze_projects.log
tail -f update_repos.log
```

## 配置说明

### 环境变量
```env
# 数据库配置
DATABASE_URL=postgresql://postgres:password@localhost:5432/edashboard

# GitHub配置
GITHUB_TOKEN=your_github_token_here
GITHUB_API_BASE_URL=https://api.github.com

# 本地仓库配置
LOCAL_REPOS_DIR=/Users/mars/jobs/pq/repos

# 应用配置
APP_NAME=软件工程课看板系统
DEBUG=true
```

### Kubernetes配置
- **命名空间**: `edashboard-dev`
- **数据库**: PostgreSQL 15
- **后端服务**: FastAPI应用
- **前端服务**: React应用
- **后台任务**: CronJob（每6小时执行一次）

## 故障排除

### 常见问题

#### 1. 脚本执行失败
```bash
# 检查Python路径
python -c "import sys; print(sys.path)"

# 检查依赖
pip install -r backend/requirements.txt

# 检查环境变量
echo $GITHUB_TOKEN
echo $DATABASE_URL
```

#### 2. Kubernetes部署失败
```bash
# 检查Pod状态
kubectl get pods -n edashboard-dev

# 查看Pod日志
kubectl logs -f deployment/backend-dev -n edashboard-dev

# 检查服务状态
kubectl get services -n edashboard-dev

# 检查配置
kubectl describe configmap backend-config-dev -n edashboard-dev
```

#### 3. 数据库连接失败
```bash
# 检查数据库服务
kubectl get pods -l app=postgres-dev -n edashboard-dev

# 查看数据库日志
kubectl logs -f deployment/postgres-dev -n edashboard-dev

# 测试数据库连接
kubectl exec -it deployment/postgres-dev -n edashboard-dev -- psql -U postgres -d edashboard
```

### 日志文件
- `sync_data.log` - 数据同步日志
- `analyze_projects.log` - 项目分析日志
- `update_repos.log` - 仓库更新日志
- `cli.log` - 命令行工具日志

## 性能优化

### 1. 脚本优化
- 使用异步操作提高性能
- 添加错误重试机制
- 优化数据库查询

### 2. Kubernetes优化
- 设置资源限制
- 使用持久化存储
- 配置健康检查

### 3. 监控和日志
- 记录任务执行时间
- 监控资源使用情况
- 设置告警机制

## 总结

Issue 6 的实现带来了以下好处：

1. **性能提升**: 移除阻塞的定时任务，API响应更快
2. **开发便利**: 独立的脚本便于调试和测试
3. **环境统一**: Kubernetes编排提供一致的开发环境
4. **灵活性**: 支持按需执行不同任务
5. **可维护性**: 清晰的代码结构和文档

通过这些改进，开发团队可以更高效地进行开发和调试工作。 