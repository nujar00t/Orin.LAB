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

- 🤖 **Telegram bot** that answers market questions and delivers signals in real time
- 📊 **Signal engine** that generates BUY/SELL/HOLD signals from live on-chain data
- 🐦 **Auto poster** that publishes alpha to Twitter/X automatically
- ⚡ **High-performance core** written in Rust for heavy computation
- 🔧 **Lightweight CLI** in Go for terminal-native signal checks

> *"Orin.LAB doesn't predict. It researches, signals, and acts."*

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
│          │   Claude AI    │  ← Anthropic API            │
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
│                      (Jupiter API)                      │
└─────────────────────────────────────────────────────────┘
```

---

## Modules

| Module | Language | Description |
|--------|----------|-------------|
| [**Telegram Bot**](bot/) | Python | AI-powered bot — market Q&A, signal delivery, inline keyboard |
| [**Signal Engine**](agents/signal_engine.py) | Python | BUY/SELL/HOLD signals with confidence score and risk level |
| [**Market Analyst**](agents/market_analyst.py) | Python | Deep multi-factor market analysis using Claude Sonnet |
| [**On-chain Agent**](agents/onchain_agent.py) | Python | Solana wallet monitoring, transaction parsing |
| [**Alert Manager**](agents/alert_manager.py) | Python | Async threshold-based alert dispatcher |
| [**Dashboard**](agents/dashboard.py) | Python | Live terminal dashboard with Rich layout |
| [**Auto Poster**](poster/) | TypeScript | Automated signal posting to Twitter/X via Tweepy |
| [**Solana SDK**](sdk/) | TypeScript | On-chain data fetcher — prices, wallets, transactions |
| [**Signal CLI**](cli/) | Go | Lightweight CLI for terminal-native signal checks |
| [**Core SDK**](core/) | Rust | High-performance signal computation and data processing |

---

## Quickstart

### Prerequisites

- Python 3.11+
- Node.js 20+ & npm
- Go 1.22+
- Rust 1.76+ & Cargo

### 1. Clone

```bash
git clone https://github.com/nujar00t/Orin.LAB.git
cd Orin.LAB
```

### 2. Install all dependencies

```bash
make install
```

Or manually:

```bash
# Python
pip install -r requirements.txt

# TypeScript (Auto Poster + SDK)
npm install
cd poster && npm install
cd sdk && npm install

# Go CLI
cd cli && go mod tidy

# Rust Core
cd core && cargo build --release
```

### 3. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in your keys — minimum required:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
ANTHROPIC_API_KEY=your_anthropic_key
```

### 4. Run

```bash
# Interactive menu
python orin.py

# Or directly via make:
make bot       # Telegram Bot
make signal    # Signal Engine (terminal)
make poster    # Auto Poster (Twitter/X)
make cli       # Go Signal CLI
```

---

## Environment Variables

