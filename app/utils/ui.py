from __future__ import annotations

import html

import streamlit as st

from .constants import RISK_COLORS


GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: "Fira Sans", sans-serif;
    letter-spacing: 0;
}

.stApp {
    background: #F8FAFC;
}

[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 14px 16px;
    min-height: 112px;
}

[data-testid="stMetricLabel"] {
    color: #475569;
}

[data-testid="stMetricValue"] {
    color: #172033;
}

.section-label {
    color: #1E40AF;
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}

.page-subtitle {
    color: #475569;
    max-width: 960px;
    margin-bottom: 1.2rem;
}

.status-strip {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #1E40AF;
    border-radius: 6px;
    padding: 12px 14px;
    margin: 8px 0 16px 0;
}

.risk-panel {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 16px;
}

.risk-tier {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
}

div[data-testid="stButton"] button,
div[data-testid="stDownloadButton"] button {
    border-radius: 6px;
    min-height: 40px;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    overflow: hidden;
}

@media (max-width: 640px) {
    h1 {
        font-size: 2.1rem !important;
        line-height: 1.15 !important;
    }

    [data-testid="stMetric"] {
        min-height: 96px;
        padding: 10px 12px;
    }
}

@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
"""


def apply_global_styles() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(label: str, title: str, subtitle: str) -> None:
    st.markdown(f'<div class="section-label">{html.escape(label)}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(
        f'<div class="page-subtitle">{html.escape(subtitle)}</div>',
        unsafe_allow_html=True,
    )


def status_strip(text: str) -> None:
    st.markdown(
        f'<div class="status-strip">{html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


def risk_panel(probability: float, tier: str, threshold: float) -> None:
    color = RISK_COLORS[tier]
    decision = "Flag retention" if probability >= threshold else "Monitor"
    st.markdown(
        f"""
        <div class="risk-panel" style="border-left: 5px solid {color};">
            <div class="risk-tier" style="color: {color};">{html.escape(tier)}</div>
            <div style="font-size: 2rem; font-weight: 700; color: #172033;">
                {probability:.1%}
            </div>
            <div style="color: #475569;">
                {html.escape(decision)} · Threshold {threshold:.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
