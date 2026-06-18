"""
ml_model.py

Trains a RandomForestRegressor on a synthetic dataset:
  features: logic_depth (int), fanout (int)
  target: slack (float)

Provides:
- predict_slack(depth, fanout) -> float

Model is trained at module import time and kept in-memory for fast predictions.
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from typing import Tuple


# Train a model on synthetic data at import time (keeps usage simple for Streamlit)
def _generate_synthetic_data(n_samples: int = 2000, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(random_state)
    logic_depth = rng.randint(1, 301, size=n_samples)  # 1..300
    fanout = rng.randint(1, 101, size=n_samples)       # 1..100
    # synthetic relationship: slack decreases with depth and fanout
    slack = 1.0 - 0.035 * logic_depth - 0.015 * fanout + rng.normal(scale=0.2, size=n_samples)
    X = np.vstack([logic_depth, fanout]).T
    y = slack
    return X, y


def _train_model() -> RandomForestRegressor:
    X, y = _generate_synthetic_data(n_samples=2000, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model


_MODEL = _train_model()


def predict_slack(depth: int, fanout: int) -> float:
    """
    Predict slack from logic depth and fanout.

    Args:
      depth: int
      fanout: int

    Returns:
      predicted slack as float
    """
    try:
        x = np.array([[int(depth), int(fanout)]], dtype=float)
        pred = _MODEL.predict(x)
        return float(pred[0])
    except Exception:
        return 0.0


if __name__ == "__main__":
    print("Example predict:", predict_slack(50, 20))
