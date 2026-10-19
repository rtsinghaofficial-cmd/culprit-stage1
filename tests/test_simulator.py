from culprit.simulator import generate_fleet


def test_seed_reproducibility():
    a, ta = generate_fleet(1000, 42, "fault")
    b, tb = generate_fleet(1000, 42, "fault")
    assert a.equals(b)
    assert ta == tb


def test_truth_separate_from_frame():
    frame, truth = generate_fleet(1000, 42, "fault")
    assert "true_cause" not in frame.columns
    assert truth["fault_injected"] is True


def test_unknown_scenario_rejected():
    import pytest
    with pytest.raises(ValueError):
        generate_fleet(1000, 1, "made-up")
