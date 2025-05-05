verify:
	@echo "🔎 Running lint, type, and test checks..."
	@ruff check .
	@PYTHONPATH=. mypy backend tests
	@echo "ACTIVE_APP=concierge" > .env
	@echo "OPENAI_API_KEY=test-key" >> .env
	@PYTHONPATH=. pytest -m "not external"

format:
	@echo "🎨 Formatting code with Ruff..."
	@ruff format .
	@ruff check . --fix

typefix:
	@echo "🛠️ Running mypy with autofix (if any tools support it)..."
	@mypy backend tests
