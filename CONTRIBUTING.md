# Contributing to Orin.LAB

Thanks for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/orinlab`
3. Create a branch: `git checkout -b feat/your-feature`
4. Make your changes
5. Run tests: `make test`
6. Submit a pull request

## Development Setup

```bash
cp .env.example .env
make install
```

## Code Style

- **Python**: follow PEP 8, use `ruff` for linting
- **TypeScript**: strict mode enabled, no `any`
- **Go**: run `go vet` and `go fmt`
- **Rust**: run `cargo clippy`

## Commit Convention

```
feat: add new feature
fix: fix a bug
docs: documentation changes
test: add or update tests
ci: CI/CD changes
chore: maintenance
```

## Reporting Bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

## Security

See [SECURITY.md](SECURITY.md) for reporting security vulnerabilities.
