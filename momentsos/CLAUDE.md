# momentsos/
> L2 | 父级: ../CLAUDE.md

成员清单
__init__.py: 暴露稳定版本号，不加载运行时依赖
__main__.py: 将 `python -m momentsos` 转发到命令行入口
cli.py: 编排 init、paths、doctor、prompt、generate；提示词与草稿只写运行目录
config.py: 定义默认设置与用户模板；初始化只补缺失文件，永不覆盖用户内容
context.py: 只读采集核心 Markdown、每日文件、目录和 LifeOS 时间段；单个可选来源失败时降级告警
prompts.py: 构建数据隔离提示词；解析 JSON 并验证候选数量与结构
providers.py: 提供 manual 与 OpenAI 兼容接口；远端地址必须显式允许上传上下文

依赖方向：cli → {config, context, prompts, providers}；context → config；prompts 与 providers 保持独立。

[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
