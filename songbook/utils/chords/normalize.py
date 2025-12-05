# normalize.py
from typing import List, Dict, Any, Optional

def normalize_variation(variation: Any) -> Dict[str, Any]:
    """
    Normalize a chord variation dict into standard form:
    {'positions': [...], 'baseFret': int, 'barre': {...} or None}.
    Uses the values in JSON directly without recomputation.
    """
    if isinstance(variation, dict):
        return {
            "positions": variation.get("positions", []),
            "baseFret": variation.get("baseFret", 1),
            "barre": variation.get("barre")
        }

    # If a plain list/tuple is provided (legacy/fallback)
    positions = list(variation) if isinstance(variation, (list, tuple)) else []
    return {"positions": positions, "baseFret": 1, "barre": None}


