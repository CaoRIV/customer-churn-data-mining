from __future__ import annotations

import plotly.express as px
import streamlit as st

from utils.business import threshold_row
from utils.data import (
    load_business_thresholds,
    load_model_comparison,
    load_telco_data,
)
from utils.model import load_threshold_metadata
from utils.ui import page_header, status_strip

page_header(
    "Telco Churn Intelligence",
    "Tổng quan dự án / Project Overview",
    "Dashboard tóm tắt quy trình Data Mining, kết quả mô hình và quyết định threshold cho bài toán giữ chân khách hàng.",
)

data = load_telco_data()
comparison = load_model_comparison()
thresholds = load_business_thresholds()
threshold_metadata = load_threshold_metadata()

churn_rate = data["Churn"].eq("Yes").mean()
selected_threshold = float(threshold_metadata["selected_threshold"])
selected = threshold_row(thresholds, selected_threshold)
default = threshold_row(thresholds, 0.50)

kpi_columns = st.columns(4)
kpi_columns[0].metric("Khách hàng / Customers", f"{len(data):,}")
kpi_columns[1].metric("Tỷ lệ churn / Churn rate", f"{churn_rate:.2%}")
kpi_columns[2].metric("ROC-AUC", f"{threshold_metadata['roc_auc']:.3f}")
kpi_columns[3].metric("Threshold đề xuất / Selected", f"{selected_threshold:.2f}")

status_strip(
    "Model được chọn: Logistic Regression · Recall ưu tiên · 5/5 phase Data Mining đã hoàn thành."
)

left, right = st.columns([1.05, 0.95], gap="large")

with left:
    st.subheader("So sánh mô hình / Model comparison")
    metric_frame = comparison.melt(
        id_vars="model",
        value_vars=[
            "accuracy",
            "precision_churn_yes",
            "recall_churn_yes",
            "f1_churn_yes",
            "roc_auc",
        ],
        var_name="metric",
        value_name="score",
    )
    metric_labels = {
        "accuracy": "Accuracy",
        "precision_churn_yes": "Precision",
        "recall_churn_yes": "Recall",
        "f1_churn_yes": "F1",
        "roc_auc": "ROC-AUC",
    }
    metric_frame["metric"] = metric_frame["metric"].map(metric_labels)
    model_chart = px.bar(
        metric_frame,
        x="metric",
        y="score",
        color="model",
        barmode="group",
        range_y=[0, 1],
        color_discrete_sequence=["#1E40AF", "#D97706"],
        labels={"metric": "", "score": "Score", "model": "Model"},
    )
    model_chart.update_layout(
        legend_title_text="",
        margin=dict(l=10, r=10, t=20, b=10),
        height=390,
    )
    st.plotly_chart(model_chart, use_container_width=True)

with right:
    st.subheader("Tác động threshold / Threshold impact")
    threshold_comparison = [
        {
            "Kịch bản / Scenario": "Default 0.50",
            "Precision": default["precision"],
            "Recall": default["recall"],
            "F1": default["f1"],
            "Flagged": int(default["flagged_customers"]),
            "Missed churn": int(default["false_negative"]),
        },
        {
            "Kịch bản / Scenario": "Selected 0.30",
            "Precision": selected["precision"],
            "Recall": selected["recall"],
            "F1": selected["f1"],
            "Flagged": int(selected["flagged_customers"]),
            "Missed churn": int(selected["false_negative"]),
        },
    ]
    st.dataframe(
        threshold_comparison,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Precision": st.column_config.NumberColumn(format="%.3f"),
            "Recall": st.column_config.NumberColumn(format="%.3f"),
            "F1": st.column_config.NumberColumn(format="%.3f"),
        },
    )
    st.info(
        "Threshold 0.30 giảm số khách churn bị bỏ sót từ 81 xuống 27, đổi lại danh sách retention tăng từ 581 lên 808 khách."
    )

st.subheader("Khám phá chính / Key findings")
finding_columns = st.columns(4)
findings = [
    ("Contract", "42.71%", "Month-to-month churn rate"),
    ("Tenure", "17.98", "Average months for churn"),
    ("Fiber optic", "41.89%", "Churn rate"),
    ("Electronic check", "45.29%", "Churn rate"),
]
for column, (label, value, detail) in zip(finding_columns, findings):
    column.metric(label, value, detail)

st.subheader("Pipeline dự án / Project pipeline")
phase_columns = st.columns(5)
phases = [
    ("01", "Data understanding"),
    ("02", "EDA & statistics"),
    ("03", "Classification"),
    ("04", "Threshold"),
    ("05", "Business action"),
]
for column, (number, label) in zip(phase_columns, phases):
    column.markdown(f"**{number}**")
    column.caption(label)
    column.success("Completed")

st.caption(
    "Ứng dụng phục vụ demo học thuật và portfolio. Kết quả không thay thế đánh giá trên dữ liệu doanh nghiệp thực tế."
)
