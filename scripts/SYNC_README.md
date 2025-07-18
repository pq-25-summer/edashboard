# 数据同步脚本使用说明

## 功能概述

`sync_data.py` 脚本用于将 `projects.txt` 和 `students.txt` 中的数据通过API写入数据库。

## 前置条件

1. **后端服务运行中**: 确保后端API服务在 `http://localhost:8000` 运行
2. **数据文件存在**: 确保 `projects.txt` 和 `students.txt` 文件存在
3. **Python环境**: 使用后端的虚拟环境

## 安装依赖

```bash
# 进入后端目录
cd ../backend

# 激活虚拟环境（如果有的话）
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install httpx
```

## 使用方法

### 1. 基本使用

```bash
# 从scripts目录运行
python sync_data.py
```

### 2. 预览模式（推荐先运行）

```bash
# 预览将要同步的数据，不会实际写入数据库
python sync_data.py --dry-run
```

### 3. 自定义参数

```bash
# 指定API地址
python sync_data.py --api-url http://localhost:8000

# 指定文件路径
python sync_data.py --projects-file projects.txt --students-file students.txt

# 组合使用
python sync_data.py --dry-run --api-url http://localhost:8000
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--api-url` | `http://localhost:8000` | API服务器地址 |
| `--projects-file` | `projects.txt` | 项目文件路径 |
| `--students-file` | `students.txt` | 学生文件路径 |
| `--dry-run` | `False` | 预览模式，不实际写入数据库 |

## 数据格式要求

### projects.txt
```
项目名称\tGitHub仓库URL
```

示例：
```
PQ-Project	https://github.com/Liangyu-Sun
popquiz-project	https://github.com/3241672910
```

### students.txt
```
学生姓名\tGitHub用户名\tGitHub个人主页URL
```

示例：
```
何佳骏	waitlili414	https://github.com/waitlili414
俞俊杉	Yujunshan	https://github.com/Yujunshan
```

## 功能特性

### 1. 智能匹配
- 自动将学生匹配到对应的项目
- 基于GitHub URL中的用户名进行匹配
- 支持手动调整匹配关系

### 2. 重复检查
- 检查项目是否已存在（基于项目名称）
- 检查学生是否已存在（基于学生姓名）
- 跳过已存在的数据，避免重复创建

### 3. 错误处理
- 网络连接异常处理
- API响应错误处理
- 文件格式验证
- 详细的错误日志

### 4. 进度显示
- 实时显示创建进度
- 成功/失败状态标识
- 最终统计信息

## 使用流程

### 1. 准备数据
确保已经运行了 `get_repos.py` 生成了数据文件：
```bash
python get_repos.py
```

### 2. 预览数据
先运行预览模式查看将要同步的数据：
```bash
python sync_data.py --dry-run
```

### 3. 执行同步
确认数据无误后，执行实际同步：
```bash
python sync_data.py
```

### 4. 验证结果
访问前端页面验证数据是否正确导入：
- 项目列表: http://localhost:5173/projects
- 学生列表: http://localhost:5173/students

## 故障排除

### 1. 连接失败
```
❌ 无法连接到API服务器，请确保后端服务正在运行
```
**解决方案**: 确保后端服务在 `http://localhost:8000` 运行

### 2. 文件不存在
```
❌ 项目文件不存在: projects.txt
```
**解决方案**: 确保在正确的目录下运行，或指定正确的文件路径

### 3. 数据格式错误
```
⚠️  警告: 第X行格式不正确
```
**解决方案**: 检查数据文件格式，确保使用制表符分隔

### 4. API错误
```
❌ 创建项目失败: 项目名称 - 400: 错误信息
```
**解决方案**: 检查API响应，可能需要调整数据格式或处理特殊字符

## 注意事项

1. **备份数据**: 建议在同步前备份数据库
2. **网络稳定**: 确保网络连接稳定，避免同步中断
3. **API限制**: 脚本包含请求间隔，避免API限制
4. **数据验证**: 建议先使用 `--dry-run` 模式验证数据
5. **权限检查**: 确保有足够的权限访问API和文件

## 扩展功能

### 自定义匹配逻辑
可以修改 `match_students_to_projects` 方法来实现自定义的学生-项目匹配逻辑。

### 批量更新
可以扩展脚本支持批量更新现有数据。

### 数据导出
可以添加功能将数据库中的数据导出为文件格式。

## 示例输出

```
🚀 开始数据同步...
✅ API连接正常
📖 从 projects.txt 读取到 24 个项目
📖 从 students.txt 读取到 80 个学生
📊 现有项目: 0 个
👥 现有学生: 0 个
✅ 创建项目成功: PQ-Project (ID: 1)
✅ 创建项目成功: popquiz-project (ID: 2)
...
✅ 创建学生成功: 何佳骏 (@waitlili414) (ID: 1)
✅ 创建学生成功: 俞俊杉 (@Yujunshan) (ID: 2)
...

✅ 同步完成!
📊 创建项目: 24 个
👥 创建学生: 80 个
``` 