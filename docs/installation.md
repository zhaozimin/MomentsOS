# 安装教程

MomentsOS 只需要 Python 3.9+。它不需要 Node.js，也不会安装数据库服务。

## 1. macOS / Linux 一键安装

```bash
git clone https://github.com/zhaozimin/MomentsOS.git
cd MomentsOS
./scripts/install.sh
```

安装脚本只做三件事：

1. 在仓库内创建 `.venv`。
2. 把当前源码安装进这个隔离环境。
3. 在 `~/.momentsos/` 创建缺失的安全模板。

脚本不会覆盖已存在的 `settings.json`、`profile.md`、`voice.md` 或 `rules.md`。

## 2. Windows 或手工安装

PowerShell：

```powershell
git clone https://github.com/zhaozimin/MomentsOS.git
cd MomentsOS
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install .
.\.venv\Scripts\momentsos init
.\.venv\Scripts\momentsos paths
```

macOS / Linux 的等价手工命令：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/momentsos init
```

## 3. 选择运行目录

默认目录是：

```text
~/.momentsos
```

如果你需要放到加密磁盘或其他目录，先设置环境变量，再初始化：

```bash
export MOMENTSOS_HOME="/你的安全目录/MomentsOS"
.venv/bin/momentsos init
```

不要把 `MOMENTSOS_HOME` 指向 Git 仓库。运行目录包含真实上下文和完整提示词。

## 4. 初始化上下文

运行：

```bash
.venv/bin/momentsos paths
```

按输出路径填写：

1. `profile.md`：只写允许模型知道的稳定事实。
2. `voice.md`：只放你亲手写过且允许读取的公开文本。
3. `rules.md`：写明禁区、事实标准与表达规则。
4. `daily/YYYY-MM-DD.md`：每天生成前更新。

## 5. 第一次运行

```bash
.venv/bin/momentsos doctor
.venv/bin/momentsos prompt
.venv/bin/momentsos generate
```

默认 `manual` 模式不会调用模型。`generate` 会打印提示词文件路径。先打开并检查这个文件，再决定交给哪个模型。

## 6. 更新

```bash
git pull --ff-only
.venv/bin/python -m pip install .
```

更新不会触碰 `~/.momentsos/`。即使如此，也应定期备份该目录。

## 7. 常见问题

### `doctor` 显示“文件不存在”

检查 `settings.json` 中启用的来源。未使用的来源应设置 `"enabled": false`。

### 本地模型连接失败

先确认本地模型服务正在运行，再检查 `base_url` 是否包含它的 OpenAI 兼容 `/v1` 根路径。

### 云端模型被拒绝

这是隐私闸门。阅读[模型选择指南](models.md)与[隐私说明](privacy.md)后，只有在接受完整上下文离开电脑时，才设置 `"allow_cloud_context": true`。

### 找不到每日上下文

不要猜路径。运行 `momentsos paths`，并使用它显示的 `YYYY-MM-DD.md` 位置。

[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
