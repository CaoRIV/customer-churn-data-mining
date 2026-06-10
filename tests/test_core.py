from __future__ import annotations

import numpy as np
import pandas as pd

from app.utils.business import recalculate_business_value
from app.utils.constants import DEFAULT_CUSTOMER, FEATURE_COLUMNS
from app.utils.model import (
    build_retention_list,
    customer_contributions,
    load_model,
    risk_tier,
    score_customers,
)
from app.utils.data import load_telco_data
from app.utils.validation import template_frame, validate_batch


def test_risk_tier_boundaries() -> None:
    assert risk_tier(0.50) == "Critical"
    assert risk_tier(0.30) == "High"
    assert risk_tier(0.15) == "Watchlist"
    assert risk_tier(0.149) == "Low"


def test_valid_template_scores_like_direct_model() -> None:
    template = template_frame()
    validated, errors = validate_batch(template)
    assert errors == []
    assert validated["validation_error"].eq("").all()

    features = validated[FEATURE_COLUMNS]
    direct_probability = load_model().predict_proba(features)[:, 1]
    utility_probability = score_customers(features)["churn_probability"].to_numpy()
    np.testing.assert_allclose(direct_probability, utility_probability)


def test_validation_reports_missing_column() -> None:
    data = template_frame().drop(columns=["Contract"])
    validated, errors = validate_batch(data)
    assert errors
    assert "Contract" in validated.loc[0, "validation_error"]


def test_validation_reports_invalid_category_and_negative_value() -> None:
    data = template_frame()
    data.loc[0, "InternetService"] = "Satellite"
    data.loc[0, "MonthlyCharges"] = -1
    validated, errors = validate_batch(data)
    assert errors == []
    assert "InternetService" in validated.loc[0, "validation_error"]
    assert "MonthlyCharges" in validated.loc[0, "validation_error"]


def test_business_formula() -> None:
    metrics = pd.DataFrame(
        [
            {
                "threshold": 0.30,
                "true_positive": 100,
                "false_positive": 50,
                "false_negative": 20,
                "flagged_customers": 150,
            }
        ]
    )
    result = recalculate_business_value(metrics, 50, 600, 0.30, 400)
    expected = 100 * 0.30 * 600 - 150 * 50 - 20 * 400
    assert result.loc[0, "expected_net_value"] == expected


def test_customer_contributions_return_both_directions() -> None:
    customer = pd.DataFrame([DEFAULT_CUSTOMER], columns=FEATURE_COLUMNS)
    increasing, decreasing = customer_contributions(customer)
    assert not increasing.empty
    assert not decreasing.empty
    assert increasing["contribution"].ge(0).all()
    assert decreasing["contribution"].ge(0).all()


def test_batch_row_limit_is_blocking() -> None:
    row = template_frame()
    oversized = pd.concat([row] * 50_001, ignore_index=True)
    validated, errors = validate_batch(oversized)
    assert errors
    assert validated["validation_error"].ne("").all()


def test_retention_download_does_not_include_ground_truth() -> None:
    retention = build_retention_list(load_telco_data().head(10))
    assert "actual_churn" not in retention.columns
    assert "Churn" not in retention.columns
