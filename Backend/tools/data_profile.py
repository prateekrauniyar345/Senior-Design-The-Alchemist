# Backend/tools/profile.py
from typing import List, Dict, Any
from collections import Counter
import math

def rows_data_profile(rows: List[Dict[str, Any]], max_keys: int = 50, sample_n: int = 5) -> Dict[str, Any]:
    if not rows:
        return {"ok": False, "error": "No rows to profile"}

    # collect keys
    keys = list({k for r in rows for k in r.keys()})[:max_keys]

    def infer_type(values):
        vals = [v for v in values if v is not None]
        if not vals:
            return "unknown"
        # numeric?
        if all(isinstance(v, (int, float)) for v in vals):
            return "quantitative"
        # datetime-ish string?
        if all(isinstance(v, str) and len(v) >= 8 and "-" in v for v in vals[:20]):
            return "temporal"
        return "nominal"

    summary = {}
    for k in keys:
        col = [r.get(k) for r in rows]
        t = infer_type(col)
        non_null = [v for v in col if v is not None]
        uniq = len(set(map(str, non_null[:2000])))  # cheap
        top = Counter(map(str, non_null[:2000])).most_common(5)
        summary[k] = {
            "type": t,
            "unique_approx": uniq,
            "top_values": top,
            "sample": [r.get(k) for r in rows[:sample_n]]
        }

    return {"ok": True, "columns": summary, "row_count": len(rows)}
