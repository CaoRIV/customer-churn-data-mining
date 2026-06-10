from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@st.cache_data(show_spinner=False)
def load_telco_data() -> pd.DataFrame:
    data = pd.read_csv(PROJECT_ROOT / "data" / "raw" / "telco_customer.csv")
    data = data.copy()
    data["SeniorCitizen"] = data["SeniorCitizen"].map({0: "No", 1: "Yes"}).fillna(
        data["SeniorCitizen"]
    )
    data["TotalCharges"] = pd.to_numeric(data["TotalCharges"], errors="coerce").fillna(0)
    return data


@st.cache_data(show_spinner=False)
def load_model_comparison() -> pd.DataFrame:
    return pd.read_csv(PROJECT_ROOT / "reports" / "classification_model_comparison.csv")


@st.cache_data(show_spinner=False)
def load_business_thresholds() -> pd.DataFrame:
    return pd.read_csv(PROJECT_ROOT / "reports" / "business_threshold_analysis.csv")


def model_features(data: pd.DataFrame) -> pd.DataFrame:
    return data.drop(columns=["customerID", "Churn"], errors="ignore")
