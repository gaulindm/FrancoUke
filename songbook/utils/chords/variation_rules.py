# variation_rules.py
import re
from typing import List, Dict, Any, Optional

from typing import Tuple, Optional

def parse_requested_variation(chord_name: str) -> Tuple[str, Optional[int]]:
    """
    Parse '[C(1)]' style notation.
    Returns (base_name, forced_index or None)
    """
    match = re.match(r"^([A-G][#b]?m?(?:add\d+)?)(?:\((\d+)\))?$", chord_name)
    if not match:
        return chord_name, None
    base = match.group(1)
    forced = match.group(2)
    return base, int(forced) if forced is not None else None


from typing import List, Dict, Any, Optional

def select_variations(
    base_name: str,
    all_variations: List[Dict[str, Any]],
    user_pref_show_alternates: bool,
    requested_variations: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Determine which variations to include for a chord.

    Rules:
    - Always include variation 0 (first variation)
    - If song forces variation N (via [C(N)]), include it even if user disables alternates
    - If user preference enables alternates, include variation 1
    - If forced variation is 0, this suppresses automatic alternates
    """
    result: List[Dict[str, Any]] = []

    # Always include variation 0 if present
    if len(all_variations) > 0:
        result.append(all_variations[0])

    forced: Optional[int] = requested_variations.get(base_name, None)

    # If song forces variation N
    if forced is not None and forced < len(all_variations):
        if forced != 0:
            result.append(all_variations[forced])
        return result

    # No forced variation -> check user preference
    if user_pref_show_alternates and len(all_variations) > 1:
        result.append(all_variations[1])

    return result

