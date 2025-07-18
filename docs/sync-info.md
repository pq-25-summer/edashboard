# 数据写入

编写一个 python 脚本，将 scripts/projects.txt 中的项目列表和 scripts/students.txt 中的学生列表写入数据库。要点：
- 如果可以从 API 提交而非直接写入数据库，就通过 API 提交，将来这个脚本可能用于向 k8s 中的项目实例提交数据
- 使用后端项目的 venv
- 如果需要 http 请求，使用 httpx
- 我已经在本地运行了前后端项目，未来如果需要像 k8s 提交数据，我也会单独启动，因此仅关注后端在 localhost:8000 ，前端在  localhost:5173 即可