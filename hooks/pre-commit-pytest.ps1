Write-Output "🧪 Running pytest with environment variables..."

$env:PYTHONPATH = "."
$env:ACTIVE_APP = "concierge"
$env:OPENAI_API_KEY = "test-key"

python -m pytest -m "not external"
