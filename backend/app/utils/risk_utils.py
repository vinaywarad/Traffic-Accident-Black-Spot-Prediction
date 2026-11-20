"""
Risk score → risk level and confidence utilities.
"""


def score_to_risk_level(score: float) -> str:
    """
    Convert a probability score to a human-readable risk level.

    Args:
        score: Probability of being a black spot (0.0–1.0).

    Returns:
        'LOW', 'MEDIUM', 'HIGH', or 'CRITICAL'
    """
    if score >= 0.75:
        return "CRITICAL"
    if score >= 0.55:
        return "HIGH"
    if score >= 0.35:
        return "MEDIUM"
    return "LOW"


def score_to_confidence(score: float, threshold: float) -> float:
    """
    Compute confidence as normalized distance from the decision boundary.

    Args:
        score: Predicted probability.
        threshold: Decision threshold.

    Returns:
        Confidence float in [0.5, 1.0].
    """
    return round(min(abs(score - threshold) * 2 + 0.5, 1.0), 4)
