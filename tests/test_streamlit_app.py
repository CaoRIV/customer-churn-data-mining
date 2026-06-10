from __future__ import annotations

from streamlit.testing.v1 import AppTest


def test_overview_page_renders_without_exception() -> None:
    app = AppTest.from_file("app/app.py").run(timeout=30)
    assert len(app.exception) == 0
    assert len(app.metric) >= 4


def test_all_navigation_pages_render_without_exception() -> None:
    page_paths = [
        "pages/eda.py",
        "pages/prediction.py",
        "pages/business.py",
    ]
    for page_path in page_paths:
        app = AppTest.from_file("app/app.py").run(timeout=30)
        app.switch_page(page_path).run(timeout=30)
        assert len(app.exception) == 0, page_path


def test_business_default_threshold_metrics() -> None:
    app = AppTest.from_file("app/app.py").run(timeout=30)
    app.switch_page("pages/business.py").run(timeout=30)
    metric_values = [metric.value for metric in app.metric]
    assert "0.928" in metric_values
    assert "808" in metric_values
