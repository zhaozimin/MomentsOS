# 模型选择指南

模型不是越大越合适。先确定隐私边界，再评估中文表达与事实纪律。

## 一、模型必须通过的五项检查

1. 能稳定理解中文长指令。
2. 能只输出合法 JSON。
3. 能引用来源编号，不凭空补细节。
4. 能区分事实、计划和不确定信息。
5. 能在你的上下文长度内保持一致。

建议准备十条带陷阱的事实做盲测：两条计划、两条不确定信息、一条隐私禁区和五条已发生事实。任何把计划写成结果、暴露禁区或虚构数字的模型都不合格。

## 二、三种模式

### 1. `manual`：默认

```json
{
  "model": {
    "provider": "manual"
  }
}
```

`momentsos generate` 只写出提示词文件。程序不联网。你可以先删减内容，再手动交给任意模型。

注意：当你把提示词粘贴到聊天产品时，内容仍会离开电脑。请阅读该产品的数据条款。

### 2. 本地 OpenAI 兼容模型

本地模型服务需要提供兼容的 `/v1/chat/completions` 接口。

```json
{
  "model": {
    "provider": "openai_compatible",
    "name": "填写本地模型名",
    "base_url": "http://127.0.0.1:11434/v1",
    "api_key_env": "MOMENTSOS_API_KEY",
    "allow_cloud_context": false,
    "timeout_seconds": 120,
    "temperature": 0.7,
    "json_mode": true
  }
}
```

优先选择中文能力强、支持较长上下文和 JSON 模式的指令模型。小模型适合整理明确事实；涉及文风模仿和九条差异化候选时，应使用更强模型。

### 3. 云端 OpenAI 兼容模型

先把密钥放入环境变量：

```bash
export MOMENTSOS_API_KEY="你的密钥"
```

再配置服务商地址、模型名和显式授权：

```json
{
  "model": {
    "provider": "openai_compatible",
    "name": "填写模型名",
    "base_url": "https://服务商地址/v1",
    "api_key_env": "MOMENTSOS_API_KEY",
    "allow_cloud_context": true,
    "timeout_seconds": 120,
    "temperature": 0.7,
    "json_mode": true
  }
}
```

`allow_cloud_context=true` 的含义很具体：`profile.md`、`voice.md`、`rules.md`、每日上下文和启用的外部来源会组合成提示词，并发送给该地址。

## 三、选择顺序

1. 上下文不能离机：选本地模型。
2. 上下文可以离机，但要逐次检查：选 `manual`。
3. 上下文可以离机，需要自动生成：选云端兼容接口。
4. 不确定：保持 `manual`，不要打开云端开关。

## 四、验收

修改配置后运行：

```bash
momentsos doctor
momentsos generate
```

检查输出：

- 数量是否正确。
- 每条能否追溯到 `source_ids`。
- `uncertainties` 是否真的没有进入正文。
- 是否出现上下文里没有的人、地点、金额或结果。
- 九条是否只是同一句话换词。

模型不合格时，先换模型或收紧上下文。不要用更多复杂提示词掩盖基本能力不足。

[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
