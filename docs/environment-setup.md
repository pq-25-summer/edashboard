# 环境配置说明

本文档说明如何配置开发和生产环境的敏感信息。

## 🔐 敏感信息管理

为了保护敏感信息（如GitHub token），我们使用以下策略：

1. **开发环境**: 使用 `.env` 文件
2. **生产环境**: 使用 Kubernetes Secrets
3. **版本控制**: 敏感文件不会被提交到代码库

## 🚀 快速配置

### 方法1: 使用配置脚本（推荐）

```bash
cd scripts
python setup_env.py
```

脚本会引导你完成配置过程。

### 方法2: 手动配置

#### 开发环境配置

1. 复制示例文件：
```bash
cd backend
cp env.example .env
```

2. 编辑 `.env` 文件，填入你的GitHub token：
```bash
# 数据库配置
DATABASE_URL=postgresql://localhost/edashboard

# GitHub API配置
GITHUB_TOKEN=your_github_token_here
GITHUB_API_BASE_URL=https://api.github.com

# 应用配置
APP_NAME=软件工程课看板系统
DEBUG=true

# 安全配置
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Kubernetes环境配置

1. 生成base64编码的token：
```bash
echo -n "your_github_token" | base64
```

2. 创建 `k8s/github-secret.yaml` 文件：
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: github-secret
  namespace: edashboard
type: Opaque
data:
  token: <base64-encoded-token>
```

## 🔑 GitHub Token获取

1. 访问 [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token (classic)"
3. 选择以下权限：
   - `repo` (完整的仓库访问权限)
   - `read:user` (读取用户信息)
4. 生成并复制token

## 📁 文件说明

| 文件 | 用途 | 是否提交到版本控制 |
|------|------|-------------------|
| `backend/.env` | 开发环境配置 | ❌ |
| `backend/env.example` | 配置示例 | ✅ |
| `k8s/github-secret.yaml` | K8s密钥配置 | ❌ |
| `scripts/setup_env.py` | 配置脚本 | ✅ |

## 🛡️ 安全注意事项

1. **永远不要提交敏感文件**：
   - `backend/.env`
   - `k8s/github-secret.yaml`

2. **定期轮换token**：
   - GitHub token有有效期限制
   - 建议定期更新token

3. **生产环境安全**：
   - 使用强密码和复杂的secret key
   - 启用HTTPS
   - 配置适当的防火墙规则

## 🔧 故障排除

### 问题1: GitHub API请求失败

**症状**: 401 Unauthorized 或 403 Forbidden

**解决方案**:
1. 检查token是否正确
2. 确认token有足够的权限
3. 验证token是否过期

### 问题2: 环境变量未加载

**症状**: `github_token` 为 None

**解决方案**:
1. 确认 `.env` 文件存在
2. 检查环境变量名称是否正确
3. 重启应用服务

### 问题3: Kubernetes secret未生效

**症状**: Pod无法读取secret

**解决方案**:
1. 检查secret是否正确创建：
   ```bash
   kubectl get secret github-secret -n edashboard
   ```
2. 确认deployment配置正确
3. 重启Pod：
   ```bash
   kubectl rollout restart deployment/backend -n edashboard
   ```

## 📞 获取帮助

如果遇到配置问题，请：

1. 检查本文档的故障排除部分
2. 查看应用日志
3. 联系项目维护者 