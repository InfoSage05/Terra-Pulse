from decimal import Decimal

from shared.scoring_formulas import affordability_score, safety_score


def test_affordability_score_typical():
    score = affordability_score(avg_price=300000, deprivation_index=2.0)
    assert score == max(0.0, 100.0 - (300000 / 10000) * 0.6 - (2.0 * 10) * 0.4)


def test_affordability_score_zero_price_is_none():
    assert affordability_score(avg_price=0, deprivation_index=1.0) is None


def test_affordability_score_missing_deprivation_is_none():
    assert affordability_score(avg_price=300000, deprivation_index=None) is None


def test_affordability_score_missing_price_is_none():
    assert affordability_score(avg_price=None, deprivation_index=1.0) is None


def test_affordability_score_floors_at_zero():
    # An extreme price should floor at 0, never go negative.
    assert affordability_score(avg_price=100_000_000, deprivation_index=10.0) == 0.0


def test_safety_score_typical():
    score = safety_score(total_crime=50, population=10000)
    crime_rate = (50 / 10000) * 1000
    assert score == max(0.0, 100.0 - (crime_rate * 2))


def test_safety_score_zero_population_is_none():
    assert safety_score(total_crime=50, population=0) is None


def test_safety_score_negative_population_is_none():
    assert safety_score(total_crime=50, population=-5) is None


def test_safety_score_missing_crime_is_none():
    assert safety_score(total_crime=None, population=10000) is None


def test_safety_score_missing_population_is_none():
    assert safety_score(total_crime=50, population=None) is None


def test_safety_score_zero_crime_is_perfect():
    assert safety_score(total_crime=0, population=10000) == 100.0


def test_safety_score_floors_at_zero():
    assert safety_score(total_crime=1_000_000, population=100) == 0.0


def test_affordability_score_accepts_decimal_from_postgres_numeric():
    # AVG(price_eur)/deprivation_index come back as decimal.Decimal via
    # psycopg2 in production - regression guard for a real TypeError
    # (Decimal * float) that only surfaced once an active affordability
    # model was actually exercised against live data.
    score = affordability_score(avg_price=Decimal("350000.00"), deprivation_index=Decimal("1.5"))
    assert score == max(0.0, 100.0 - (350000.0 / 10000) * 0.6 - (1.5 * 10) * 0.4)


def test_safety_score_accepts_decimal_from_postgres_numeric():
    score = safety_score(total_crime=Decimal("50"), population=Decimal("10000"))
    crime_rate = (50.0 / 10000.0) * 1000
    assert score == max(0.0, 100.0 - (crime_rate * 2))
