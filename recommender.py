"""
recommender.py

Rule-based recommendation engine.

Function:
- recommend_fix(path) -> list of suggestion strings

Rules:
- slack < -0.5 → ["Insert pipeline stage", "Break combinational path", "Optimize logic"]
- slack < 0   → ["Reduce fanout", "Buffer insertion", "Increase drive strength"]
- else        → ["No action needed"]
"""
from typing import List, Dict


def recommend_fix(path: Dict) -> List[str]:
    """
    Generate recommended fixes for a single path dict with key 'slack'.

    Args:
      path: dict with numeric 'slack' key

    Returns:
      list of recommendation strings
    """
    slack = path.get("slack")
    try:
        s = float(slack)
    except Exception:
        return ["No action needed"]

    if s < -0.5:
        return [
            "Insert pipeline stage",
            "Break combinational path",
            "Optimize logic"
        ]
    elif s < 0:
        return [
            "Reduce fanout",
            "Buffer insertion",
            "Increase drive strength"
        ]
    else:
        return ["No action needed"]


if __name__ == "__main__":
    print(recommend_fix({"slack": -0.8}))
    print(recommend_fix({"slack": -0.2}))
    print(recommend_fix({"slack": 0.3}))
