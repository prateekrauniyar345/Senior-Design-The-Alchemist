# Backend/viz/specs/histogram.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

def build_histogram_vega_spec(
    element_counts: pd.Series,
    title: Optional[str] = None,
    top_n: int = 20,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Deterministic Vega-Lite spec for a bar histogram of element frequencies.
    Returns (spec, chart_data).
    """
    top = element_counts.head(top_n)
    chart_data = [{"element": str(k), "count": int(v)} for k, v in top.items()]

    spec: Dict[str, Any] = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": title or f"Top {top_n} Elements Distribution in Mineral Dataset",
        "data": {"values": chart_data},  # OR omit this and provide data separately
        "mark": {"type": "bar"},
        "encoding": {
            "x": {
                "field": "element",
                "type": "nominal",
                "sort": "-y",
                "axis": {"labelAngle": -45},
            },
            "y": {"field": "count", "type": "quantitative"},
            "tooltip": [
                {"field": "element", "type": "nominal"},
                {"field": "count", "type": "quantitative"},
            ],
        },
    }
    return spec, chart_data
