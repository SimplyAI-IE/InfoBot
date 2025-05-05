verify:
	@echo "🔎 Running lint, type, and test checks..."
	@ruff check .
	@mypy backend tests
	@PYTHONPATH=. ACTIVE_APP=concierge OPENAI_API_KEY=test-key pytest -m "not external"

format:
	@echo "🎨 Formatting code with Ruff..."
	@ruff format .
	@ruff check . --fix

typefix:
	@echo "🛠️ Running mypy with autofix (if any tools support it)..."
	@mypy backend tests
