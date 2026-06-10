from __future__ import annotations

import numpy as np
import pandas as pd


def recalculate_business_value(
    threshold_metrics: pd.DataFrame,
    intervention_cost_per_customer: float,
    retained_customer_value: float,
    retention_success_rate: float,
    missed_churn_cost: float,
) -> pd.DataFrame:
    result = threshold_metrics.copy()
    result["expected_retained_customers"] = (
        result["true_positive"] * retention_success_rate
    )
    result["expected_retained_value"] = (
        result["expected_retained_customers"] * retained_customer_value
    )
    result["intervention_cost"] = (
        result["flagged_customers"] * intervention_cost_per_customer
    )
    result["missed_churn_cost"] = result["false_negative"] * missed_churn_cost
    result["expected_net_value"] = (
        result["expected_retained_value"]
        - result["intervention_cost"]
        - result["missed_churn_cost"]
    )
    return result


def threshold_row(data: pd.DataFrame, threshold: float) -> pd.Series:
    match = data.loc[np.isclose(data["threshold"], threshold)]
    if match.empty:
        raise ValueError(f"Threshold {threshold:.2f} không tồn tại.")
    return match.iloc[0]
