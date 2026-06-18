"""
analyzer.py

Provides analyze_paths(paths) which:
- Accepts a list of path dicts (each with 'slack' key)
- Returns (violations, ok_paths)
  - violations: list of dicts with slack < 0, sorted worst-first (most negative first)
  - ok_paths: list of dicts with slack >= 0

The function preserves input dicts but will attach a 'type' field ("VIOLATION" or "OK").
"""
from typing import List, Tuple, Dict


def analyze_paths(paths: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Split and sort paths.

    Args:
      paths: list of dicts, each must have 'slack' numeric key.

    Returns:
      (violations, ok_paths)
    """
    violations = []
    ok = []

    if not paths:
        return violations, ok

    for p in paths:
        # defensive: ensure slack exists and is numeric
        try:
            s = float(p.get("slack"))
        except Exception:
            # treat missing/invalid as OK (could be tuned)
            p["type"] = "OK"
            ok.append(p)
            continue

        if s < 0:
            p["type"] = "VIOLATION"
            violations.append(p)
        else:
            p["type"] = "OK"
            ok.append(p)

    # SORT: worst slack first (most negative first). ascending sort of slack achieves that.
    violations.sort(key=lambda x: float(x.get("slack") if x.get("slack") is not None else 0.0))
    return violations, ok


if __name__ == "__main__":
    sample = [
        {"slack": 0.5, "arrival": 10, "required": 9.5},
        {"slack": -0.3, "arrival": 12, "required": 11.7},
        {"slack": -1.2, "arrival": 15, "required": 13.8},
    ]
    v, o = analyze_paths(sample)
    print("Violations:", v)
    print("OK:", o)