| Variable | Required | Source | Description |
|----------|----------|--------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | [@BotFather](https://t.me/BotFather) | Telegram bot token |
| `ANTHROPIC_API_KEY` | ✅ | [console.anthropic.com](https://console.anthropic.com) | Claude AI API key |
| `SOLANA_RPC_URL` | ⬜ | [helius.dev](https://helius.dev) | Solana RPC endpoint (default: mainnet) |
| `SOLANA_WALLET_ADDRESS` | ⬜ | Your wallet | Wallet to monitor with on-chain agent |
| `TWITTER_API_KEY` | ⬜ | [developer.twitter.com](https://developer.twitter.com) | Twitter/X API key (for Auto Poster) |
| `TWITTER_API_SECRET` | ⬜ | Twitter Dev Portal | Twitter API secret |
| `TWITTER_ACCESS_TOKEN` | ⬜ | Twitter Dev Portal | OAuth access token |
| `TWITTER_ACCESS_SECRET` | ⬜ | Twitter Dev Portal | OAuth access secret |
| `SIGNAL_CONFIDENCE_THRESHOLD` | ⬜ | — | Min confidence to fire alerts (default: 70) |
| `LOG_LEVEL` | ⬜ | — | `DEBUG` / `INFO` / `WARNING` (default: `INFO`) |

---

## Telegram Bot Commands

Once the bot is running, these commands are available:

| Command | Description |
|---------|-------------|
| `/start` | Welcome screen with quick-action keyboard |
| `/signal $TOKEN` | Generate BUY/SELL/HOLD signal with confidence score |
| `/analyze $TOKEN` | Deep AI market analysis (price action, levels, risks) |
| `/help` | Show all commands |

**Example:**
```
/signal $SOL
→ 📊 Signal: $SOL
   SIGNAL: BUY
   Confidence: 82/100
   Target: $185.00
   Stop Loss: $152.00
   Reasoning: SOL is holding key support at $158 with increasing DEX volume...
   Risk Level: MEDIUM
```

Or just chat naturally — Orin maintains conversation history per user.

---

## Project Structure

```
Orin.LAB/
├── orin.py                     ← Main entry point (Python)
├── bot/
│   ├── __init__.py
│   ├── telegram_bot.py         ← Bot application setup
│   └── handlers.py             ← Command & message handlers
├── agents/
│   ├── signal_engine.py        ← Signal generation (Jupiter + Claude)
│   ├── signal_engine_v2.py     ← Rate-limited + cached version
│   ├── market_analyst.py       ← Deep market analysis agent
│   ├── onchain_agent.py        ← Solana on-chain monitoring
│   ├── alert_manager.py        ← Threshold-based alert dispatcher
│   └── dashboard.py            ← Live terminal dashboard
├── utils/
│   ├── config.py               ← Typed env-var config loader
│   ├── logger.py               ← Centralized Rich logger
│   ├── rate_limiter.py         ← Sliding-window rate limiter
│   ├── cache.py                ← In-memory TTL cache
│   └── helpers.py              ← Formatting and parsing utilities
├── poster/
│   └── src/index.ts            ← Auto poster to Twitter/X
├── sdk/
│   └── src/index.ts            ← Solana data SDK (TypeScript)
├── cli/
│   └── main.go                 ← Signal CLI (Go)
├── core/
│   └── src/lib.rs              ← High-performance core (Rust)
├── tests/
│   ├── test_signal_engine.py
│   ├── test_onchain_agent.py
│   ├── test_helpers.py
│   ├── test_rate_limiter.py
│   ├── test_cache.py
│   └── test_config.py
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              ← Full CI pipeline
│   │   ├── codeql.yml          ← Security scanning
│   │   ├── test.yml            ← Test runner with coverage
│   │   ├── lint.yml            ← Ruff + TypeScript linting
│   │   └── release.yml         ← Auto GitHub releases
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CODEOWNERS
│   ├── FUNDING.yml
│   └── dependabot.yml
├── Makefile
├── requirements.txt
├── pyproject.toml
├── package.json
├── tsconfig.json
├── .editorconfig
└── .env.example
```

---

## Development

### Run tests

```bash
# All Python tests
make test

# With coverage
pytest tests/ -v --cov=utils --cov=agents --cov=bot --cov-report=term-missing

# Individual test files
pytest tests/test_signal_engine.py -v
```

### Lint

```bash
make lint

# Python only
ruff check .
ruff format --check .

# TypeScript only
npx tsc --noEmit
```

### Branches

| Branch | Purpose |
|--------|---------|
| `main` | Stable, production-ready |
| `develop` | Integration branch for features |
| `feature/*` | New features |
| `hotfix/*` | Urgent production fixes |
| `chore/*` | Config, docs, tooling |

---

## Roadmap

### v1.0.0 — Foundation ✅
- [x] Telegram AI Bot with conversation history
- [x] Signal Engine with on-chain data + AI
- [x] Market Analyst (Claude Sonnet)
- [x] On-chain Agent (Solana wallet monitoring)
- [x] Auto Poster (Twitter/X)
- [x] TypeScript Solana SDK
- [x] Go Signal CLI
- [x] Rust Core SDK
- [x] Full CI/CD pipeline + CodeQL + Dependabot

### v1.1.0 — Intelligence Layer
- [ ] Alert Manager — auto-notify on high-confidence signals
- [ ] Live terminal dashboard
- [ ] Whale wallet tracker
- [ ] Chart image analysis via Telegram photo
- [ ] Rate limiter + TTL cache for all API calls

### v1.2.0 — Distribution
- [ ] Web dashboard (Next.js)
- [ ] Signal history & analytics
- [ ] Webhook support for third-party integrations

### v2.0.0 — Multi-chain
- [ ] EVM chain support (Ethereum, Base, Arbitrum)
- [ ] Agent coordination layer
- [ ] Mobile app

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes following [Conventional Commits](https://www.conventionalcommits.org/)
4. Open a pull request against `develop`

---

## Security

Found a vulnerability? See [SECURITY.md](SECURITY.md) for responsible disclosure guidelines. Do **not** open a public issue.

---

## Disclaimer

Orin.LAB is experimental software for research purposes.

- AI signals are **not financial advice**
- Past signal accuracy does **not** guarantee future results
- Always do your own research (DYOR)
- Never share your private key or seed phrase
- Use at your own risk

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

**Orin.LAB** · AI Research Lab for Crypto Markets

Built with ❤️ on [Solana](https://solana.com) · Powered by [Claude AI](https://anthropic.com)

`$ORNL` · [GitHub](https://github.com/nujar00t/Orin.LAB) · [Issues](https://github.com/nujar00t/Orin.LAB/issues)

</div>