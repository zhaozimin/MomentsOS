<div align="center">
  <img src="assets/logo.png" width="144" alt="MomentsOS Logo">

# MomentsOS

**Turn the facts of your day into social-post drafts you can review and rewrite.**

[简体中文](README.md) · [English](README_EN.md)

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-171b26?style=flat-square)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-171b26?style=flat-square)](LICENSE)
[![Local first](https://img.shields.io/badge/data-local--first-2ec671?style=flat-square)](docs/privacy.md)
</div>

---

MomentsOS is a **local-first open-source framework**. It turns Markdown you provide, optional [VoxTerra](https://github.com/zhaozimin/VoxTerra) voice logs, and optional [LifeOS](https://github.com/zhaozimin/LifeOS) time records into an auditable prompt for the model you choose.

This repository is a generic framework. It contains none of the author's persona, writing samples, posting history, databases, private paths, tokens, or production configuration.

> [!IMPORTANT]
> MomentsOS only creates drafts. It never publishes automatically. You remain responsible for facts, privacy, editing, and publication.

## Quick start

Python 3.9 or newer is required. On macOS or Linux:

```bash
git clone https://github.com/zhaozimin/MomentsOS.git
cd MomentsOS
./scripts/install.sh
.venv/bin/momentsos paths
```

Before generating, write the day's facts to:

```text
~/.momentsos/context/daily/YYYY-MM-DD.md
```

Then run:

```bash
.venv/bin/momentsos doctor
.venv/bin/momentsos generate
```

The default `manual` mode writes a prompt file and makes no network request. Give that file to a model you trust. See the [installation guide](docs/installation.md) for manual and Windows setup.

## Where context lives

Runtime data lives outside the repository, under `~/.momentsos/` by default:

| Path | Purpose | Update cadence |
| --- | --- | --- |
| `context/profile.md` | Identity, long-running projects, disclosure boundaries | When those facts change |
| `context/voice.md` | Public text written by you, used only as style evidence | Monthly or when your style changes |
| `context/rules.md` | Factual, privacy, and writing constraints | When a rule changes |
| `context/daily/YYYY-MM-DD.md` | Events, observations, results, and uncertainties for the day | **Before each day's generation** |
| `config/settings.json` | Model and source configuration | When adding a source or changing models |
| `runs/` | Full prompts before model submission | Generated; sensitive |
| `output/` | Candidate drafts | Generated; sensitive |

Run `momentsos paths` whenever you are unsure. It is the source of truth after changing `MOMENTSOS_HOME` or `context.daily_dir`.

## Choosing a model

Start with one question: **may this context leave your computer?**

| Mode | Use it when | Privacy boundary |
| --- | --- | --- |
| `manual` (default) | You want to inspect the prompt or use any chat product | The program stays offline; you decide what to paste |
| Local OpenAI-compatible server | The context is sensitive and your machine can run a model | Requests stay on `127.0.0.1` |
| Cloud OpenAI-compatible server | You prioritize writing quality and accept the provider's terms | The complete prompt is sent to the provider |

Choose a model with reliable Chinese writing, strict JSON output, a long context window, low hallucination, and strong instruction following. Test it on ten facts of your own: reject it if it invents details, leaks excluded information, or turns plans into completed events. A remote endpoint remains blocked until you explicitly set `allow_cloud_context` to `true`.

## VoxTerra and LifeOS

MomentsOS does not observe your life by itself. The author currently uses two local products as its context layer:

- [VoxTerra · VoiceLog](https://github.com/zhaozimin/VoxTerra) converts local speech to Markdown. MomentsOS reads the directory you selected in VoxTerra, without writing to it.
- [LifeOS](https://github.com/zhaozimin/LifeOS) records time and projects. MomentsOS reads its loopback API, without writing to either ledger.

Both integrations are disabled by default. Copy only the sources you need from [`examples/settings.integrations.json`](examples/settings.integrations.json), replace paths, and then set `enabled` to `true`. Keep tokens in environment variables, never in JSON.

## Commands

```bash
momentsos init       # create missing templates without overwriting user files
momentsos paths      # print exact context and output locations
momentsos doctor     # validate configuration and show source warnings
momentsos prompt     # build a prompt without calling a model
momentsos generate   # use the configured provider, or stay in manual mode
```

## Privacy baseline

- Repository and runtime data are physically separate.
- Context, prompts, outputs, secrets, and databases are ignored by Git.
- External sources are read-only.
- Remote endpoints are blocked until explicit consent is recorded.
- API keys are read from environment variables only.
- `python3 scripts/privacy_check.py` provides a release gate, not a substitute for human review.

See [Context](docs/context.md), [Model selection](docs/models.md), and [Privacy](docs/privacy.md). The detailed manuals are currently written in Chinese; contributions for full English manuals are welcome.

## Development

```bash
python3 -m unittest discover -s tests -v
python3 scripts/privacy_check.py
```

This is a usable open-source skeleton, not a mirror of the author's private production system.

## Context products used by the author

- [VoxTerra · VoiceLog](https://github.com/zhaozimin/VoxTerra) supplies speech-to-text context about what happened that day.
- [LifeOS](https://github.com/zhaozimin/LifeOS) supplies time, activity, and project context.

MomentsOS reads and organizes that context; it does not replace either recording system.

## License

[MIT](LICENSE) © 2026 zhaozimin
