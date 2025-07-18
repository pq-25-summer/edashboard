# 抓取项目列表

学员们已经将各组的项目链接提交到了 https://github.com/xinase/PQ/issues/3 。开发一个 Python 脚本，将项目列表和学生列表抓取下来。

- 这个脚本尽可能使用 github api 而非直接读取页面分析内容，这是为了尊重github的使用模式
- 脚本是一次性的，尽管有些逻辑可能还会在别出出现。
- 输出保存到文件projects.txt和students.txt，每项一行
- 如果需要 github token，告诉我如何配置，我会向你提供
- 使用httpx 而非 requests
- 生成的程序脚本放到项目根目录下的 scripts 子目录