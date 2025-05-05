#!/bin/bash
echo "🧪 Running pytest with CI environment..."
export PYTHONPATH=.
export ACTIVE_APP=pension_guru
export OPENAI_API_KEY=fake-ci-key
pytest -m "not external"