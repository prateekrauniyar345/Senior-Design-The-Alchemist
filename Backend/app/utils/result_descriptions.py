from __future__ import annotations

from collections import Counter
from math import sqrt
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional


CHART_INTENT_WORDS = (
    "plot",
    "chart",
    "figure",
    "histogram",
    "scatter",
    "heatmap",
    "map",
    "network",
    "visualize",
    "visualise",
    "graph",
)

FIELD_LABELS = {
    "hmin": "minimum Mohs hardness",
    "hmax": "maximum Mohs hardness",
    "density_min": "minimum density",
    "density_max": "maximum density",
    "dmeas": "measured density",
    "dcalc": "calculated density",
    "weighting": "Mindat weighting",
    "element": "element",
    "elements": "elements",
    "csystem": "crystal system",
    "diapheny": "transparency",
    "lustretype": "lustre type",
    "name": "name",
    "country": "country",
    "country_name": "country",
}


def build_result_description(
    query: str,
    vega_spec: Optional[Dict[str, Any]],
    data_rows: Optional[List[Dict[str, Any]]],
    chart_generated: bool,
) -> str:
    rows = data_rows or []

    if chart_generated and vega_spec:
        return _describe_chart(query, vega_spec, rows)

    if rows:
        return _describe_table(query, rows)

    return "The request completed, but no returned records were available to summarize."


def _describe_chart(query: str, spec: Dict[str, Any], rows: List[Dict[str, Any]]) -> str:
    mark = _mark_type(spec)
    encoding = spec.get("encoding", {}) if isinstance(spec.get("encoding"), dict) else {}

    if _is_element_distribution(spec, encoding):
        return _describe_element_distribution(query, rows)

    if mark == "bar" and _is_histogram_like(encoding):
        return _describe_histogram(query, encoding, rows)

    if mark == "bar":
        return _describe_bar_chart(query, encoding, rows)

    if mark in {"point", "circle", "square"} and _has_geo_encoding(encoding):
        return _describe_map(query, rows)

    if mark in {"point", "circle", "square"}:
        return _describe_scatter(query, encoding, rows)

    if mark == "rect":
        return _describe_heatmap(query, encoding, rows)

    return _generic_chart_description(query, spec, rows)


def _describe_table(query: str, rows: List[Dict[str, Any]]) -> str:
    row_count = len(rows)
    columns = list(rows[0].keys()) if rows else []
    important_columns = [c for c in ("name", "csystem", "hmin", "hmax", "density_min", "density_max", "country", "latitude", "longitude") if c in columns]
    names = _first_values(rows, "name", limit=3) or _first_values(rows, "txt", limit=3)

    intro = (
        "I found the matching records, but chart generation did not complete, so the table below is a preview of the returned data."
        if _has_chart_intent(query)
        else "This table is a preview of the records returned for your query."
    )
    detail = f"It includes {row_count} returned record{'s' if row_count != 1 else ''}"
    if important_columns:
        detail += f" with fields such as {', '.join(_label(c) for c in important_columns[:5])}"
    detail += "."

    if names:
        examples = f"Examples in the returned records include {', '.join(names)}."
    else:
        examples = "Use the columns in the table to inspect individual returned records."

    return (
        f"{intro}\n\n"
        f"{detail} {examples} Interpret this as the returned Mindat result set, not necessarily the entire Mindat database."
    )


def _describe_element_distribution(query: str, rows: List[Dict[str, Any]]) -> str:
    counts = Counter(_iter_elements(rows))
    row_count = len(rows)

    if not counts:
        return (
            f"This element-distribution chart is based on {row_count} returned record{'s' if row_count != 1 else ''}, "
            "but the returned data did not include usable element values to summarize."
        )

    top = counts.most_common(5)
    top_text = _format_counts(top)
    unique_count = len(counts)
    total_mentions = sum(counts.values())

    interpretation = _element_interpretation(counts)

    return (
        f"This element-distribution chart summarizes the chemical elements listed in the {row_count} returned mineral record{'s' if row_count != 1 else ''} matching your filters.\n\n"
        f"The most frequent elements are {top_text}; together, the chart contains {total_mentions} element appearances across {unique_count} distinct element symbol{'s' if unique_count != 1 else ''}. "
        f"{interpretation} Elements with very small counts occur in only a few returned records, so they represent narrower chemistries within this filtered result set."
    )


