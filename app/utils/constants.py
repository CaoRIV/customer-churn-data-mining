from __future__ import annotations

FEATURE_COLUMNS = [
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
]

NUMERIC_COLUMNS = ["tenure", "MonthlyCharges", "TotalCharges"]

CATEGORY_OPTIONS = {
    "gender": ["Female", "Male"],
    "SeniorCitizen": ["No", "Yes"],
    "Partner": ["No", "Yes"],
    "Dependents": ["No", "Yes"],
    "PhoneService": ["No", "Yes"],
    "MultipleLines": ["No", "Yes", "No phone service"],
    "InternetService": ["DSL", "Fiber optic", "No"],
    "OnlineSecurity": ["No", "Yes", "No internet service"],
    "OnlineBackup": ["No", "Yes", "No internet service"],
    "DeviceProtection": ["No", "Yes", "No internet service"],
    "TechSupport": ["No", "Yes", "No internet service"],
    "StreamingTV": ["No", "Yes", "No internet service"],
    "StreamingMovies": ["No", "Yes", "No internet service"],
    "Contract": ["Month-to-month", "One year", "Two year"],
    "PaperlessBilling": ["No", "Yes"],
    "PaymentMethod": [
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ],
}

INTERNET_ADDON_COLUMNS = [
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
]

RISK_ORDER = ["Critical", "High", "Watchlist", "Low"]

RISK_COLORS = {
    "Critical": "#B42318",
    "High": "#D97706",
    "Watchlist": "#2563EB",
    "Low": "#15803D",
}

MODEL_THRESHOLD = 0.30
CRITICAL_THRESHOLD = 0.50
WATCHLIST_THRESHOLD = 0.15

MAX_BATCH_ROWS = 50_000
MAX_UPLOAD_BYTES = 20 * 1024 * 1024

DEFAULT_CUSTOMER = {
    "gender": "Female",
    "SeniorCitizen": "No",
    "Partner": "No",
    "Dependents": "No",
    "tenure": 12,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "No",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "No",
    "StreamingMovies": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 75.0,
    "TotalCharges": 900.0,
}

FEATURE_LABELS = {
    "gender": "Giới tính / Gender",
    "SeniorCitizen": "Người cao tuổi / Senior citizen",
    "Partner": "Có partner / Partner",
    "Dependents": "Có người phụ thuộc / Dependents",
    "tenure": "Thời gian sử dụng / Tenure (months)",
    "PhoneService": "Dịch vụ điện thoại / Phone service",
    "MultipleLines": "Nhiều đường dây / Multiple lines",
    "InternetService": "Dịch vụ Internet / Internet service",
    "OnlineSecurity": "Bảo mật trực tuyến / Online security",
    "OnlineBackup": "Sao lưu trực tuyến / Online backup",
    "DeviceProtection": "Bảo vệ thiết bị / Device protection",
    "TechSupport": "Hỗ trợ kỹ thuật / Tech support",
    "StreamingTV": "Streaming TV",
    "StreamingMovies": "Streaming movies",
    "Contract": "Hợp đồng / Contract",
    "PaperlessBilling": "Hóa đơn điện tử / Paperless billing",
    "PaymentMethod": "Phương thức thanh toán / Payment method",
    "MonthlyCharges": "Phí hàng tháng / Monthly charges",
    "TotalCharges": "Tổng phí / Total charges",
}
