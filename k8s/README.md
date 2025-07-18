# Kubernetes 部署说明

## 概述

本项目使用Kubernetes进行容器编排，支持开发环境和生产环境的不同配置。

## 环境差异

### 开发环境
- 数据库连接使用系统信任模式：`postgresql://localhost/edashboard`
- 无需密码认证，便于本地开发

### 生产环境 (Kubernetes)
- 数据库使用SCRAM-SHA-256认证
- 通过Secret管理敏感信息
- 完整的网络安全配置

## 部署步骤

### 1. 创建命名空间
```bash
kubectl apply -f namespace.yaml
```

### 2. 配置数据库
```bash
# 创建PostgreSQL配置
kubectl apply -f postgres-config.yaml
kubectl apply -f postgres-secret.yaml
kubectl apply -f postgres-pvc.yaml

# 部署PostgreSQL
kubectl apply -f postgres-deployment.yaml
kubectl apply -f postgres-service.yaml
```

### 3. 配置GitHub API
```bash
# 编辑github-secret.yaml，设置实际的GitHub token
# 将 <base64-encoded-github-token> 替换为实际的base64编码token
kubectl apply -f github-secret.yaml
```

### 4. 构建和推送Docker镜像
```bash
# 构建后端镜像
cd ../backend
docker build -t edashboard-backend:latest .

# 构建前端镜像
cd ../frontend
docker build -t edashboard-frontend:latest .

# 推送到镜像仓库（根据实际情况调整）
docker tag edashboard-backend:latest your-registry/edashboard-backend:latest
docker tag edashboard-frontend:latest your-registry/edashboard-frontend:latest
docker push your-registry/edashboard-backend:latest
docker push your-registry/edashboard-frontend:latest
```

### 5. 部署应用
```bash
# 部署后端
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml

# 部署前端
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
```

### 6. 配置定时任务
```bash
kubectl apply -f github-sync-cronjob.yaml
```

### 7. 配置入口
```bash
# 编辑ingress.yaml，设置实际的域名
kubectl apply -f ingress.yaml
```

### 8. 一键部署（推荐）
```bash
# 使用kustomize进行一键部署
kubectl apply -k .
```

## 配置说明

### 数据库认证
- **开发环境**: 使用系统信任模式，无需密码
- **生产环境**: 使用SCRAM-SHA-256认证，通过Secret管理密码

### 网络安全
- PostgreSQL仅允许集群内部访问
- 前端通过LoadBalancer暴露
- API通过Ingress路由

### 资源限制
- 后端: 256Mi-512Mi内存，250m-500m CPU
- 前端: 128Mi-256Mi内存，100m-200m CPU
- PostgreSQL: 10Gi持久化存储

## 监控和日志

### 健康检查
- 后端: `/health` 端点
- 前端: `/` 端点
- PostgreSQL: 内置健康检查

### 日志
- 所有容器日志通过kubectl logs查看
- PostgreSQL日志配置为stderr输出

## 故障排除

### 常见问题
1. **数据库连接失败**: 检查Secret配置和网络策略
2. **GitHub同步失败**: 验证GitHub token权限
3. **前端无法访问后端**: 检查Ingress配置和Service

### 调试命令
```bash
# 查看Pod状态
kubectl get pods -n edashboard

# 查看日志
kubectl logs -f deployment/backend -n edashboard
kubectl logs -f deployment/frontend -n edashboard

# 进入容器调试
kubectl exec -it deployment/backend -n edashboard -- /bin/bash
```

## 扩展配置

### 水平扩展
```bash
# 扩展后端实例
kubectl scale deployment backend --replicas=3 -n edashboard

# 扩展前端实例
kubectl scale deployment frontend --replicas=3 -n edashboard
```

### 资源调整
编辑对应的deployment.yaml文件，调整resources配置。

### 自定义域名
编辑ingress.yaml文件，将`edashboard.local`替换为实际域名。 