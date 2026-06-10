from __future__ import annotations

import plotly.express as px
import streamlit as st

from utils.business import recalculate_business_value, threshold_row
from utils.constants import MODEL_THRESHOLD, RISK_ORDER
from utils.data import load_business_thresholds, load_telco_data
from utils.model import build_retention_list
from utils.ui import page_header

page_header(
    "Decision Support",
    "Tối ưu kinh doanh / Business Optimization",
    "Điều chỉnh threshold và giả định chi phí để đánh giá trade-off giữa phát hiện churn, quy mô chiến dịch và expected net value.",
)

base_thresholds = load_business_thresholds()

control_columns = st.columns([1.1, 1, 1, 1, 1])
selected_threshold = control_columns[0].slider(
    "Threshold",
    min_value=0.10,
    max_value=0.90,
    value=MODEL_THRESHOLD,
    step=0.05,
)
intervention_cost = control_columns[1].number_input(
    "Chi phí can thiệp / Intervention cost",
    min_value=0.0,
    value=50.0,
    step=5.0,
)
retained_value = control_columns[2].number_input(
    "Giá trị giữ lại / Retained value",
    min_value=0.0,
    value=600.0,
    step=25.0,
)
success_rate = control_columns[3].number_input(
    "Tỷ lệ thành công / Success rate",
    min_value=0.0,
    max_value=1.0,
    value=0.30,
    step=0.05,
)
missed_cost = control_columns[4].number_input(
    "Chi phí bỏ sót / Missed churn cost",
    min_value=0.0,
    value=400.0,
    step=25.0,
)

recalculated = recalculate_business_value(
    base_thresholds,
    intervention_cost_per_customer=intervention_cost,
    retained_customer_value=retained_value,
    retention_success_rate=success_rate,
    missed_churn_cost=missed_cost,
)
selected = threshold_row(recalculated, selected_threshold)

kpi_columns = st.columns(6)
kpi_columns[0].metric("Precision", f"{selected['precision']:.3f}")
kpi_columns[1].metric("Recall", f"{selected['recall']:.3f}")
kpi_columns[2].metric("F1-score", f"{selected['f1']:.3f}")
kpi_columns[3].metric("Flagged", f"{int(selected['flagged_customers']):,}")
kpi_columns[4].metric("False Negative", f"{int(selected['false_negative']):,}")
kpi_columns[5].metric("Expected net value", f"{selected['expected_net_value']:,.0f}")

chart_left, chart_right = st.columns(2, gap="large")
with chart_left:
    metric_data = recalculated.melt(
        id_vars="threshold",
        value_vars=["precision", "recall", "f1"],
        var_name="metric",
        value_name="score",
    )
    metric_chart = px.line(
        metric_data,
        x="threshold",
        y="score",
        color="metric",
        markers=True,
        color_discrete_map={
            "precision": "#1E40AF",
            "recall": "#B42318",
            "f1": "#D97706",
        },
    )
    metric_chart.add_vline(x=selected_threshold, line_dash="dash", line_color="#172033")
    metric_chart.update_layout(
        title="Metric theo threshold / Metrics by threshold",
        yaxis_range=[0, 1],
        legend_title_text="",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    st.plotly_chart(metric_chart, use_container_width=True)

with chart_right:
    value_chart = px.line(
        recalculated,
        x="threshold",
        y="expected_net_value",
        markers=True,
        color_discrete_sequence=["#15803D"],
    )
    value_chart.add_vline(x=selected_threshold, line_dash="dash", line_color="#172033")
    value_chart.update_layout(
        title="Expected net value theo threshold",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    st.plotly_chart(value_chart, use_container_width=True)

st.warning(
    "Xác suất raw có xu hướng overestimate do class weighting. Các giả định business chỉ là mô phỏng và cần được thay bằng dữ liệu thực tế."
)

st.subheader("Danh sách retention demo / Demo retention list")
data = load_telco_data()
retention = build_retention_list(data, threshold=selected_threshold)

list_controls = st.columns([1, 1, 2])
selected_tiers = list_controls[0].multiselect(
    "Risk tier",
    RISK_ORDER,
    default=["Critical", "High"],
)
only_selected = list_controls[1].toggle(
    "Chỉ khách được chọn / Selected only", value=True
)

retention_view = retention.copy()
if selected_tiers:
    retention_view = retention_view.loc[retention_view["risk_tier"].isin(selected_tiers)]
if only_selected:
    retention_view = retention_view.loc[retention_view["selected_for_retention"]]

list_controls[2].metric("Khách hàng hiển thị / Visible customers", f"{len(retention_view):,}")
st.dataframe(
    retention_view.head(1_000),
    use_container_width=True,
    hide_index=True,
    column_config={
        "churn_probability": st.column_config.ProgressColumn(
            "Churn probability", min_value=0.0, max_value=1.0, format="percent"
        ),
        "selected_for_retention": st.column_config.CheckboxColumn("Selected"),
    },
)

download_data = retention_view.to_csv(index=False).encode("utf-8")
st.download_button(
    "Tải danh sách / Download list",
    data=download_data,
    file_name=f"retention_priority_threshold_{selected_threshold:.2f}.csv",
    mime="text/csv",
    icon=":material/download:",
)
st.caption(
    "Danh sách vận hành không chứa actual_churn. Ground truth chỉ dùng cho đánh giá mô hình."
)
