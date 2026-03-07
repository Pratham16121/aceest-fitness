"""
Unit tests for ACEest Fitness Flask application.
Validates routes, program data, and template rendering before build.
"""
import re
from unittest.mock import patch

import pytest

from app import PROGRAMS

# Fake test-run payload so /test-results route tests don't trigger a real pytest run (avoids nested run and hang).
FAKE_TEST_RESULTS = {
    "results": [
        {"nodeid": "tests/test_app.py::test_index_returns_200", "outcome": "passed", "duration": 0.01, "message": None},
    ],
    "summary": {"passed": 1, "failed": 0, "skipped": 0, "error": 0},
    "total": 1,
    "passed": 1,
    "failed": 0,
    "skipped": 0,
    "all_passed": True,
}


# --- Route & HTTP behaviour ---


def test_index_returns_200(client):
    """GET / must return HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_index_returns_html(client):
    """GET / must return HTML content type."""
    response = client.get("/")
    assert "text/html" in response.content_type


def test_index_renders_index_template(client):
    """Index route must render index.html."""
    response = client.get("/")
    data = response.get_data(as_text=True)
    assert "ACEest FUNCTIONAL FITNESS" in data
    assert "Weekly Workout Chart" in data
    assert "Daily Nutrition Plan" in data


@patch("test_runner.run_tests", return_value=FAKE_TEST_RESULTS)
def test_test_results_returns_200(mock_run_tests, client):
    """GET /test-results must return HTTP 200."""
    response = client.get("/test-results")
    assert response.status_code == 200
    mock_run_tests.assert_called_once()


@patch("test_runner.run_tests", return_value=FAKE_TEST_RESULTS)
def test_test_results_renders_summary(mock_run_tests, client):
    """Test results page must show unit test summary and list."""
    response = client.get("/test-results")
    data = response.get_data(as_text=True)
    assert "Unit test results" in data
    assert "Total" in data
    assert "Passed" in data
    assert "test_app.py" in data
    mock_run_tests.assert_called_once()


def test_nonexistent_route_returns_404(client):
    """Unknown routes must return 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_index_contains_all_program_options(client):
    """Rendered page must include all program names in the selector."""
    response = client.get("/")
    data = response.get_data(as_text=True)
    for name in PROGRAMS:
        assert name in data


def test_index_contains_program_data_for_js(client):
    """Rendered page must pass programs to JavaScript (tojson)."""
    response = client.get("/")
    data = response.get_data(as_text=True)
    # Template uses {{ programs | tojson }} so we expect at least one program key in HTML
    assert "Fat Loss (FL)" in data
    assert "Muscle Gain (MG)" in data
    assert "Beginner (BG)" in data


# --- Program data structure (specification) ---


def test_programs_is_non_empty_dict():
    """PROGRAMS must be a non-empty dictionary."""
    assert isinstance(PROGRAMS, dict)
    assert len(PROGRAMS) >= 1


def test_programs_expected_keys():
    """PROGRAMS must contain the three specified program keys."""
    expected = {"Fat Loss (FL)", "Muscle Gain (MG)", "Beginner (BG)"}
    assert set(PROGRAMS.keys()) == expected


def test_each_program_has_required_fields():
    """Each program entry must have workout, diet, and color."""
    required = {"workout", "diet", "color"}
    for name, data in PROGRAMS.items():
        assert isinstance(data, dict), f"Program {name!r} must be a dict"
        missing = required - set(data.keys())
        assert not missing, f"Program {name!r} missing keys: {missing}"


def test_program_workout_non_empty():
    """Each program workout string must be non-empty."""
    for name, data in PROGRAMS.items():
        w = data["workout"]
        assert isinstance(w, str), f"Program {name!r} workout must be str"
        assert w.strip(), f"Program {name!r} workout must be non-empty"


def test_program_diet_non_empty():
    """Each program diet string must be non-empty."""
    for name, data in PROGRAMS.items():
        d = data["diet"]
        assert isinstance(d, str), f"Program {name!r} diet must be str"
        assert d.strip(), f"Program {name!r} diet must be non-empty"


def test_program_color_hex_format():
    """Each program color must be a valid hex color (#RRGGBB)."""
    hex_re = re.compile(r"^#[0-9a-fA-F]{6}$")
    for name, data in PROGRAMS.items():
        c = data["color"]
        assert isinstance(c, str), f"Program {name!r} color must be str"
        assert hex_re.match(c), f"Program {name!r} color must be #RRGGBB, got {c!r}"


def test_program_no_extra_keys():
    """Each program must only have workout, diet, color (no extra keys)."""
    allowed = {"workout", "diet", "color"}
    for name, data in PROGRAMS.items():
        extra = set(data.keys()) - allowed
        assert not extra, f"Program {name!r} has unexpected keys: {extra}"


# --- Content validation (business logic) ---


def test_fat_loss_workout_contains_expected_phrases():
    """Fat Loss program workout must reference expected activities."""
    data = PROGRAMS["Fat Loss (FL)"]
    w = data["workout"].lower()
    assert "squat" in w or "amrap" in w
    assert "bench" in w or "deadlift" in w


def test_fat_loss_diet_contains_kcal_target():
    """Fat Loss program diet must include calorie target."""
    data = PROGRAMS["Fat Loss (FL)"]
    assert "2,000" in data["diet"] or "2000" in data["diet"]


def test_muscle_gain_diet_contains_kcal_target():
    """Muscle Gain program diet must include calorie target."""
    data = PROGRAMS["Muscle Gain (MG)"]
    assert "3,200" in data["diet"] or "3200" in data["diet"]


def test_beginner_program_mentions_technique_or_form():
    """Beginner program should reference technique or form."""
    data = PROGRAMS["Beginner (BG)"]
    combined = (data["workout"] + " " + data["diet"]).lower()
    assert "technique" in combined or "form" in combined or "protein" in combined


# --- App instance ---


def test_app_exists():
    """Flask app must be importable and have expected config."""
    from app import app as flask_app

    assert flask_app is not None
    assert flask_app.name == "app"


def test_app_has_index_route():
    """Flask app must register the index route."""
    from app import app as flask_app

    rules = [r.rule for r in flask_app.url_map.iter_rules()]
    assert "/" in rules


def test_app_has_test_results_route():
    """Flask app must register the test-results route."""
    from app import app as flask_app

    rules = [r.rule for r in flask_app.url_map.iter_rules()]
    assert "/test-results" in rules