def _describe_histogram(query: str, encoding: Dict[str, Any], rows: List[Dict[str, Any]]) -> str:
    x_field = _field_from_channel(encoding, "x")
    values = _numeric_values(rows, x_field)
    label = _label(x_field)

    if not values:
        return (
            f"This histogram was requested for {label}, but the returned records did not include enough numeric values to summarize the distribution."
        )

    min_v, max_v = min(values), max(values)
    avg_v = mean(values)
    bin_label, bin_count = _densest_bin(values)
    row_count = len(rows)

    if x_field in {"hmin", "hmax"}:
        hardness_note = _hardness_interpretation(values)
        return (
            f"This histogram summarizes {label} for {len(values)} usable value{'s' if len(values) != 1 else ''} from {row_count} returned mineral record{'s' if row_count != 1 else ''}.\n\n"
            f"The values range from {min_v:g} to {max_v:g}, with an average near {avg_v:.2f}. The densest range is {bin_label}, containing {bin_count} returned record{'s' if bin_count != 1 else ''}. "
            f"{hardness_note} Interpret the pattern as a summary of the returned Mindat records for this query."
        )

    return (
        f"This histogram summarizes {label} for {len(values)} usable value{'s' if len(values) != 1 else ''} from {row_count} returned record{'s' if row_count != 1 else ''}.\n\n"
        f"The values range from {min_v:g} to {max_v:g}, with an average near {avg_v:.2f}. The densest range is {bin_label}, containing {bin_count} returned record{'s' if bin_count != 1 else ''}. "
        "Higher bars mark value ranges that appear more often in the returned dataset."
    )


def _describe_bar_chart(query: str, encoding: Dict[str, Any], rows: List[Dict[str, Any]]) -> str:
    x_field = _field_from_channel(encoding, "x")
    values = [str(row.get(x_field)).strip() for row in rows if row.get(x_field) not in (None, "")]
    counts = Counter(values)
    label = _label(x_field)

    if not counts:
        return f"This bar chart was generated for {label}, but the returned records did not include enough values to summarize."

    top = counts.most_common(5)
    return (
        f"This bar chart compares {label} values across {len(rows)} returned record{'s' if len(rows) != 1 else ''}.\n\n"
        f"The most common categories are { _format_counts(top) }. Categories with smaller bars appear in fewer returned records, so they represent less frequent groups within this query result."
    )


def _describe_scatter(query: str, encoding: Dict[str, Any], rows: List[Dict[str, Any]]) -> str:
    x_field = _field_from_channel(encoding, "x")
    y_field = _field_from_channel(encoding, "y")
    pairs = _numeric_pairs(rows, x_field, y_field)

    if not pairs:
        return "This scatter plot was generated, but the returned records did not include enough paired numeric values to summarize the relationship."

    xs, ys = zip(*pairs)
    relationship = _correlation_text(xs, ys)
    return (
        f"This scatter plot compares {_label(x_field)} with {_label(y_field)} for {len(pairs)} returned record{'s' if len(pairs) != 1 else ''} that have both values.\n\n"
        f"The {_label(x_field)} values range from {min(xs):g} to {max(xs):g}, while {_label(y_field)} ranges from {min(ys):g} to {max(ys):g}. {relationship} Points far from the main cluster are good candidates for closer inspection."
    )


def _describe_heatmap(query: str, encoding: Dict[str, Any], rows: List[Dict[str, Any]]) -> str:
    x_field = _field_from_channel(encoding, "x")
    y_field = _field_from_channel(encoding, "y")
    pair_counts = Counter(
        (str(row.get(x_field)).strip(), str(row.get(y_field)).strip())
        for row in rows
        if row.get(x_field) not in (None, "") and row.get(y_field) not in (None, "")
    )

    if not pair_counts:
        return "This heatmap was generated, but the returned records did not include enough paired category values to summarize."

    (x_value, y_value), count = pair_counts.most_common(1)[0]
    return (
        f"This heatmap summarizes how {_label(x_field)} and {_label(y_field)} combine across the returned records.\n\n"
        f"The strongest cell is {x_value} with {y_value}, appearing in {count} returned record{'s' if count != 1 else ''}. Darker cells represent combinations that occur more often in this filtered result set."
    )


def _describe_map(query: str, rows: List[Dict[str, Any]]) -> str:
    countries = Counter(
        str(row.get("country") or row.get("country_name")).strip()
        for row in rows
        if row.get("country") or row.get("country_name")
    )
    located = [
        row for row in rows
        if _to_float(row.get("latitude")) is not None and _to_float(row.get("longitude")) is not None
    ]

    if countries:
        location_text = f"The most common countries or regions in the returned records are {_format_counts(countries.most_common(3))}."
    else:
        location_text = "The plotted points represent returned records with usable latitude and longitude values."

    return (
        f"This map shows {len(located)} returned localit{'y' if len(located) == 1 else 'ies'} with usable coordinates.\n\n"
        f"{location_text} Dense clusters indicate areas where more returned locality records are present for this query."
    )


def _generic_chart_description(query: str, spec: Dict[str, Any], rows: List[Dict[str, Any]]) -> str:
    title = spec.get("title")
    if isinstance(title, dict):
        title = title.get("text") or title.get("name")
    title_text = f" for {title}" if title else ""
    return (
        f"This figure{title_text} summarizes {len(rows)} returned record{'s' if len(rows) != 1 else ''} from the Mindat query.\n\n"
        "Use the visual pattern to compare the returned records, and interpret it as a summary of this result set rather than the entire Mindat database."
    )


def _mark_type(spec: Dict[str, Any]) -> str:
    mark = spec.get("mark")
    if isinstance(mark, dict):
        return str(mark.get("type", "")).lower()
    return str(mark or "").lower()


