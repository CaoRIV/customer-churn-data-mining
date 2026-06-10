from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from utils.ui import apply_global_styles

st.set_page_config(
    page_title="Telco Churn Intelligence",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="auto",
)

apply_global_styles()

pages = [
    st.Page(
        "pages/overview.py",
        title="Tổng quan / Overview",
        icon=":material/dashboard:",
        default=True,
    ),
    st.Page(
        "pages/eda.py",
        title="Khám phá dữ liệu / EDA",
        icon=":material/analytics:",
    ),
    st.Page(
        "pages/prediction.py",
        title="Dự đoán churn / Prediction",
        icon=":material/model_training:",
    ),
    st.Page(
        "pages/business.py",
        title="Tối ưu kinh doanh / Business",
        icon=":material/tune:",
    ),
]

navigation = st.navigation(pages, position="sidebar")
navigation.run()
