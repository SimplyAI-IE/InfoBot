PENSION_RATE_IE_2025 = 289.30
PENSION_RATE_UK_2025 = 221.20

WEEKS_PER_YEAR = 52
MAX_PRSI_CONTRIBUTIONS = 2080  # 40 years × 52
MAX_NI_YEARS = 35


def calculate_ireland_pension(prsi_years: int, age: int = None, retirement_age: int = None):
    current_contribs = prsi_years * WEEKS_PER_YEAR
    current_fraction = current_contribs / MAX_PRSI_CONTRIBUTIONS
    current_weekly = max(min(round(current_fraction * PENSION_RATE_IE_2025, 2), PENSION_RATE_IE_2025), 70.00)

    # ❌ Block future projection if age or retirement_age is missing
    if age is None or retirement_age is None or retirement_age <= age:
        return None

    extra_years = retirement_age - age
    future_years = prsi_years + extra_years
    future_contribs = future_years * WEEKS_PER_YEAR
    future_fraction = future_contribs / MAX_PRSI_CONTRIBUTIONS
    future_weekly = max(min(round(future_fraction * PENSION_RATE_IE_2025, 2), PENSION_RATE_IE_2025), 70.00)

    return {
        "region": "Ireland",
        "method": "PRSI-based formula",
        "prsi_years": prsi_years,
        "contributions_now": current_contribs,
        "fraction_now": round(current_fraction, 2),
        "weekly_pension_now": current_weekly,
        "contributions_future": future_contribs,
        "fraction_future": round(future_fraction, 2),
        "weekly_pension_future": future_weekly,
        "retirement_age": retirement_age,
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


def calculate_pension(region: str, years: int, age: int = None, retirement_age: int = None):
    if region.lower() == "ireland":
        return calculate_ireland_pension(years, age, retirement_age)
    elif region.lower() == "uk":
        return calculate_uk_pension(years)
    else:
        return None
