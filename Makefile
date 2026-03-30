.PHONY: install bot signal poster cli test lint clean

install:
	pip install -r requirements.txt
	npm install
	cd poster && npm install
	cd sdk && npm install
	cd cli && go mod tidy
	cd core && cargo build --release

bot:
	python orin.py bot

signal:
	python orin.py signal

poster:
	cd poster && npm run dev

cli:
	cd cli && go run main.go

test:
	pytest tests/ -v --tb=short
	cd poster && npm test
	cd sdk && npm test
	cd cli && go test ./...
	cd core && cargo test

lint:
	python -m ruff check .
	cd poster && npx tsc --noEmit
	cd sdk && npx tsc --noEmit
	cd cli && go vet ./...
	cd core && cargo clippy

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	cd cli && go clean
	cd core && cargo clean
