# 项目克隆工具使用说明

## 概述

`clone_all.py` 是一个用于批量克隆学员项目的Python脚本。该脚本会读取 `projects.txt` 文件中的项目列表，并将所有项目克隆到指定的目录中。

## 功能特性

- ✅ 支持命令行参数指定目标目录
- ✅ 自动创建 `owner/repo` 目录结构避免同名冲突
- ✅ 详细的日志记录和进度显示
- ✅ 跳过已存在的项目目录
- ✅ 错误处理和超时控制
- ✅ 克隆结果统计和摘要

## 使用方法

### 基本用法

```bash
# 克隆所有项目到指定目录
python scripts/clone_all.py /path/to/repos

# 使用自定义项目文件
python scripts/clone_all.py /path/to/repos --projects-file custom_projects.txt
```

### 参数说明

- `target_dir`: 必需参数，指定克隆目标目录
- `--projects-file`: 可选参数，指定项目列表文件路径（默认为 `projects.txt`）

### 示例

```bash
# 克隆到当前目录下的 repos 文件夹
python scripts/clone_all.py ./repos

# 克隆到绝对路径
python scripts/clone_all.py /Users/username/student-projects

# 使用自定义项目文件
python scripts/clone_all.py ./repos --projects-file my_projects.txt
```

## 项目文件格式

脚本读取的项目文件格式为制表符分隔的文本文件：

```
项目名称	GitHub URL
```

示例：
```
llj-public	https://github.com/ldg-aqing/llj-public
PQ-Project	https://github.com/TeamCvOriented/PQ-Project
popquiz-project	https://github.com/kevinzhangzj710/popquiz-project
```

## 目录结构

克隆后的目录结构将按照 `owner/repo` 的方式组织：

```
target_dir/
├── ldg-aqing/
│   └── llj-public/
├── TeamCvOriented/
│   └── PQ-Project/
├── kevinzhangzj710/
│   └── popquiz-project/
└── ...
```

## 日志和输出

脚本会生成详细的日志信息：

- 控制台输出：实时显示克隆进度
- 日志文件：`clone_all.log` 包含完整的操作记录
- 摘要报告：显示成功/失败统计

示例输出：
```
2024-01-15 10:30:15 - INFO - 成功读取 25 个项目
2024-01-15 10:30:15 - INFO - 开始克隆 25 个项目到: /path/to/repos
2024-01-15 10:30:16 - INFO - 克隆仓库: https://github.com/ldg-aqing/llj-public -> /path/to/repos/ldg-aqing/llj-public
2024-01-15 10:30:20 - INFO - 成功克隆: /path/to/repos/ldg-aqing/llj-public
...
==================================================
克隆完成摘要:
总项目数: 25
成功克隆: 24
失败数量: 1
成功率: 96.0%
目标目录: /path/to/repos
==================================================
```

## 错误处理

脚本包含完善的错误处理机制：

- **网络超时**: 单个仓库克隆超时时间为5分钟
- **已存在目录**: 自动跳过已存在的项目目录
- **无效URL**: 记录错误并继续处理其他项目
- **权限问题**: 记录错误信息并提供解决建议

## 退出码

- `0`: 所有项目克隆成功
- `1`: 部分或全部项目克隆失败

## 注意事项

1. **网络连接**: 确保有稳定的网络连接访问GitHub
2. **磁盘空间**: 确保目标目录有足够的磁盘空间
3. **Git工具**: 确保系统已安装Git命令行工具
4. **权限**: 确保对目标目录有写入权限

## 故障排除

### 常见问题

1. **克隆失败**: 检查网络连接和GitHub仓库是否可访问
2. **权限错误**: 确保对目标目录有写入权限
3. **超时错误**: 网络较慢时可能需要更长的超时时间
4. **磁盘空间不足**: 检查可用磁盘空间

### 调试模式

可以通过查看日志文件 `clone_all.log` 获取详细的错误信息：

```bash
tail -f clone_all.log
```

## 扩展功能

脚本设计为可扩展的，未来可以添加：

- 并行克隆支持
- GitHub API认证
- 增量更新功能
- 更多输出格式
- Kubernetes环境支持 