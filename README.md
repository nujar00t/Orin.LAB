# Orin.LAB

> **AI Research Lab for Crypto Markets**
> Reads the market. Signals the moves. Posts the alpha.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![TypeScript](https://img.shields.io/badge/typescript-5.4+-blue.svg)](https://typescriptlang.org)
[![Rust](https://img.shields.io/badge/rust-1.76+-orange.svg)](https://rust-lang.org)
[![Go](https://img.shields.io/badge/go-1.22+-cyan.svg)](https://go.dev)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Solana](https://img.shields.io/badge/chain-Solana-purple.svg)](https://solana.com)
[![Token](https://img.shields.io/badge/token-%24ORNL-orange.svg)](https://pump.fun)
[![CI](https://github.com/nujar00t/orinlab/actions/workflows/ci.yml/badge.svg)](https://github.com/nujar00t/orinlab/actions)

---

## What is Orin.LAB?

Orin.LAB is an open-source AI research lab for crypto markets built on Solana. It combines a Telegram AI assistant, real-time market signal generation, on-chain data analysis, and automated alpha distribution — all powered by Claude AI.

> *"Orin.LAB doesn't predict. It researches, signals, and acts."*

---

## Agents & Modules

| Module | Language | Description |
|--------|----------|-------------|
| **Telegram Bot** | Python | AI-powered bot — chart analysis, Q&A, signal delivery |
| **Signal Engine** | Python | Generate BUY/SELL/HOLD signals from on-chain + sentiment |
| **Auto Poster** | TypeScript | Post signals and alpha to Twitter/X automatically |
| **Solana SDK** | TypeScript | On-chain data fetcher — prices, wallets, transactions |
| **Signal CLI** | Go | Lightweight CLI for running signal checks |
| **Core SDK** | Rust | High-performance data processing core |

---

## Quickstart

### 1. Clone
```bash
git clone https://github.com/nujar00t/orinlab
cd orinlab
```

### 2. Install
```bash
make install
```

### 3. Configure
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Run
```bash
# Telegram Bot
make bot

# Signal Engine
make signal

# Auto Poster
make poster

# Signal CLI (Go)
make cli
```

---

## Project Structure

```
orinlab/
├── orin.py                        ← Python entry point
├── bot/
│   ├── telegram_bot.py            ← Telegram AI bot
│   └── handlers.py                ← Message handlers
├── agents/
│   ├── signal_engine.py           ← Signal generation
│   ├── market_analyst.py          ← Market analysis with Claude
│   └── onchain_agent.py           ← Solana on-chain data
├── poster/
│   └── src/index.ts               ← Auto post to Twitter/X
├── sdk/
│   └── src/index.ts               ← Solana data SDK (TypeScript)
├── cli/
│   └── main.go                    ← Signal CLI (Go)
├── core/
│   └── src/lib.rs                 ← High-performance core (Rust)
├── tests/                         ← Python unit tests
├── .github/
│   ├── workflows/ci.yml
│   ├── workflows/codeql.yml
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CODEOWNERS
│   ├── FUNDING.yml
│   └── dependabot.yml
├── Makefile
├── requirements.txt
├── pyproject.toml
├── package.json
└── .env.example
```

---

## API Keys

| Key | Source | Used by |
|-----|--------|---------|
| `TELEGRAM_BOT_TOKEN` | [@BotFather](https://t.me/BotFather) | Telegram Bot |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | All AI features |
| `SOLANA_RPC_URL` | [helius.dev](https://helius.dev) | On-chain data |
| `TWITTER_BEARER_TOKEN` | [developer.twitter.com](https://developer.twitter.com) | Auto Poster |

---

## Disclaimer

Orin.LAB is experimental software. AI signals are **not financial advice**. Always DYOR. Never share your private key.

---

## Roadmap

### v1.0.0 (current)
- [x] Telegram AI Bot — market Q&A + signal delivery
- [x] Signal Engine — on-chain + sentiment signals
- [x] Auto Poster — Twitter/X alpha distribution
- [x] Solana SDK (TypeScript)
- [x] Signal CLI (Go)
- [x] Core SDK (Rust)
- [x] CI/CD pipeline + CodeQL

### v1.1.0
- [ ] Whale wallet tracker
- [ ] Chart image analysis via Telegram photo
- [ ] Web dashboard

### v2.0.0
- [ ] Multi-chain support
- [ ] Agent coordination layer
- [ ] Mobile app

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — contributions welcome.

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">
  <strong>Orin.LAB</strong> · AI Research Lab for Crypto Markets<br>
  <code>$ORNL</code> · Built on Solana
</div>
