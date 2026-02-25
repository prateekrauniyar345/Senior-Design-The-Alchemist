# Backend/tools/profile_tool.py
import json
from pathlib import Path
from typing import Any, Dict, List
from collections import Counter

from Backend.models.tool_response_models import ProfileToolResponse, ProfileToolArgs


def _rows_data_profile(rows: List[Dict[str, Any]], max_keys: int = 50, sample_n: int = 5) -> Dict[str, Any]:
    if not rows:
        return {"ok": False, "error": "No rows to profile"}

    keys = list({k for r in rows for k in r.keys()})[:max_keys]

    def infer_type(values):
        vals = [v for v in values if v is not None]
        if not vals:
            return "unknown"
        if all(isinstance(v, (int, float)) for v in vals):
            return "quantitative"
        if all(isinstance(v, str) and len(v) >= 8 and "-" in v for v in vals[:20]):
            return "temporal"
        return "nominal"

    summary = {}
    for k in keys:
        col = [r.get(k) for r in rows]
        t = infer_type(col)
        non_null = [v for v in col if v is not None]
        uniq = len(set(map(str, non_null[:2000])))
        top = Counter(map(str, non_null[:2000])).most_common(5)
        summary[k] = {
            "type": t,
            "unique_approx": uniq,
            "top_values": top,
            "sample": [r.get(k) for r in rows[:sample_n]],
        }

    return {"ok": True, "columns": summary, "row_count": len(rows)}


def profile_sample_data(args: ProfileToolArgs) -> ProfileToolResponse:
    """
    Generate a lightweight structural profile of a saved dataset for visualization planning.

    This tool reads a previously saved JSON data file (produced by a collector agent),
    extracts the `results` array, and computes a summarized schema profile suitable for
    Vega-Lite chart generation.

    The profile is intentionally compact and avoids loading full datasets into LLM state.
    It is designed to support downstream visualization planning (e.g., by the
    `vega_plot_planner` agent) without exposing raw data values.

    Expected input file format:
    - JSON object with a top-level key `results`
    - `results` must be a list of dictionaries (rows)

    For each column (up to `max_keys`):
    - Infers semantic data type:
        - "quantitative"  → numeric values
        - "temporal"      → date-like strings
        - "nominal"       → categorical / string values
    - Estimates cardinality
    - Extracts the most frequent values
    - Provides a small sample of example values

    Args:
        args (ProfileToolArgs):
            sample_data_path (str):
                Filesystem path to a JSON file containing a `results` list.
            max_keys (int, optional):
                Maximum number of columns to profile. Defaults to 50.
            sample_n (int, optional):
                Number of sample values per column. Defaults to 5.

    Returns:
        ProfileToolResponse:
            status:
                "OK" if profiling succeeds, otherwise "ERROR".
            error:
                Human-readable error message if profiling fails.
            profile:
                Dictionary containing:
                - row_count: total number of rows
                - columns: per-column summaries including:
                    - inferred type
                    - approximate unique count
                    - top values
                    - example samples

    Usage Notes:
        - This tool is typically called by the `vega_plot_planner` agent.
        - It should be invoked only after data has been collected and saved to disk.
        - The returned profile is intended for chart grammar generation, not analysis.
        - No raw data rows are returned to avoid LLM hallucination and state bloat.

    Failure Cases:
        - File does not exist
        - JSON is invalid or unreadable
        - Missing or malformed `results` field
        - Empty dataset

    Example:
        Input:
            sample_data_path="/contents/sample_data/mindat_geomaterial_response.json"

        Output:
            {
                "status": "OK",
                "profile": {
                    "row_count": 125,
                    "columns": {
                        "name": {"type": "nominal", ...},
                        "hardness": {"type": "quantitative", ...}
                    }
                }
            }
    """
    p = Path(args.sample_data_path)
    if not p.exists():
        return ProfileToolResponse(status="ERROR", error=f"File not found: {args.sample_data_path}", profile=None)

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return ProfileToolResponse(status="ERROR", error=f"Failed to parse JSON: {e}", profile=None)

    rows = data.get("results") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return ProfileToolResponse(status="ERROR", error="Invalid format: expected dict with 'results' list", profile=None)

    profile = _rows_data_profile(rows, max_keys=args.max_keys, sample_n=args.sample_n)
    if not profile.get("ok"):
        return ProfileToolResponse(status="ERROR", error=profile.get("error", "Unknown error"), profile=profile)

    return ProfileToolResponse(status="OK", error=None, profile=profile)
