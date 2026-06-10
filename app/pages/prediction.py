from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.constants import (
    CATEGORY_OPTIONS,
    FEATURE_COLUMNS,
    FEATURE_LABELS,
    INTERNET_ADDON_COLUMNS,
    MAX_UPLOAD_BYTES,
    MODEL_THRESHOLD,
)
from utils.model import (
    customer_contributions,
    retention_recommendations,
    risk_tier,
    score_customers,
)
from utils.ui import page_header, risk_panel
from utils.validation import template_frame, validate_batch

page_header(
    "Model Inference",
    "Dự đoán churn / Churn Prediction",
    "Dự đoán một khách hàng hoặc chấm điểm hàng loạt bằng pipeline Logistic Regression đã huấn luyện.",
)

single_tab, batch_tab = st.tabs(
    ["Khách hàng đơn / Single customer", "Tệp CSV / Batch scoring"]
)

with single_tab:
    st.subheader("Thông tin khách hàng / Customer profile")

    customer_id = st.text_input(
        "Mã khách hàng / Customer ID",
        placeholder="Optional",
        key="single_customer_id",
    )

    identity_columns = st.columns(4)
    gender = identity_columns[0].selectbox(
        FEATURE_LABELS["gender"], CATEGORY_OPTIONS["gender"], key="single_gender"
    )
    senior = identity_columns[1].selectbox(
        FEATURE_LABELS["SeniorCitizen"],
        CATEGORY_OPTIONS["SeniorCitizen"],
        key="single_senior",
    )
    partner = identity_columns[2].selectbox(
        FEATURE_LABELS["Partner"], CATEGORY_OPTIONS["Partner"], key="single_partner"
    )
    dependents = identity_columns[3].selectbox(
        FEATURE_LABELS["Dependents"],
        CATEGORY_OPTIONS["Dependents"],
        key="single_dependents",
    )

    service_columns = st.columns(3)
    tenure = service_columns[0].number_input(
        FEATURE_LABELS["tenure"], min_value=0, max_value=120, value=12, step=1
    )
    phone_service = service_columns[1].selectbox(
        FEATURE_LABELS["PhoneService"],
        CATEGORY_OPTIONS["PhoneService"],
        index=1,
        key="single_phone",
    )
    if phone_service == "No":
        multiple_lines = service_columns[2].selectbox(
            FEATURE_LABELS["MultipleLines"],
            ["No phone service"],
            disabled=True,
            key="single_lines_no_phone",
        )
    else:
        multiple_lines = service_columns[2].selectbox(
            FEATURE_LABELS["MultipleLines"],
            ["No", "Yes"],
            key="single_lines",
        )

    internet_service = st.selectbox(
        FEATURE_LABELS["InternetService"],
        CATEGORY_OPTIONS["InternetService"],
        index=1,
        key="single_internet",
    )

    addon_values = {}
    addon_columns = st.columns(3)
    for index, column in enumerate(INTERNET_ADDON_COLUMNS):
        target_column = addon_columns[index % 3]
        if internet_service == "No":
            addon_values[column] = target_column.selectbox(
                FEATURE_LABELS[column],
                ["No internet service"],
                disabled=True,
                key=f"single_{column}_no_internet",
            )
        else:
            addon_values[column] = target_column.selectbox(
                FEATURE_LABELS[column],
                ["No", "Yes"],
                key=f"single_{column}",
            )

    contract_columns = st.columns(3)
    contract = contract_columns[0].selectbox(
        FEATURE_LABELS["Contract"], CATEGORY_OPTIONS["Contract"], key="single_contract"
    )
    paperless = contract_columns[1].selectbox(
        FEATURE_LABELS["PaperlessBilling"],
        CATEGORY_OPTIONS["PaperlessBilling"],
        index=1,
        key="single_paperless",
    )
    payment = contract_columns[2].selectbox(
        FEATURE_LABELS["PaymentMethod"],
        CATEGORY_OPTIONS["PaymentMethod"],
        key="single_payment",
    )

    charge_columns = st.columns([1, 1, 0.8])
    monthly_charges = charge_columns[0].number_input(
        FEATURE_LABELS["MonthlyCharges"],
        min_value=0.0,
        max_value=500.0,
        value=75.0,
        step=0.5,
    )
    auto_total = charge_columns[2].toggle(
        "Tự tính tổng phí / Auto total", value=True
    )
    computed_total = float(tenure) * float(monthly_charges)
    total_charges = charge_columns[1].number_input(
        FEATURE_LABELS["TotalCharges"],
        min_value=0.0,
        max_value=50_000.0,
        value=computed_total if auto_total else 900.0,
        step=1.0,
        disabled=auto_total,
    )
    if auto_total:
        total_charges = computed_total
        charge_columns[1].caption(f"Calculated: {computed_total:,.2f}")

    customer = {
        "gender": gender,
        "SeniorCitizen": senior,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": int(tenure),
        "PhoneService": phone_service,
        "MultipleLines": multiple_lines,
        "InternetService": internet_service,
        **addon_values,
        "Contract": contract,
        "PaperlessBilling": paperless,
        "PaymentMethod": payment,
        "MonthlyCharges": float(monthly_charges),
        "TotalCharges": float(total_charges),
    }

    if st.button(
        "Phân tích rủi ro / Analyze risk",
        type="primary",
        icon=":material/analytics:",
        use_container_width=True,
    ):
        customer_frame = pd.DataFrame([customer], columns=FEATURE_COLUMNS)
        scored = score_customers(customer_frame)
        probability = float(scored.loc[0, "churn_probability"])
        tier = risk_tier(probability)
        st.session_state["single_prediction"] = {
            "customer_id": customer_id,
            "customer": customer,
            "probability": probability,
            "tier": tier,
        }

    result = st.session_state.get("single_prediction")
    if result:
        st.divider()
        result_left, result_right = st.columns([0.8, 1.2], gap="large")
        with result_left:
            risk_panel(result["probability"], result["tier"], MODEL_THRESHOLD)
            st.markdown("#### Hành động đề xuất / Recommended actions")
            for recommendation in retention_recommendations(
                result["customer"], result["probability"]
            ):
                st.markdown(f"- {recommendation}")

        with result_right:
            st.markdown("#### Yếu tố đóng góp / Local contributions")
            increasing, decreasing = customer_contributions(
                pd.DataFrame([result["customer"]], columns=FEATURE_COLUMNS)
            )
            contribution_frame = pd.concat(
                [
                    increasing.assign(direction="Tăng risk / Increase"),
                    decreasing.assign(direction="Giảm risk / Decrease"),
                ],
                ignore_index=True,
            )
            contribution_chart = px.bar(
                contribution_frame,
                x="contribution",
                y="feature",
                color="direction",
                orientation="h",
                color_discrete_map={
                    "Tăng risk / Increase": "#B42318",
                    "Giảm risk / Decrease": "#15803D",
                },
                labels={"contribution": "Absolute contribution", "feature": ""},
            )
            contribution_chart.update_layout(
                yaxis={"categoryorder": "total ascending"},
                legend_title_text="",
                margin=dict(l=10, r=10, t=10, b=10),
                height=390,
            )
            st.plotly_chart(contribution_chart, use_container_width=True)
            st.caption(
                "Coefficient contribution giải thích dự đoán của model, không chứng minh quan hệ nhân quả."
            )