def _field_from_channel(encoding: Dict[str, Any], channel: str) -> str:
    value = encoding.get(channel, {})
    if isinstance(value, dict):
        return str(value.get("field", ""))
    return ""


def _is_histogram_like(encoding: Dict[str, Any]) -> bool:
    x = encoding.get("x", {})
    y = encoding.get("y", {})
    return isinstance(x, dict) and isinstance(y, dict) and bool(x.get("bin")) and y.get("aggregate") == "count"


def _is_element_distribution(spec: Dict[str, Any], encoding: Dict[str, Any]) -> bool:
    x_field = _field_from_channel(encoding, "x")
    if x_field == "element":
        return True
    transforms = spec.get("transform") or []
    return any(isinstance(t, dict) and "elements" in t.get("flatten", []) for t in transforms)


def _has_geo_encoding(encoding: Dict[str, Any]) -> bool:
    return "latitude" in encoding and "longitude" in encoding


def _has_chart_intent(query: str) -> bool:
    lower = query.lower()
    return any(word in lower for word in CHART_INTENT_WORDS)


def _iter_elements(rows: Iterable[Dict[str, Any]]) -> Iterable[str]:
    for row in rows:
        elements = row.get("elements")
        if isinstance(elements, list):
            for element in elements:
                value = str(element).strip()
                if value:
                    yield value
        elif isinstance(elements, str):
            for element in elements.strip("-").split("-"):
                value = element.strip()
                if value:
                    yield value


def _numeric_values(rows: Iterable[Dict[str, Any]], field: str) -> List[float]:
    return [
        value
        for row in rows
        for value in [_to_float(row.get(field))]
        if value is not None
    ]


def _numeric_pairs(rows: Iterable[Dict[str, Any]], x_field: str, y_field: str) -> List[tuple[float, float]]:
    pairs = []
    for row in rows:
        x = _to_float(row.get(x_field))
        y = _to_float(row.get(y_field))
        if x is not None and y is not None:
            pairs.append((x, y))
    return pairs


def _to_float(value: Any) -> Optional[float]:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _densest_bin(values: List[float], bin_count: int = 5) -> tuple[str, int]:
    if len(values) == 1 or min(values) == max(values):
        value = values[0]
        return f"around {value:g}", len(values)

    low, high = min(values), max(values)
    width = (high - low) / bin_count
    bins = [0] * bin_count
    for value in values:
        index = min(int((value - low) / width), bin_count - 1)
        bins[index] += 1

    max_index = max(range(bin_count), key=lambda i: bins[i])
    start = low + (max_index * width)
    end = start + width
    return f"{start:g} to {end:g}", bins[max_index]


def _hardness_interpretation(values: List[float]) -> str:
    soft = sum(1 for v in values if v < 3)
    moderate = sum(1 for v in values if 3 <= v <= 6)
    hard = sum(1 for v in values if v > 6)
    buckets = {"soft": soft, "moderately hard": moderate, "hard": hard}
    dominant = max(buckets, key=buckets.get)
    return (
        f"The returned dataset is dominated by {dominant} minerals "
        f"({buckets[dominant]} of {len(values)} usable hardness values), with fewer records in the other hardness ranges."
    )


def _element_interpretation(counts: Counter[str]) -> str:
    common_rock_forming = {"O", "Si", "H", "Al", "Ca", "Fe", "Mg", "Na", "K"}
    top_symbols = {symbol for symbol, _ in counts.most_common(5)}
    if top_symbols & common_rock_forming:
        return (
            "The leading elements include common rock-forming or mineral-forming elements, which suggests the result set is dominated by familiar silicate, oxide, hydroxide, carbonate, sulfate, or related chemistries."
        )
    return "The leading elements identify the chemistries that appear most often within the returned records."


def _correlation_text(xs: Iterable[float], ys: Iterable[float]) -> str:
    x_values = list(xs)
    y_values = list(ys)
    if len(x_values) < 3:
        return "There are too few points to describe a reliable relationship."

    x_mean = mean(x_values)
    y_mean = mean(y_values)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    x_den = sqrt(sum((x - x_mean) ** 2 for x in x_values))
    y_den = sqrt(sum((y - y_mean) ** 2 for y in y_values))
    if x_den == 0 or y_den == 0:
        return "The returned points do not show enough variation to describe a clear relationship."

    corr = numerator / (x_den * y_den)
    if corr > 0.45:
        return "The returned records show a positive relationship: higher x-axis values generally appear with higher y-axis values."
    if corr < -0.45:
        return "The returned records show a negative relationship: higher x-axis values generally appear with lower y-axis values."
    return "The returned records do not show a strong linear relationship; the points are more scattered than trend-like."


def _format_counts(items: List[tuple[str, int]]) -> str:
    return ", ".join(f"{name} ({count})" for name, count in items)


def _first_values(rows: List[Dict[str, Any]], field: str, limit: int = 3) -> List[str]:
    values = []
    for row in rows:
        value = row.get(field)
        if value not in (None, ""):
            values.append(str(value).strip())
        if len(values) == limit:
            break
    return values


def _label(field: str) -> str:
    return FIELD_LABELS.get(field, field.replace("_", " ") if field else "the selected field")
