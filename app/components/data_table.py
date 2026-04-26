"""
DataTable Component - Styled data display with formatting

Reusable component for displaying tabular data with consistent styling
"""
import streamlit as st
import pandas as pd
from typing import Optional, List, Callable


def data_table(
    df: pd.DataFrame,
    title: Optional[str] = None,
    description: Optional[str] = None,
    show_index: bool = False,
    highlight_cols: Optional[List[str]] = None,
    format_rules: Optional[dict] = None,
    use_container_width: bool = True,
) -> None:
    """
    Display a formatted, styled DataFrame with optional highlighting

    Args:
        df: Pandas DataFrame to display
        title: Optional table title
        description: Optional table description
        show_index: Whether to show DataFrame index (default: False)
        highlight_cols: List of columns to highlight (optional)
        format_rules: Dict of column -> format_func for custom formatting
        use_container_width: Use full container width (default: True)

    Example:
        data_table(
            df,
            title="Stock Data",
            description="Last 30 days",
            highlight_cols=["Close"],
            format_rules={
                "Close": lambda x: f"${x:.2f}",
                "Volume": lambda x: f"{x:,.0f}"
            }
        )
    """
    if title:
        st.markdown(f"### {title}")
    if description:
        st.caption(description)

    # Apply formatting rules if provided
    display_df = df.copy()
    if format_rules:
        for col, format_func in format_rules.items():
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(format_func)

    # Display with Streamlit styling
    st.dataframe(
        display_df,
        use_container_width=use_container_width,
        hide_index=not show_index,
    )


def summary_stats(
    df: pd.DataFrame,
    title: str = "Summary Statistics",
    numeric_only: bool = True,
) -> None:
    """
    Display summary statistics in a styled format

    Args:
        df: DataFrame to analyze
        title: Section title
        numeric_only: Only show numeric columns (default: True)

    Example:
        summary_stats(df, title="Market Statistics")
    """
    st.markdown(f"### {title}")

    stats_df = df.describe(include="number" if numeric_only else None)

    # Round to 2 decimal places
    stats_df = stats_df.round(2)

    st.dataframe(
        stats_df,
        use_container_width=True,
    )


def comparison_table(
    data: dict[str, list],
    title: str = "Comparison",
) -> None:
    """
    Display a comparison table from structured data

    Args:
        data: Dict where key=column_name, value=list of values
        title: Table title

    Example:
        comparison_table({
            "Model": ["Random Forest", "XGBoost", "Linear Reg"],
            "R² Score": [0.92, 0.89, 0.78],
            "RMSE": [2.1, 2.5, 3.2],
            "Time (ms)": [145, 230, 50]
        })
    """
    st.markdown(f"### {title}")

    df = pd.DataFrame(data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


def key_value_table(
    data: dict[str, any],
    title: Optional[str] = None,
    format_values: Optional[Callable] = None,
) -> None:
    """
    Display key-value pairs in a styled table

    Args:
        data: Dict of key -> value
        title: Optional table title
        format_values: Optional function to format values

    Example:
        key_value_table({
            "Total Return": "15.3%",
            "Annual Return": "12.1%",
            "Volatility": "18.5%",
            "Sharpe Ratio": "0.67"
        }, title="Portfolio Metrics")
    """
    if title:
        st.markdown(f"### {title}")

    df = pd.DataFrame(
        list(data.items()),
        columns=["Metric", "Value"]
    )

    if format_values:
        df["Value"] = df["Value"].apply(format_values)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )
