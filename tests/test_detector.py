
from culprit.simulator import generate_fleet
from culprit.detector import detect


def test_detector_returns_list():
    frame, _ = generate_fleet(2000, 123, "fault")
    assert isinstance(detect(frame), list)


def test_null_scenario_does_not_crash():
    frame, _ = generate_fleet(2000, 123, "null")
    assert isinstance(detect(frame), list)


def test_fault_scenario_detects_correct_cohort():
    frame, truth = generate_fleet(5000, 20261010, "fault")
    predictions = detect(frame)

    assert truth["true_cause"] == "firmware=A"
    assert any(
        prediction.get("cohort") == truth["true_cause"]
        for prediction in predictions
    )


def test_simpson_scenario_avoids_false_attribution():
    frame, truth = generate_fleet(5000, 20261010, "simpson")
    predictions = detect(frame)

    assert truth["true_cause"] is None
    assert predictions == []
def test_detector_rejects_simpson_trap():
    frame, truth = generate_fleet(5000, 20261010, "simpson")
    predictions = detect(frame)

    assert truth["true_cause"] is None
    assert predictions == []