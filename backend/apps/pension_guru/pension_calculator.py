from typing import Optional, Union


def calculate_ireland_pension(
    prsi_years: int, age: Optional[int] = None, retirement_age: Optional[int] = None
) -> dict[str, Union[str, float]]:
    return {
        "currency": "€",
        "weekly_pension_now": float(prsi_years * 10),
        "weekly_pension_future": float(prsi_years * 12.5),
        "prsi_years": float(prsi_years),
        "contributions_now": float(prsi_years * 48),
        "contributions_future": float(prsi_years * 52),
    }


def calculate_uk_pension(ni_years: int) -> dict[str, Union[str, float]]:
    weekly = ni_years * 5.0
    return {
        "currency": "£",
        "weekly_pension_now": weekly,
        "weekly_pension_future": weekly + 50,
        "prsi_years": float(ni_years),
        "contributions_now": float(ni_years * 50),
        "contributions_future": float(ni_years * 60),
    }


def calculate_pension(
    region: str,
    years: int,
    age: Optional[int] = None,
    retirement_age: Optional[int] = None,
) -> dict[str, Union[str, float]]:
    if region.lower() == "ireland":
        return calculate_ireland_pension(years, age, retirement_age)
    elif region.lower() == "uk":
        return calculate_uk_pension(years)
    return {}
