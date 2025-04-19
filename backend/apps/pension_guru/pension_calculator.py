PENSION_RATE_IE_2025 = 289.30
PENSION_RATE_UK_2025 = 221.20

WEEKS_PER_YEAR = 52
MAX_PRSI_CONTRIBUTIONS = 2080  # 40 years × 52
MAX_NI_YEARS = 35

def calculate_ireland_pension(prsi_years: int):
    contributions = prsi_years * WEEKS_PER_YEAR
    fraction = contributions / MAX_PRSI_CONTRIBUTIONS
    raw = round(fraction * PENSION_RATE_IE_2025, 2)
    pension = max(min(raw, PENSION_RATE_IE_2025), 70.00)

    return {
        "region": "Ireland",
        "method": "PRSI-based formula",
        "prsi_years": prsi_years,
        "contributions": contributions,
        "fraction": round(fraction, 2),
        "weekly_pension": pension,
        "currency": "€"
    }

def calculate_uk_pension(ni_years: int):
    fraction = ni_years / MAX_NI_YEARS
    raw = round(fraction * PENSION_RATE_UK_2025, 2)
    pension = max(min(raw, PENSION_RATE_UK_2025), 50.00)

    return {
        "region": "UK",
        "method": "NI years formula",
        "ni_years": ni_years,
        "fraction": round(fraction, 2),
        "weekly_pension": pension,
        "currency": "£"
    }

def calculate_pension(region: str, years: int):
    if region == "Ireland":
        return calculate_ireland_pension(years)
    elif region == "UK":
        return calculate_uk_pension(years)
    else:
        return None
