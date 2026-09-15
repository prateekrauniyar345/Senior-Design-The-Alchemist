# Backend/app/input_validation/parameters.py
import re
from datetime import datetime

VALID_CRYSTAL_SYSTEMS = [
    "amorphous",
    "hexagonal",
    "icosahedral",
    "isometric",
    "monoclinic",
    "orthorhombic",
    "tetragonal",
    "triclinic",
    "trigonal"
]

NUMBER_PATTERN = r"(?<![\w.])-?\d+(?:\.\d+)?"
YEAR_PATTERN = r"\b(\d{4})\b"
DATE_PATTERN = r"\b(\d{4}-\d{2}-\d{2})(?:[ T]\d{2}:\d{2}:\d{2})?\b"
CURRENT_YEAR = datetime.now().year

SUPPORTED_CHART_TYPES = [
    "histogram",
    "bar chart",
    "bar graph",
    "scatter plot",
    "scatter",
    "heatmap",
    "map",
    "geographic map",
    "network",
    "line chart",
    "pie chart",
    "line graph",
]

UNSUPPORTED_CHART_TYPES = {
    "pie chart": "Use a bar chart or histogram for category counts and distributions.",
    "3d chart": "Use a 2D histogram, scatter plot, heatmap, or map.",
    "3-d chart": "Use a 2D histogram, scatter plot, heatmap, or map.",
    "box plot": "Use a histogram or scatter plot for the current Mindat visualization flow.",
    "violin plot": "Use a histogram for the current Mindat visualization flow.",
}


def _extract_hardness_values(user_input: str) -> list[float]:
    """
    Extract only numbers that are part of an explicit Mohs hardness filter.

    Queries can mention hardness as a chart field and include unrelated numbers,
    such as discovery years. Those unrelated numbers should not be validated as
    Mohs hardness values.
    """
    lower = user_input.lower()
    values: list[float] = []

    patterns = [
        # "hardness between 5 and 7", "hardness from 5 to 7", "hardness 3-5"
        rf"\bhardness\b\s*(?:between|from)?\s*({NUMBER_PATTERN})\s*(?:-|–|—|to|and)\s*({NUMBER_PATTERN})",
        # "hardness greater than 10", "hardness <= 7", "hardness of 5"
        rf"\bhardness\b\s*(?:of|is|=|>|<|>=|<=|above|below|under|over|at\s+least|at\s+most|greater\s+than|less\s+than)?\s*({NUMBER_PATTERN})",
        # "minimum hardness of 5", "max hardness 7"
        rf"\b(?:minimum|min|maximum|max|lower|upper)\s+hardness\b\s*(?:of|is|=)?\s*({NUMBER_PATTERN})",
        # "hardness minimum 5", "hardness max 7"
        rf"\bhardness\s+(?:minimum|min|maximum|max|lower|upper)\b\s*(?:of|is|=)?\s*({NUMBER_PATTERN})",
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, lower):
            for group in match.groups():
                if group is not None:
                    values.append(float(group))

    return values


def _invalid(code: str, message: str, detail: str, suggestion: str) -> dict:
    return {
        "status": "invalid",
        "code": code,
        "message": message,
        "detail": detail,
        "suggestion": suggestion,
    }


def _validate_chart_type(lower: str) -> dict | None:
    for chart_type, suggestion in UNSUPPORTED_CHART_TYPES.items():
        if chart_type in lower:
            return _invalid(
                "unsupported_chart_type",
                "That chart type is not currently supported.",
                f"The request asks for a {chart_type}, but the current Mindat workflow supports histograms, bar charts, scatter plots, heatmaps, maps, and networks.",
                suggestion,
            )

    return None


def _validate_dates(lower: str) -> dict | None:
    date_context = r"\b(?:discovered|discovery|updated|created|modified)\b"
    if not re.search(date_context, lower):
        return None

    for date_text in re.findall(DATE_PATTERN, lower):
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            return _invalid(
                "invalid_date",
                "Date filters must use valid calendar dates.",
                f"The request includes an invalid date value: {date_text}.",
                "Use a valid date such as 2000-01-01, or a year such as discovered before 1990.",
            )

    for year_text in re.findall(YEAR_PATTERN, lower):
        year = int(year_text)
        if year < 1500 or year > CURRENT_YEAR + 1:
            return _invalid(
                "invalid_year",
                "Year filters must use realistic calendar years.",
                f"The request includes year {year}, which is outside the supported range for Mindat date filters.",
                "Use a realistic discovery or update year, such as discovered before 1990 or updated since 2000-01-01.",
            )

    return None


def _validate_result_limits(lower: str) -> dict | None:
    limit_patterns = [
        (r"\bpage\s*[- ]?size\s*(?:=|of|is)?\s*(\d+)\b", "page_size"),
        (r"\btop\s+(\d+)\b", "top_n"),
        (r"\blimit\s*(?:=|to|of|is)?\s*(\d+)\b", "limit"),
    ]

    for pattern, code in limit_patterns:
        for match in re.finditer(pattern, lower):
            value = int(match.group(1))
            if value <= 0:
                return _invalid(
                    f"invalid_{code}",
                    "Result limits must be greater than zero.",
                    f"The request includes a {code.replace('_', ' ')} value of {value}.",
                    "Use a positive result limit, such as top 50 results or page-size 500.",
                )
            if value > 1000:
                return _invalid(
                    f"invalid_{code}",
                    "Result limits are too large.",
                    f"The request includes a {code.replace('_', ' ')} value of {value}, which is above the supported limit of 1000.",
                    "Use a smaller limit, such as top 50 results or page-size 500.",
                )

    return None


def validate_parameters(user_input: str) -> dict:
    lower = user_input.lower()

    for validation_check in (
        _validate_chart_type,
        _validate_dates,
        _validate_result_limits,
    ):
        result = validation_check(lower)
        if result:
            return result

    # Hardness validation
    if "hardness" in lower:
        for n in _extract_hardness_values(user_input):
            if n < 0 or n > 10:
                return _invalid(
                    "invalid_hardness_range",
                    "Hardness must be between 0 and 10.",
                    (
                        f"The request includes a Mohs hardness value of {n:g}, "
                        "but Mindat hardness filters must stay between 0 and 10."
                    ),
                    "Try a valid Mindat hardness range, such as minerals with hardness between 3 and 7.",
                )

    # Crystal system validation
    for system in VALID_CRYSTAL_SYSTEMS:
        if system in lower:
            return {"status": "valid"}

    return {"status": "valid"}
