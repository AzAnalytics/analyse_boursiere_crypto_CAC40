"""
MetricCard Component - Styled metric display with animations

Reusable component for displaying KPIs, statistics, and metrics
"""
import streamlit as st
from typing import Optional


def metric_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "positive",
    icon: Optional[str] = None,
) -> None:
    """
    Display a styled metric card with optional delta indicator

    Args:
        title: Card title (e.g., "Sharpe Ratio")
        value: Main metric value (e.g., "0.67")
        delta: Optional change indicator (e.g., "+2.3%")
        delta_color: "positive" (green) or "negative" (red)
        icon: Optional emoji icon (e.g., "📊")

    Example:
        metric_card("Volatility", "18.5%", "+1.2%", delta_color="negative")
    """
    delta_class = f"metric-card-delta {delta_color}"
    delta_html = ""

    if delta:
        delta_html = f'<div class="{delta_class}">{delta}</div>'

    icon_html = f'<span style="font-size: 1.2em; margin-right: 8px;">{icon}</span>' if icon else ""

    html = f"""
    <div class="metric-card">
        <div class="metric-card-title">{icon_html}{title}</div>
        <div class="metric-card-value">{value}</div>
        {delta_html}
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


def metric_card_grid(
    metrics: dict[str, dict],
    columns: int = 3,
) -> None:
    """
    Display multiple metric cards in a responsive grid

    Args:
        metrics: Dict of metric_id -> {"title": str, "value": str, "delta": str, "delta_color": str, "icon": str}
        columns: Number of columns (default: 3)

    Example:
        metric_card_grid({
            "sharpe": {
                "title": "Sharpe Ratio",
                "value": "0.67",
                "delta": "+0.05",
                "delta_color": "positive",
                "icon": "📊"
            },
            "volatility": {
                "title": "Volatility",
                "value": "18.5%",
                "delta": "-1.2%",
                "delta_color": "positive",
                "icon": "📈"
            }
        })
    """
    cols = st.columns(columns)

    for idx, (metric_id, metric_data) in enumerate(metrics.items()):
        with cols[idx % columns]:
            metric_card(
                title=metric_data.get("title", ""),
                value=metric_data.get("value", ""),
                delta=metric_data.get("delta"),
                delta_color=metric_data.get("delta_color", "positive"),
                icon=metric_data.get("icon"),
            )
