#!/bin/sh
echo "🔍 Running type checks and tests before commit..."

export PYTHONPATH=.
export ACTIVE_APP=concierge
export OPENAI_API_KEY=test-key

echo "🔎 Running mypy..."
python -m mypy backend tests
MYPY_RESULT=$?

if [ $MYPY_RESULT -ne 0 ]; then
  echo "❌ mypy failed. Commit blocked."
  exit 1
fi

echo "🧪 Running pytest..."
python -m pytest -m "not external"
PYTEST_RESULT=$?

if [ $PYTEST_RESULT -ne 0 ]; then
  echo "❌ Tests failed. Commit blocked."
  exit 1
fi

echo "✅ All checks passed. Proceeding with commit."
