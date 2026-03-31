<div align="center">

<img src="https://img.shields.io/badge/Orin.LAB-AI%20Research%20Lab-cyan?style=for-the-badge&labelColor=0d1117" alt="Orin.LAB" />

# Orin.LAB

**AI Research Lab for Crypto Markets**

*Reads the market. Signals the moves. Posts the alpha.*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4+-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Rust](https://img.shields.io/badge/Rust-1.76+-CE422B?style=flat-square&logo=rust&logoColor=white)](https://rust-lang.org)
[![Go](https://img.shields.io/badge/Go-1.22+-00ADD8?style=flat-square&logo=go&logoColor=white)](https://go.dev)
[![Solana](https://img.shields.io/badge/Solana-Mainnet-9945FF?style=flat-square&logo=solana&logoColor=white)](https://solana.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![CI](https://github.com/nujar00t/Orin.LAB/actions/workflows/ci.yml/badge.svg)](https://github.com/nujar00t/Orin.LAB/actions)
[![CodeQL](https://github.com/nujar00t/Orin.LAB/actions/workflows/codeql.yml/badge.svg)](https://github.com/nujar00t/Orin.LAB/actions)

</div>

---

## What is Orin.LAB?

Orin.LAB is an open-source, multi-language AI research lab for crypto markets — built on Solana and powered by Claude AI.

It connects **on-chain data**, **AI reasoning**, and **automated distribution** into a single, modular toolkit:

- 🤖 **Telegram bot** that answers market questions, analyzes chart photos, and delivers signals in real time
- 📊 **Signal engine** with pure-Python TA (RSI, MACD, Bollinger Bands, EMA, ATR) — no external TA libraries
- 🐋 **Whale tracker** that monitors large Solana wallets and fires instant alerts on big moves
- 🐦 **Auto poster** that generates natural, human-style posts ready for Twitter/X
- 📈 **Live dashboard** for real-time price and signal monitoring in the terminal
- ⚡ **High-performance core** written in Rust for heavy computation

> *"Orin.LAB doesn't predict. It researches, signals, and acts."*

---

## Install

```bash
pip install orinlab
```

That's it. No cloning, no manual config files.

---

## Quickstart

```bash
# 1. Install
pip install orinlab

# 2. Setup — interactive wizard, takes ~1 minute
orinlab setup

# 3. Run
orinlab bot        # Telegram AI bot
orinlab signal     # Signal engine (terminal)
orinlab posts SOL  # Generate posts for $SOL
orinlab dashboard  # Live terminal dashboard
```

### What `orinlab setup` looks like

```
Step 1 — AI Provider
  1 Anthropic (Claude)
  2 DeepInfra (free tier)
Choose provider: 2
DeepInfra API key: ••••••••

Step 2 — Telegram Bot
Telegram bot token: ••••••••

Step 3 — Solana (optional)
Configure Solana wallet tracking? [y/N]

Step 4 — Twitter/X Auto Poster (optional)
Configure Twitter/X posting? [y/N]

✓ Setup complete! Config saved to ~/.orinlab/.env
  orinlab bot      — start Telegram bot
  orinlab signal   — signal engine
```

Config is saved to `~/.orinlab/.env` — edit anytime to update keys.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Orin.LAB                         │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                  │
│  │ Telegram Bot │    │ Signal Engine│                   │
│  │   (Python)   │    │   (Python)   │                   │
│  └──────┬───────┘    └──────┬───────┘                   │
│         │                   │                           │
│         └─────────┬─────────┘                           │
│                   ▼                                     │
│          ┌────────────────┐                             │
│          │   Claude AI    │  ← Anthropic / DeepInfra    │
│          │  (Haiku/Sonnet)│                             │
│          └────────┬───────┘                             │
│                   │                                     │
│         ┌─────────┴──────────┐                          │
│         ▼                    ▼                          │
│  ┌─────────────┐    ┌────────────────┐                  │
│  │ Auto Poster │    │  On-chain Agent│                   │
│  │ (TypeScript)│    │   (Python)     │                   │
│  └──────┬──────┘    └───────┬────────┘                  │
│         │                   │                           │
│         ▼                   ▼                           │
│    Twitter/X           Solana RPC                       │
│                      (CoinGecko API)                    │
└─────────────────────────────────────────────────────────┘
```

---

## Modules

| Module | Language | Description |
|--------|----------|-------------|
| [**Telegram Bot**](bot/) | Python | AI-powered bot — market Q&A, signal delivery, chart photo analysis |
| [**Signal Engine**](agents/signal_engine.py) | Python | BUY/SELL/HOLD signals with confidence score and risk level |
| [**Technical Analysis**](agents/technical_analysis.py) | Python | RSI, MACD, BB, EMA, ATR — pure Python, no TA libraries |
| [**Market Analyst**](agents/market_analyst.py) | Python | Deep multi-factor market analysis using Claude Sonnet |
| [**On-chain Agent**](agents/onchain_agent.py) | Python | Solana wallet monitoring, transaction parsing |
| [**Whale Tracker**](agents/whale_tracker.py) | Python | Monitors large wallets, alerts on $50k+ moves |
| [**Alert Manager**](agents/alert_manager.py) | Python | Async threshold-based alert dispatcher |
| [**Post Writer**](agents/post_writer.py) | Python | Natural human-style post generator for Twitter/X |
| [**Signal History**](agents/signal_history.py) | Python | Append-only JSON signal log with stats and filters |
| [**Dashboard**](agents/dashboard.py) | Python | Live terminal dashboard with Rich layout |
| [**Auto Poster**](poster/) | TypeScript | Automated signal posting to Twitter/X |
| [**Solana SDK**](sdk/) | TypeScript | On-chain data fetcher — prices, wallets, transactions |
| [**Signal CLI**](cli/) | Go | Lightweight CLI for terminal-native signal checks |
| [**Core SDK**](core/) | Rust | High-performance signal computation and data processing |

---

## Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome screen with quick-action keyboard |
| `/signal $TOKEN` | BUY/SELL/HOLD signal with confidence score |
| `/ta $TOKEN` | Full technical analysis — RSI, MACD, BB, EMA |
| `/analyze $TOKEN` | Deep AI market analysis (Claude Sonnet) |
| `/post $TOKEN` | Generate a ready-to-copy Twitter/X post |
| `/history` | Last 10 signals generated |
| `/help` | Show all commands |

**Send a chart photo** → instant AI chart analysis with signal, key levels, and pattern recognition.

---

## AI Providers

Orin.LAB supports multiple AI backends — switch with one env var:

| Provider | Setup | Notes |
|----------|-------|-------|
| **Anthropic** | `ANTHROPIC_API_KEY` | Best quality, Claude Haiku/Sonnet |
| **DeepInfra** | `DEEPINFRA_API_KEY` | Free tier available, Llama 3.1 70B |
| **OpenAI** | `OPENAI_API_KEY` | Any OpenAI-compatible endpoint |
| **OpenRouter** | `OPENAI_API_KEY` + `OPENAI_BASE_URL` | Access to 100+ models |

```env
# Switch provider in ~/.orinlab/.env
AI_PROVIDER=deepinfra
DEEPINFRA_API_KEY=your_key
DEEPINFRA_MODEL=meta-llama/Meta-Llama-3.1-70B-Instruct
```

---

## For Developers

Clone and run locally:

```bash
git clone https://github.com/nujar00t/Orin.LAB.git
cd Orin.LAB
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
py orin.py signal
```

### Run tests

```bash
pytest tests/ -v
# With coverage
pytest tests/ --cov=utils --cov=agents --cov-report=term-missing
```

### Project Structure

```
Orin.LAB/
├── orinlab/            ← installable package entry point
│   ├── cli.py          ← orinlab command
│   └── __main__.py
├── cli_setup.py        ← interactive setup wizard
├── orin.py             ← dev entry point
├── bot/                ← Telegram bot
├── agents/             ← all AI agents and tools
├── utils/              ← shared utilities (cache, rate limiter, logger, config)
├── poster/             ← TypeScript auto poster
├── sdk/                ← TypeScript Solana SDK
├── cli/                ← Go signal CLI
├── core/               ← Rust core SDK
├── tests/              ← Python unit tests (35+ tests)
├── docs/               ← GitHub Pages landing page
└── .github/            ← CI/CD, CodeQL, issue templates
```

### Branches

| Branch | Purpose |
|--------|---------|
| `main` | Stable, production-ready |
| `develop` | Integration branch |
| `feature/*` | New features |
| `hotfix/*` | Urgent fixes |

---

## Roadmap

### v1.0.0 — Foundation ✅
- [x] Telegram AI Bot with conversation history
- [x] Signal Engine with on-chain data + AI
- [x] Auto Poster (Twitter/X)
- [x] TypeScript Solana SDK, Go CLI, Rust Core
- [x] Full CI/CD + CodeQL + Dependabot

### v1.1.0 — Intelligence Layer ✅
- [x] Pure-Python TA engine (RSI, MACD, BB, EMA, ATR)
- [x] Whale Tracker — real-time large wallet monitoring
- [x] Chart photo analysis via Telegram
- [x] Signal history log
- [x] Alert Manager
- [x] Post Writer — natural human-style posts
- [x] `pip install orinlab` — one-line install

### v1.2.0 — Distribution
- [ ] Publish to PyPI (pip install orinlab globally)
- [ ] Web dashboard (Next.js)
- [ ] Signal history analytics
- [ ] Webhook support

### v2.0.0 — Multi-chain
- [ ] EVM support (Base, Arbitrum, Ethereum)
- [ ] Agent coordination layer
- [ ] Mobile app

---

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Follow [Conventional Commits](https://www.conventionalcommits.org/)
4. Open a PR against `develop`

---

## Security

Found a vulnerability? See [SECURITY.md](SECURITY.md). Do **not** open a public issue.

---

## Disclaimer

Orin.LAB is experimental software for research purposes.

- AI signals are **not financial advice**
- Always DYOR
- Never share your private key
- Use at your own risk

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

**Orin.LAB** · AI Research Lab for Crypto Markets

Built on [Solana](https://solana.com) · Powered by [Claude AI](https://anthropic.com)

`$ORNL` · [GitHub](https://github.com/nujar00t/Orin.LAB) · [Issues](https://github.com/nujar00t/Orin.LAB/issues)

</div>
