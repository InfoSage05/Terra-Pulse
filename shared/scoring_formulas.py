"""Pure, unit-testable scoring formulas shared between the training scripts
(models_layer/training/train_affordability.py, train_safety.py) and the
backend's live inference path (backend/app/services/score_service.py).

These formulas were previously duplicated inline in score_service.py -
keeping a single copy here means a tuning change only has to happen once,
and both call sites are guaranteed to agree. Formulas are documented in
docs/architecture.md ("Scoring Formulas") - update both places together.
"""
from typing import Optional


def affordability_score(avg_price: Optional[float], deprivation_index: Optional[float]) -> Optional[float]:
    """Score = max(0, 100 - (Price / 10000) * 0.6 - (Deprivation * 10) * 0.4)

    Returns None if either input is missing, or if avg_price is not positive
    (an area with no recorded sales has no meaningful affordability signal).
    """
    if avg_price is None or deprivation_index is None:
        return None
    # Postgres NUMERIC columns (e.g. AVG(price_eur)) come back as
    # decimal.Decimal via psycopg2, which can't be mixed with float in
    # arithmetic (TypeError) - normalize both inputs up front rather than
    # relying on every caller to pass plain floats.
    avg_price = float(avg_price)
    deprivation_index = float(deprivation_index)
    if avg_price <= 0:
        return None
    return max(0.0, 100.0 - (avg_price / 10000) * 0.6 - (deprivation_index * 10) * 0.4)


def safety_score(total_crime: Optional[float], population: Optional[float]) -> Optional[float]:
    """Score = max(0, 100 - (Crime / Population * 1000) * 2)

    Returns None if either input is missing, or if population is not
    positive (crime rate per capita is undefined without a population base).
    """
    if total_crime is None or population is None:
        return None
    total_crime = float(total_crime)
    population = float(population)
    if population <= 0:
        return None
    crime_rate = (total_crime / population) * 1000
    return max(0.0, 100.0 - (crime_rate * 2))
