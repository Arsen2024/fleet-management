from ..services.anomaly_detector import detect_anomalies


def test_normal_telemetry_has_no_anomalies():
    result = detect_anomalies(
        speed=80,
        engine_temperature=90,
        fuel_level=60,
    )

    assert result == []


def test_high_speed_is_detected():
    result = detect_anomalies(
        speed=145,
        engine_temperature=90,
        fuel_level=60,
    )

    assert result == ["HIGH_SPEED"]


def test_multiple_anomalies_are_detected():
    result = detect_anomalies(
        speed=145,
        engine_temperature=115,
        fuel_level=5,
    )

    assert result == [
        "HIGH_SPEED",
        "HIGH_ENGINE_TEMPERATURE",
        "LOW_FUEL_LEVEL",
    ]


def test_values_at_thresholds_are_not_anomalies():
    result = detect_anomalies(
        speed=130,
        engine_temperature=110,
        fuel_level=10,
    )

    assert result == []
