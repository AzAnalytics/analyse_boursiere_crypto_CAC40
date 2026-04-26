"""
ChartCard Component - Styled container for charts

Wraps Streamlit charts with consistent styling and layout
"""
import streamlit as st
from typing import Optional, Callable


def chart_card(
    title: str,
    chart_func: Callable,
    description: Optional[str] = None,
    help_text: Optional[str] = None,
) -> None:
    """
    Display a chart within a styled card container

    Args:
        title: Card title
        chart_func: Function that creates/displays the chart (receives no args)
        description: Optional subtitle or description
        help_text: Optional tooltip/help text

    Example:
        def draw_price_chart():
            st.line_chart(df[["Close"]])

        chart_card(
            title="Stock Price History",
            chart_func=draw_price_chart,
            description="Last 12 months"
        )
    """
    st.markdown(
        f"""
        <div style="margin-bottom: 20px;">
            <h3 style="margin: 0 0 5px 0; color: var(--text-primary);">{title}</h3>
            {f'<p style="margin: 0; font-size: 0.875rem; color: var(--text-secondary);">{description}</p>' if description else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Create styled container
    with st.container(border=True):
        chart_func()

    if help_text:
        st.caption(help_text)


def chart_grid(
    charts: dict[str, dict],
    columns: int = 2,
) -> None:
    """
    Display multiple charts in a responsive grid

    Args:
        charts: Dict of chart_id -> {"title": str, "func": callable, "description": str, "help_text": str}
        columns: Number of columns (default: 2)

    Example:
        def draw_price():
            st.line_chart(df[["Close"]])

        def draw_returns():
            st.bar_chart(df[["Daily_Return"]])

        chart_grid({
            "price": {
                "title": "Price Chart",
                "func": draw_price,
                "description": "Historical prices"
            },
            "returns": {
                "title": "Daily Returns",
                "func": draw_returns,
                "description": "Return distribution"
            }
        }, columns=2)
    """
    cols = st.columns(columns)

    for idx, (chart_id, chart_data) in enumerate(charts.items()):
        with cols[idx % columns]:
            chart_card(
                title=chart_data.get("title", ""),
                chart_func=chart_data.get("func", lambda: None),
                description=chart_data.get("description"),
                help_text=chart_data.get("help_text"),
            )
