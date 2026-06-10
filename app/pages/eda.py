from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import chi2_contingency

from utils.data import load_telco_data
from utils.ui import page_header

page_header(
    "Explore & Analyze",
    "Khám phá dữ liệu / EDA Dashboard",
    "Lọc và so sánh churn theo hợp đồng, dịch vụ, hành vi thanh toán và đặc điểm khách hàng.",
)

data = load_telco_data()

filter_columns = [
    "Contract",
    "InternetService",
    "PaymentMethod",
    "Partner",
    "Dependents",
]

st.sidebar.markdown("### Bộ lọc / Filters")
filtered = data.copy()
for column in filter_columns:
    options = sorted(data[column].dropna().unique().tolist())
    selected = st.sidebar.multiselect(column, options, placeholder="All")
    if selected:
        filtered = filtered.loc[filtered[column].isin(selected)]

if filtered.empty:
    st.warning("Không có dữ liệu phù hợp bộ lọc / No rows match the selected filters.")
    st.stop()

churn_count = int(filtered["Churn"].eq("Yes").sum())
churn_rate = filtered["Churn"].eq("Yes").mean()

kpi_columns = st.columns(4)
kpi_columns[0].metric("Khách hàng / Customers", f"{len(filtered):,}")
kpi_columns[1].metric("Churn / Churned", f"{churn_count:,}")
kpi_columns[2].metric("Tỷ lệ churn / Churn rate", f"{churn_rate:.2%}")
kpi_columns[3].metric(
    "Phí tháng TB / Avg monthly",
    f"{filtered['MonthlyCharges'].mean():.2f}",
)

target_left, target_right = st.columns([0.8, 1.2], gap="large")
with target_left:
    st.subheader("Phân phối target / Target distribution")
    target_counts = (
        filtered["Churn"].value_counts().rename_axis("Churn").reset_index(name="Customers")
    )
    target_chart = px.bar(
        target_counts,
        x="Churn",
        y="Customers",
        color="Churn",
        text="Customers",
        color_discrete_map={"No": "#1E40AF", "Yes": "#D97706"},
    )
    target_chart.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(target_chart, use_container_width=True)

with target_right:
    st.subheader("Biến số / Numeric analysis")
    numeric_column = st.selectbox(
        "Chọn biến / Select metric",
        ["tenure", "MonthlyCharges", "TotalCharges"],
    )
    numeric_chart = px.box(
        filtered,
        x="Churn",
        y=numeric_column,
        color="Churn",
        points=False,
        color_discrete_map={"No": "#1E40AF", "Yes": "#D97706"},
    )
    numeric_chart.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(numeric_chart, use_container_width=True)

st.subheader("Churn rate theo nhóm / Categorical churn rate")
categorical_column = st.selectbox(
    "Chọn đặc trưng / Select feature",
    [
        "Contract",
        "InternetService",
        "OnlineSecurity",
        "TechSupport",
        "PaymentMethod",
        "PaperlessBilling",
        "Dependents",
        "Partner",
    ],
)

category_summary = (
    filtered.assign(ChurnFlag=filtered["Churn"].eq("Yes").astype(int))
    .groupby(categorical_column, observed=False)["ChurnFlag"]
    .agg(customers="count", churn_rate="mean")
    .reset_index()
    .sort_values("churn_rate", ascending=False)
)
category_summary["churn_rate_pct"] = category_summary["churn_rate"] * 100

category_chart = px.bar(
    category_summary,
    x="churn_rate_pct",
    y=categorical_column,
    orientation="h",
    color="customers",
    text=category_summary["churn_rate_pct"].map(lambda value: f"{value:.1f}%"),
    color_continuous_scale=["#DBEAFE", "#1E40AF"],
    hover_data={"customers": True, "churn_rate": ":.2%"},
    labels={
        "churn_rate_pct": "Churn rate (%)",
        "customers": "Sample size",
    },
)
category_chart.update_layout(
    yaxis={"categoryorder": "total ascending"},
    margin=dict(l=10, r=10, t=20, b=10),
    coloraxis_colorbar_title="Customers",
)
st.plotly_chart(category_chart, use_container_width=True)
st.caption(
    "Màu thể hiện quy mô mẫu. Churn rate cao ở nhóm nhỏ cần được diễn giải thận trọng / Color indicates sample size."
)

analysis_left, analysis_right = st.columns(2, gap="large")
with analysis_left:
    st.subheader("Correlation")
    correlation_data = filtered[["tenure", "MonthlyCharges", "TotalCharges"]].copy()
    correlation_data["ChurnFlag"] = filtered["Churn"].eq("Yes").astype(int)
    correlation = correlation_data.corr()
    heatmap = go.Figure(
        data=go.Heatmap(
            z=correlation.values,
            x=correlation.columns,
            y=correlation.index,
            zmin=-1,
            zmax=1,
            colorscale="RdBu_r",
            text=correlation.round(2).values,
            texttemplate="%{text}",
            hovertemplate="%{y} × %{x}: %{z:.3f}<extra></extra>",
        )
    )
    heatmap.update_layout(height=420, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(heatmap, use_container_width=True)

with analysis_right:
    st.subheader("Chi-square test")
    chi_rows = []
    for column in [
        "Contract",
        "InternetService",
        "OnlineSecurity",
        "TechSupport",
        "PaymentMethod",
        "PaperlessBilling",
        "Dependents",
        "Partner",
    ]:
        contingency = pd.crosstab(filtered[column], filtered["Churn"])
        if contingency.shape[0] < 2 or contingency.shape[1] < 2:
            continue
        chi2, p_value, degrees, _ = chi2_contingency(contingency)
        chi_rows.append(
            {
                "Feature": column,
                "Chi-square": chi2,
                "p-value": p_value,
                "Significant": p_value < 0.05,
                "DoF": degrees,
            }
        )
    chi_frame = pd.DataFrame(chi_rows).sort_values("p-value")
    st.dataframe(
        chi_frame,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Chi-square": st.column_config.NumberColumn(format="%.2f"),
            "p-value": st.column_config.NumberColumn(format="%.4g"),
            "Significant": st.column_config.CheckboxColumn(),
        },
    )
    st.caption(
        "p-value < 0.05 cho thấy có mối liên hệ thống kê, không chứng minh quan hệ nhân quả."
    )
