# Customer Churn - Data Mining Project

## Giới thiệu

Dự án phân tích và dự đoán khả năng rời bỏ dịch vụ của khách hàng trên bộ dữ liệu Telco Customer Churn. Mục tiêu là hiểu các yếu tố liên quan đến churn, xây dựng mô hình phân loại, tối ưu ngưỡng dự đoán và đề xuất hành động kinh doanh.

## Dataset

Dataset gốc được đặt tại:

```text
data/raw/telco_customer.csv
```

Bộ dữ liệu Telco Customer Churn có 7,043 khách hàng, 21 cột, trong đó biến mục tiêu là `Churn`.

## Cấu trúc thư mục

```text
configs/
  base.yaml
  classification.yaml
  clustering.yaml
data/
  raw/
    telco_customer.csv
  processed/
models/
notebooks/
  01_data_understanding.ipynb
  02_eda.ipynb
  03_classification.ipynb
  04_model_calibration_threshold_and_business_optimization.ipynb
reports/
README.md
requirements.txt
.gitignore
```

## Cài đặt

Khuyến nghị dùng Python 3.12.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m ipykernel install --user --name customer-churn-dm
```

## Thứ tự chạy notebook

1. `notebooks/01_data_understanding.ipynb`
2. `notebooks/02_eda.ipynb`
3. `notebooks/03_classification.ipynb`
4. `notebooks/04_model_calibration_threshold_and_business_optimization.ipynb`

## Đầu ra chính

- `data/processed/features.csv`
- `data/processed/target.csv`
- `models/best_model.joblib`
- bảng so sánh mô hình
- bảng tối ưu threshold
- insight và đề xuất giữ chân khách hàng

## Kết quả classification hiện tại

Logistic Regression được chọn làm model tốt nhất tại threshold mặc định `0.5`:

| Metric | Kết quả |
|---|---:|
| Accuracy | 0.738 |
| Precision - Churn Yes | 0.504 |
| Recall - Churn Yes | 0.783 |
| F1-score - Churn Yes | 0.614 |
| ROC-AUC | 0.842 |

Model ưu tiên phát hiện khách hàng churn nên Recall và F1-score của lớp `Churn = Yes` được dùng làm tiêu chí lựa chọn chính. Threshold sẽ tiếp tục được tối ưu trong notebook 04.

## Checklist hiện tại

- [x] Tạo cấu trúc thư mục dự án
- [x] Chuẩn hóa tên file dataset đầu vào
- [x] Tạo `data/processed/features.csv`
- [x] Tạo `data/processed/target.csv`
- [x] Tạo file cấu hình nền
- [x] Tạo README bản nháp
- [x] Hoàn thiện notebook 01
- [x] Hoàn thiện notebook 02
- [x] Hoàn thiện notebook 03
- [ ] Hoàn thiện notebook 04