with batch_tab:
    st.subheader("Batch scoring")
    template_csv = template_frame().to_csv(index=False).encode("utf-8")
    st.download_button(
        "Tải CSV mẫu / Download template",
        data=template_csv,
        file_name="telco_churn_scoring_template.csv",
        mime="text/csv",
        icon=":material/download:",
    )

    uploaded_file = st.file_uploader(
        "Tải file CSV / Upload CSV",
        type=["csv"],
        help="Maximum 20 MB and 50,000 rows.",
    )

    if uploaded_file is not None:
        if uploaded_file.size > MAX_UPLOAD_BYTES:
            st.error("File vượt quá 20 MB / File exceeds the 20 MB limit.")
        else:
            try:
                batch_data = pd.read_csv(uploaded_file)
            except Exception as exc:
                st.error(f"Không thể đọc CSV / Unable to read CSV: {exc}")
            else:
                validated, file_errors = validate_batch(batch_data)
                if file_errors:
                    for error in file_errors:
                        st.error(error)

                if all(column in validated.columns for column in FEATURE_COLUMNS):
                    valid_mask = validated["validation_error"].eq("")
                    output = validated[["customerID", "validation_error"]].copy()
                    output["churn_probability"] = pd.NA
                    output["predicted_churn"] = pd.NA
                    output["threshold"] = MODEL_THRESHOLD
                    output["risk_tier"] = pd.NA

                    if valid_mask.any():
                        scores = score_customers(validated.loc[valid_mask, FEATURE_COLUMNS])
                        output.loc[valid_mask, "churn_probability"] = scores[
                            "churn_probability"
                        ].values
                        output.loc[valid_mask, "predicted_churn"] = scores[
                            "predicted_churn"
                        ].values
                        output.loc[valid_mask, "risk_tier"] = scores["risk_tier"].values

                    valid_count = int(valid_mask.sum())
                    invalid_count = int((~valid_mask).sum())
                    summary_columns = st.columns(3)
                    summary_columns[0].metric("Tổng dòng / Rows", f"{len(validated):,}")
                    summary_columns[1].metric("Hợp lệ / Valid", f"{valid_count:,}")
                    summary_columns[2].metric("Lỗi / Invalid", f"{invalid_count:,}")

                    st.dataframe(output.head(200), use_container_width=True, hide_index=True)
                    output_csv = output.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "Tải kết quả / Download results",
                        data=output_csv,
                        file_name="telco_churn_scored.csv",
                        mime="text/csv",
                        icon=":material/download:",
                        type="primary",
                    )
