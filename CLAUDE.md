# MomentsOS - 本地上下文生成朋友圈草稿的开源框架
Python 3.9+ 标准库 + OpenAI 兼容 HTTP 接口 + Markdown 上下文；运行数据与仓库分离，默认不调用模型。

<directory>
momentsos/ - 运行代码：配置、只读采集、提示词、模型边界与命令行
docs/ - 中文使用手册：安装、上下文、模型选择与隐私边界
examples/ - 无密钥的配置样例
scripts/ - 安装入口与发布前隐私扫描
tests/ - 零网络核心回归
assets/ - MomentsOS 正式 Logo 的 SVG 与 PNG
.github/ - GitHub Actions 回归与隐私发布门禁
</directory>

<config>
pyproject.toml - 包元数据与 momentsos 命令入口
.gitignore - 隔离密钥、数据库、每日上下文、输出与运行记录
README.md - 默认中文入口
README_EN.md - 英文入口
SECURITY.md - 漏洞与隐私泄露报告方式
</config>

运行数据默认位于 `~/.momentsos/`。仓库不包含任何作者上下文、发布记录、私有路径、令牌或数据库。

[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
