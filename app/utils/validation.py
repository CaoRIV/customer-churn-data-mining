from __future__ import annotations

import pandas as pd

from .constants import (
    CATEGORY_OPTIONS,
    DEFAULT_CUSTOMER,
    FEATURE_COLUMNS,
    INTERNET_ADDON_COLUMNS,
    MAX_BATCH_ROWS,
    NUMERIC_COLUMNS,
)


def template_frame() -> pd.DataFrame:
    row = {"customerID": "DEMO-0001", **DEFAULT_CUSTOMER}
    return pd.DataFrame([row], columns=["customerID", *FEATURE_COLUMNS])


def validate_batch(data: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    frame = data.copy()
    file_errors: list[str] = []

    if len(frame) > MAX_BATCH_ROWS:
        file_errors.append(
            f"File có {len(frame):,} dòng, vượt giới hạn {MAX_BATCH_ROWS:,} / Row limit exceeded."
        )
        frame["validation_error"] = file_errors[-1]
        return frame, file_errors

    missing_columns = [column for column in FEATURE_COLUMNS if column not in frame.columns]
    if missing_columns:
        file_errors.append(
            "Thiếu cột bắt buộc / Missing required columns: " + ", ".join(missing_columns)
        )
        frame["validation_error"] = file_errors[-1]
        return frame, file_errors

    if "customerID" not in frame.columns:
        frame.insert(0, "customerID", [f"ROW-{index + 1:05d}" for index in range(len(frame))])

    errors: dict[int, list[str]] = {index: [] for index in frame.index}

    for column in NUMERIC_COLUMNS:
        numeric = pd.to_numeric(frame[column], errors="coerce")
        invalid = numeric.isna()
        negative = numeric < 0
        for index in frame.index[invalid]:
            errors[index].append(f"{column}: không phải số / not numeric")
        for index in frame.index[negative.fillna(False)]:
            errors[index].append(f"{column}: không được âm / must be non-negative")
        frame[column] = numeric

    for column, allowed_values in CATEGORY_OPTIONS.items():
        invalid = ~frame[column].isin(allowed_values)
        for index in frame.index[invalid]:
            errors[index].append(
                f"{column}: giá trị không hợp lệ / invalid category"
            )

    inconsistent_phone = (frame["PhoneService"] == "No") & (
        frame["MultipleLines"] != "No phone service"
    )
    for index in frame.index[inconsistent_phone]:
        errors[index].append(
            "MultipleLines phải là 'No phone service' khi PhoneService = No"
        )

    for column in INTERNET_ADDON_COLUMNS:
        inconsistent_internet = (frame["InternetService"] == "No") & (
            frame[column] != "No internet service"
        )
        for index in frame.index[inconsistent_internet]:
            errors[index].append(
                f"{column} phải là 'No internet service' khi InternetService = No"
            )

    frame["validation_error"] = [
        "; ".join(errors[index]) for index in frame.index
    ]
    return frame, file_errors
