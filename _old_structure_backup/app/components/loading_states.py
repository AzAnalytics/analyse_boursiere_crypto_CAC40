"""
LoadingStates Component - Loading animations, skeletons, and state messages

Reusable components for UX feedback during async operations
"""
import streamlit as st
from typing import Optional, List


def loading_spinner(
    message: str = "Loading data...",
    icon: str = "⏳",
) -> None:
    """
    Display a spinner with message during long operations

    Args:
        message: Message to display (default: "Loading data...")
        icon: Icon prefix (default: "⏳")

    Example:
        with st.spinner("Loading data..."):
            data = fetch_data()
    """
    with st.spinner(f"{icon} {message}"):
        pass


def loading_skeleton(
    num_lines: int = 5,
    title: Optional[str] = None,
) -> None:
    """
    Display a skeleton loader placeholder

    Args:
        num_lines: Number of skeleton lines to show (default: 5)
        title: Optional title before skeleton

    Example:
        loading_skeleton(num_lines=3, title="Loading chart...")
    """
    if title:
        st.markdown(f"### {title}")

    st.markdown(
        f"""
        <div style="animation: fadeIn 0.5s ease;">
            {''.join([f'<div style="height: 20px; background: var(--bg-secondary); border-radius: 4px; margin-bottom: 12px; animation: pulse 1.5s infinite;"></div>' for _ in range(num_lines)])}
        </div>
        """,
        unsafe_allow_html=True,
    )


def success_message(
    message: str,
    icon: str = "✅",
    duration: Optional[int] = 3,
) -> None:
    """
    Display a success message with animation

    Args:
        message: Success message text
        icon: Icon prefix (default: "✅")
        duration: Display duration in seconds (optional)

    Example:
        success_message("Data loaded successfully!")
    """
    st.success(f"{icon} {message}")


def error_message(
    message: str,
    icon: str = "❌",
    details: Optional[str] = None,
) -> None:
    """
    Display an error message with optional details

    Args:
        message: Error message text
        icon: Icon prefix (default: "❌")
        details: Optional error details/traceback

    Example:
        error_message("Failed to fetch data", details="Connection timeout")
    """
    st.error(f"{icon} {message}")
    if details:
        with st.expander("Error Details"):
            st.code(details)


def warning_message(
    message: str,
    icon: str = "⚠️",
) -> None:
    """
    Display a warning message

    Args:
        message: Warning message text
        icon: Icon prefix (default: "⚠️")

    Example:
        warning_message("Data may be incomplete")
    """
    st.warning(f"{icon} {message}")


def info_message(
    message: str,
    icon: str = "ℹ️",
) -> None:
    """
    Display an info message

    Args:
        message: Info message text
        icon: Icon prefix (default: "ℹ️")

    Example:
        info_message("Using cached data from 1 hour ago")
    """
    st.info(f"{icon} {message}")


def empty_state(
    title: str = "No data available",
    message: str = "Try adjusting your filters or parameters",
    icon: str = "🔍",
) -> None:
    """
    Display an empty state message when no data is available

    Args:
        title: Empty state title
        message: Description message
        icon: Icon to display (default: "🔍")

    Example:
        empty_state(
            title="No matching results",
            message="No stocks match your criteria"
        )
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 40px 20px;">
                <div style="font-size: 3rem; margin-bottom: 20px;">{icon}</div>
                <h3 style="margin: 10px 0; color: var(--text-primary);">{title}</h3>
                <p style="color: var(--text-secondary); margin: 10px 0;">{message}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def progress_indicator(
    current: int,
    total: int,
    label: str = "Progress",
    show_percentage: bool = True,
) -> None:
    """
    Display a progress indicator with percentage

    Args:
        current: Current progress value
        total: Total value
        label: Progress label (default: "Progress")
        show_percentage: Show percentage text (default: True)

    Example:
        progress_indicator(current=3, total=10, label="Processing")
    """
    percentage = current / total if total > 0 else 0
    st.progress(percentage)

    if show_percentage:
        st.caption(f"{label}: {current}/{total} ({percentage*100:.0f}%)")


def status_badge(
    status: str,
    status_type: str = "info",  # "info", "success", "warning", "error"
) -> None:
    """
    Display a colored status badge

    Args:
        status: Status text
        status_type: Type of status (default: "info")
            - "info" (blue)
            - "success" (green)
            - "warning" (orange)
            - "error" (red)

    Example:
        status_badge("Active", status_type="success")
    """
    color_map = {
        "info": "#17becf",
        "success": "#2ca02c",
        "warning": "#ff7f0e",
        "error": "#d62728",
    }

    color = color_map.get(status_type, "#17becf")

    st.markdown(
        f"""
        <span style="
            background-color: {color};
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.875rem;
            font-weight: 500;
        ">{status}</span>
        """,
        unsafe_allow_html=True,
    )
