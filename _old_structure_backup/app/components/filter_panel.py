"""
FilterPanel Component - Styled filter controls and selections

Reusable component for data filtering and parameter selection
"""
import streamlit as st
from typing import Optional, List, Any, Dict


def filter_panel(
    title: str = "Filters",
    icon: str = "🔍",
) -> None:
    """
    Create a collapsible filter panel in the sidebar

    Args:
        title: Panel title (default: "Filters")
        icon: Icon to display (default: "🔍")

    Example:
        with filter_panel("Search & Filter"):
            period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"])
            threshold = st.slider("Min Volatility", 0.0, 1.0, 0.1)
    """
    with st.sidebar:
        st.markdown(f"### {icon} {title}")
        st.divider()


def filter_row(
    filters: Dict[str, dict],
    columns: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Create a row of filter controls in columns

    Args:
        filters: Dict of filter_id -> {
            "label": str,
            "type": "select" | "slider" | "text" | "multiselect",
            "options": list (for select/multiselect),
            "min": float (for slider),
            "max": float (for slider),
            "value": Any (default value),
            "key": str (optional, for state management)
        }
        columns: Number of columns (default: len(filters))

    Returns:
        Dict of filter_id -> selected value

    Example:
        results = filter_row({
            "period": {
                "label": "Period",
                "type": "select",
                "options": ["1mo", "3mo", "6mo", "1y"],
                "value": "1y"
            },
            "volatility": {
                "label": "Min Volatility",
                "type": "slider",
                "min": 0.0,
                "max": 1.0,
                "value": 0.1
            }
        })
    """
    if columns is None:
        columns = len(filters)

    cols = st.columns(columns)
    results = {}

    for idx, (filter_id, filter_config) in enumerate(filters.items()):
        with cols[idx % columns]:
            label = filter_config.get("label", filter_id)
            filter_type = filter_config.get("type", "text")
            key = filter_config.get("key", f"filter_{filter_id}")

            if filter_type == "select":
                results[filter_id] = st.selectbox(
                    label,
                    options=filter_config.get("options", []),
                    index=0,
                    key=key,
                )

            elif filter_type == "multiselect":
                results[filter_id] = st.multiselect(
                    label,
                    options=filter_config.get("options", []),
                    default=filter_config.get("value", []),
                    key=key,
                )

            elif filter_type == "slider":
                results[filter_id] = st.slider(
                    label,
                    min_value=filter_config.get("min", 0.0),
                    max_value=filter_config.get("max", 100.0),
                    value=filter_config.get("value", 50.0),
                    key=key,
                )

            elif filter_type == "text":
                results[filter_id] = st.text_input(
                    label,
                    value=filter_config.get("value", ""),
                    key=key,
                )

    return results


def advanced_filters(
    title: str = "Advanced Filters",
) -> Dict[str, Any]:
    """
    Create an expandable advanced filter section

    Args:
        title: Section title

    Returns:
        Filter results dict (can be empty if expander is closed)

    Example:
        filters = advanced_filters("Advanced Options")
        if filters:
            period = filters.get("period")
            ...
    """
    with st.expander(f"⚙️ {title}", expanded=False):
        results = filter_row({
            "start_date": {
                "label": "Start Date",
                "type": "text",
                "value": "2024-01-01"
            },
            "end_date": {
                "label": "End Date",
                "type": "text",
                "value": "2025-01-01"
            },
            "data_quality": {
                "label": "Data Quality Filter",
                "type": "slider",
                "min": 0,
                "max": 100,
                "value": 80
            }
        })
        return results

    return {}
