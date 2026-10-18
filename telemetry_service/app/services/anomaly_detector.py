def detect_anomalies(
    speed: float,
    engine_temperature: float,
    fuel_level: float,
) -> list[str]:
    anomalies = []

    if speed > 130:
        anomalies.append("HIGH_SPEED")

    if engine_temperature > 110:
        anomalies.append("HIGH_ENGINE_TEMPERATURE")

    if fuel_level < 10:
        anomalies.append("LOW_FUEL_LEVEL")

    return anomalies
