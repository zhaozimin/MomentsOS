# 上下文教程

MomentsOS 不知道你是谁，也不会监听屏幕。草稿质量只取决于你主动提供的上下文。

## 一、固定上下文

运行 `momentsos init` 后会得到三个文件：

### `context/profile.md`

写稳定事实，不写临时状态。

```markdown
# 我是谁

- 我的公开职业：独立开发者。
- 我正在公开建设：产品 A。
- 读者通常关心：本地优先工具与工作方法。

## 不可公开

- 客户名称、未发布收入、住址和联系方式。
```

### `context/voice.md`

放 3～10 条你亲手写过的公开文字。它们只用于学习语气，不是事实来源。不要放他人的聊天记录。

### `context/rules.md`

写不可违反的边界。规则必须短、明确、可检查。

```markdown
1. 计划不能写成已经完成。
2. 未公开产品不写名称。
3. 不引用家人、客户或朋友的原话。
4. 每条只讲一件事。
```

## 二、每天更新的位置

默认位置是：

```text
~/.momentsos/context/daily/YYYY-MM-DD.md
```

每天生成前建立当天文件。例如：

```markdown
# 2026-10-07

## 已经发生

- 完成开源仓库的安装教程。
- 下午散步 35 分钟。

## 我的观察

- 真正难的不是多写功能，而是把隐私边界做成默认值。

## 计划，不得写成结果

- 明天准备邀请两位朋友测试安装流程。

## 不确定，不得写进正文

- 下载次数还没有核对。
```

默认读取今天和前两天，共三天。修改 `context.lookback_days` 可以调整窗口。

如果你改变了 `context.daily_dir`，新目录就是每日更新位置。任何时候都可以运行：

```bash
momentsos paths
```

## 三、接入言壤

[言壤 · VoiceLog](https://github.com/zhaozimin/VoxTerra) 把本地语音转成 Markdown。先在言壤菜单中确认“保存位置”，再把下面的来源加入 `settings.json` 的 `context.sources`：

```json
{
  "name": "言壤 VoiceLog",
  "type": "markdown_dir",
  "enabled": true,
  "path": "/替换为你在言壤中选择的保存目录",
  "glob": "**/*.md",
  "lookback_days": 1,
  "max_files": 5
}
```

MomentsOS 只读最近一天、最多五个匹配文件。它不会改变言壤配置，也不会写回日志。

注意：目录来源会读取匹配到的文件。请把言壤保存到独立目录，不要把整个 Obsidian 仓库作为来源。

## 四、接入 LifeOS

[LifeOS](https://github.com/zhaozimin/LifeOS) 默认只监听本机。把下面的来源加入 `context.sources`：

```json
{
  "name": "LifeOS",
  "type": "lifeos",
  "enabled": true,
  "base_url": "http://127.0.0.1:59418",
  "token_env": "LIFEOS_TOKEN",
  "timeout_seconds": 10
}
```

然后在启动 MomentsOS 的同一个终端设置 LifeOS 访问令牌：

```bash
export LIFEOS_TOKEN="你的本机令牌"
```

令牌不得写进 `settings.json`，也不得提交到 Git。MomentsOS 只调用时间段读取接口，不修改 LifeOS 的时间或财务账本。

如果你的 LifeOS 安装方式没有要求令牌，可以不设置该环境变量。不要为了省一步而把令牌硬编码进配置。

## 五、接入其他 Markdown

单文件：

```json
{
  "name": "公开项目周报",
  "type": "markdown_file",
  "enabled": true,
  "path": "/你的目录/weekly.md"
}
```

目录：

```json
{
  "name": "灵感箱",
  "type": "markdown_dir",
  "enabled": true,
  "path": "/你的目录/ideas",
  "glob": "*.md"
}
```

只接入独立、边界清晰的目录。不要把用户主目录、完整聊天备份或整个知识库交给通配符。

## 六、上下文写作原则

1. 写事实，不写模型应该如何猜测。
2. 把“已经发生”“计划”“不确定”分开。
3. 精确数字必须有来源。
4. 他人原话默认不进入上下文。
5. 文风样本与事实来源分开。
6. 生成前打开 `runs/` 中的提示词抽查。
7. 用 `max_total_chars` 限制单次发送的上下文总量。

[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
