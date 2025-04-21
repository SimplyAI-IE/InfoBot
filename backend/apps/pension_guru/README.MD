# 📊 Pension Guru App

This app powers InfoBot’s pension forecasting capabilities. It uses deterministic rules, validated input extraction, and YAML-driven dialogue — **no GPT is used** in any projection logic.

---

## 🔍 Purpose

- Calculates future pension value based on inputs like age, income, contribution rate, etc.
- Follows strict deterministic logic — no AI or prediction models.
- Requires all fields before computation (no partial estimates).

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `conversation_flow.yaml` | Defines step-by-step data collection and logic flow |
| `extract_user_data.py` | Parses raw user inputs and maps them to required fields |
| `pension_calculator.py` | Core deterministic calculator |
| `flow_engine.py` | Drives the data collection flow |
| `prompt.txt` | (Legacy) Used for potential GPT fallback — currently unused |
| `config.json` | Validation or flow metadata (e.g., min/max age, limits) |

---

## 🚫 GPT-Free Zone

All calculations are made using strict logic in `pension_calculator.py`. This file must:
- Not depend on AI models
- Be fully covered by unit tests
- Be explainable and auditable

---

## 📦 Data Input Format

Required fields:
- `current_age`
- `retirement_age`
- `current_salary`
- `annual_contribution_percent`
- `expected_return_rate`
- `current_pension_balance`

---

## 🧪 Testing

Tests should cover:
- Edge cases (e.g., retirement_age < current_age)
- Bad inputs (e.g., negative salary)
- Return rate boundaries (0%, 100%)
