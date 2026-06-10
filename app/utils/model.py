from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from .constants import (
    CRITICAL_THRESHOLD,
    FEATURE_COLUMNS,
    MODEL_THRESHOLD,
    WATCHLIST_THRESHOLD,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@st.cache_resource(show_spinner=False)
def load_model():
    return joblib.load(PROJECT_ROOT / "models" / "best_model.joblib")


@st.cache_data(show_spinner=False)
def load_model_metadata() -> dict:
    with (PROJECT_ROOT / "models" / "best_model_metadata.json").open(
        "r", encoding="utf-8"
    ) as file:
        return json.load(file)


@st.cache_data(show_spinner=False)
def load_threshold_metadata() -> dict:
    with (PROJECT_ROOT / "models" / "selected_threshold.json").open(
        "r", encoding="utf-8"
    ) as file:
        return json.load(file)


def risk_tier(probability: float) -> str:
    if probability >= CRITICAL_THRESHOLD:
        return "Critical"
    if probability >= MODEL_THRESHOLD:
        return "High"
    if probability >= WATCHLIST_THRESHOLD:
        return "Watchlist"
    return "Low"


def risk_tier_series(probabilities: pd.Series | np.ndarray) -> pd.Series:
    values = pd.Series(probabilities)
    return pd.Series(
        np.select(
            [
                values >= CRITICAL_THRESHOLD,
                values >= MODEL_THRESHOLD,
                values >= WATCHLIST_THRESHOLD,
            ],
            ["Critical", "High", "Watchlist"],
            default="Low",
        ),
        index=values.index,
        dtype="object",
    )


def score_customers(data: pd.DataFrame, threshold: float = MODEL_THRESHOLD) -> pd.DataFrame:
    features = data.loc[:, FEATURE_COLUMNS].copy()
    probabilities = load_model().predict_proba(features)[:, 1]
    result = pd.DataFrame(index=data.index)
    result["churn_probability"] = probabilities
    result["predicted_churn"] = np.where(probabilities >= threshold, "Yes", "No")
    result["threshold"] = threshold
    result["risk_tier"] = risk_tier_series(probabilities).values
    return result


def build_retention_list(
    data: pd.DataFrame, threshold: float = MODEL_THRESHOLD
) -> pd.DataFrame:
    features = data.loc[:, FEATURE_COLUMNS]
    scores = score_customers(features, threshold=threshold)
    return pd.DataFrame(
        {
            "customerID": data["customerID"].values,
            "churn_probability": scores["churn_probability"].values,
            "risk_tier": scores["risk_tier"].values,
            "selected_for_retention": scores["predicted_churn"].eq("Yes").values,
            "tenure": data["tenure"].values,
            "Contract": data["Contract"].values,
            "InternetService": data["InternetService"].values,
            "MonthlyCharges": data["MonthlyCharges"].values,
            "OnlineSecurity": data["OnlineSecurity"].values,
            "TechSupport": data["TechSupport"].values,
            "PaymentMethod": data["PaymentMethod"].values,
        }
    ).sort_values("churn_probability", ascending=False)


def _clean_feature_name(feature_name: str) -> str:
    feature_name = feature_name.replace("numeric__", "").replace("categorical__", "")
    return feature_name.replace("_", " ")


def customer_contributions(customer: pd.DataFrame, top_n: int = 5) -> tuple[pd.DataFrame, pd.DataFrame]:
    pipeline = load_model()
    preprocessor = pipeline.named_steps["preprocessor"]
    estimator = pipeline.named_steps["model"]

    transformed = preprocessor.transform(customer.loc[:, FEATURE_COLUMNS])
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()

    feature_names = preprocessor.get_feature_names_out()
    contributions = transformed[0] * estimator.coef_[0]
    contribution_frame = pd.DataFrame(
        {
            "feature": [_clean_feature_name(name) for name in feature_names],
            "contribution": contributions,
        }
    )

    increasing = (
        contribution_frame.loc[contribution_frame["contribution"] > 0]
        .nlargest(top_n, "contribution")
        .reset_index(drop=True)
    )
    decreasing = (
        contribution_frame.loc[contribution_frame["contribution"] < 0]
        .nsmallest(top_n, "contribution")
        .assign(contribution=lambda frame: frame["contribution"].abs())
        .reset_index(drop=True)
    )
    return increasing, decreasing


def retention_recommendations(customer: dict, probability: float) -> list[str]:
    recommendations: list[str] = []
    if customer["tenure"] <= 12:
        recommendations.append(
            "Ưu tiên onboarding và kiểm tra trải nghiệm trong năm đầu / Prioritize first-year onboarding."
        )
    if customer["Contract"] == "Month-to-month":
        recommendations.append(
            "Đề xuất ưu đãi chuyển sang hợp đồng dài hạn / Offer a longer-term contract incentive."
        )
    if customer["InternetService"] == "Fiber optic":
        recommendations.append(
            "Rà soát chất lượng Fiber optic và mức độ phù hợp gói cước / Review fiber quality and plan fit."
        )
    if customer["OnlineSecurity"] == "No" or customer["TechSupport"] == "No":
        recommendations.append(
            "Thử nghiệm bundle bảo mật hoặc hỗ trợ kỹ thuật / Test a security or tech-support bundle."
        )
    if customer["PaymentMethod"] == "Electronic check":
        recommendations.append(
            "Khuyến khích chuyển sang thanh toán tự động / Encourage automatic payment."
        )
    if not recommendations:
        recommendations.append(
            "Duy trì chăm sóc định kỳ và theo dõi thay đổi risk score / Maintain regular care and monitor risk."
        )
    if probability < MODEL_THRESHOLD:
        recommendations.insert(
            0,
            "Chưa cần ưu đãi giữ chân chủ động / No proactive retention offer is currently required.",
        )
    return recommendations
