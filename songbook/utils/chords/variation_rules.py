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
'''
def select_variations(base_name, all_variations, user_pref_show_alt, requested_dict):
    result = []

    # Always include v0
    if len(all_variations) > 0:
        result.append(all_variations[0])

    forced_list = requested_dict.get(base_name, None)

    # 🐛 DEBUG
    print(f"  select_variations for '{base_name}':")
    print(f"    - total variations available: {len(all_variations)}")
    print(f"    - forced variations from requested_dict: {forced_list}")
    print(f"    - user_pref_show_alt: {user_pref_show_alt}")

    # SONG FORCES VARIATION(S) (from suggested_alternate OR inline [C(1)])
    if forced_list is not None:
        print(f"    - FORCED variations detected: {forced_list}")
        for forced in forced_list:
            if forced < len(all_variations) and forced != 0:
                if all_variations[forced] not in result:
                    result.append(all_variations[forced])
                    print(f"    - Added variation {forced}")
            else:
                print(f"    - Forced variation {forced} is invalid or is 0")
        print(f"    - Final variations: {len(result)} variations")
        return result

    # USER PREF: INCLUDE DEFAULT ALTERNATE v1
    if user_pref_show_alt and len(all_variations) > 1:
        result.append(all_variations[1])
        print(f"    - Added v1 due to user preference")

    print(f"    - Final variations: {len(result)} variations")
    return result
'''