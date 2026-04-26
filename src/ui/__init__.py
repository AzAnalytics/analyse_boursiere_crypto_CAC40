"""
UI Layer - Streamlit Application

Moderne minimalist design avec composants réutilisables.
- main.py: Application principale avec navigation
- components.py: Bibliothèque de composants (20+)
- pages/: Pages individuelles (bourses, crypto, portfolio, ml_forecast)
"""

from .components import (
    apply_modern_theme,
    header,
    tabs_section,
    metric_card,
    metrics_row,
    line_chart,
    bar_chart,
    candlestick_chart,
    data_table,
    alert_success,
    alert_warning,
    alert_error,
    alert_info,
    kpi_section,
    performance_summary,
    symbol_selector,
    date_range_filter,
)

__all__ = [
    'apply_modern_theme',
    'header',
    'tabs_section',
    'metric_card',
    'metrics_row',
    'line_chart',
    'bar_chart',
    'candlestick_chart',
    'data_table',
    'alert_success',
    'alert_warning',
    'alert_error',
    'alert_info',
    'kpi_section',
    'performance_summary',
    'symbol_selector',
    'date_range_filter',
]
