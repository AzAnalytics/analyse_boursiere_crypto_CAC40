"""
Styles & Theme Configuration - Modern Minimalist Design

Centralized styling for consistent, professional look across all pages
"""
import streamlit as st

# Color Palette - Modern Minimalist
COLORS = {
    "primary": "#1f77b4",      # Professional blue
    "secondary": "#ff7f0e",    # Accent orange
    "success": "#2ca02c",      # Success green
    "warning": "#d62728",      # Warning red
    "info": "#17becf",         # Info cyan

    "bg_primary": "#ffffff",   # White background
    "bg_secondary": "#f8f9fa", # Light gray background
    "bg_tertiary": "#f0f2f6",  # Streamlit gray

    "text_primary": "#262730", # Dark text
    "text_secondary": "#808080", # Medium gray text
    "text_light": "#b0b0b0",   # Light gray text

    "border": "#e0e0e0",       # Light border
    "shadow": "rgba(0, 0, 0, 0.1)",
}

# Typography
FONTS = {
    "title": "Segoe UI, sans-serif",
    "body": "Segoe UI, sans-serif",
    "mono": "Fira Code, monospace",
}

# Spacing System
SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "2xl": "48px",
}

# Border Radius
BORDER_RADIUS = {
    "sm": "4px",
    "md": "8px",
    "lg": "12px",
    "xl": "16px",
}


def inject_custom_css():
    """Inject custom CSS for modern, minimalist design"""

    css = f"""
    <style>

    /* ===== ROOT VARIABLES ===== */
    :root {{
        --primary: {COLORS['primary']};
        --secondary: {COLORS['secondary']};
        --success: {COLORS['success']};
        --warning: {COLORS['warning']};
        --info: {COLORS['info']};

        --bg-primary: {COLORS['bg_primary']};
        --bg-secondary: {COLORS['bg_secondary']};
        --bg-tertiary: {COLORS['bg_tertiary']};

        --text-primary: {COLORS['text_primary']};
        --text-secondary: {COLORS['text_secondary']};
        --text-light: {COLORS['text_light']};

        --border: {COLORS['border']};
        --shadow: {COLORS['shadow']};
    }}

    /* ===== GLOBAL STYLES ===== */
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}

    body {{
        font-family: {FONTS['body']};
        color: var(--text-primary);
        background-color: var(--bg-primary);
        line-height: 1.6;
    }}

    /* ===== TYPOGRAPHY ===== */
    h1, h2, h3, h4, h5, h6 {{
        font-weight: 600;
        letter-spacing: -0.5px;
        margin-bottom: {SPACING['md']};
    }}

    h1 {{
        font-size: 2.5rem;
        color: var(--text-primary);
    }}

    h2 {{
        font-size: 2rem;
        color: var(--text-primary);
        border-bottom: 2px solid var(--primary);
        padding-bottom: {SPACING['sm']};
    }}

    h3 {{
        font-size: 1.5rem;
        color: var(--text-primary);
    }}

    p {{
        font-size: 1rem;
        color: var(--text-secondary);
        margin-bottom: {SPACING['md']};
    }}

    /* ===== MAIN CONTAINER ===== */
    .main {{
        padding: {SPACING['xl']};
        max-width: 1400px;
        margin: 0 auto;
    }}

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {{
        background-color: var(--bg-secondary);
        border-right: 1px solid var(--border);
    }}

    [data-testid="stSidebar"] > div:first-child {{
        padding: {SPACING['lg']};
    }}

    /* ===== CARDS ===== */
    .metric-card {{
        background-color: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: {BORDER_RADIUS['lg']};
        padding: {SPACING['lg']};
        margin-bottom: {SPACING['md']};
        box-shadow: 0 2px 8px var(--shadow);
        transition: all 0.3s ease;
    }}

    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px var(--shadow);
    }}

    .metric-card-title {{
        font-size: 0.875rem;
        color: var(--text-secondary);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: {SPACING['sm']};
    }}

    .metric-card-value {{
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
        font-family: {FONTS['mono']};
    }}

    .metric-card-delta {{
        font-size: 0.875rem;
        margin-top: {SPACING['sm']};
    }}

    .metric-card-delta.positive {{
        color: var(--success);
    }}

    .metric-card-delta.negative {{
        color: var(--warning);
    }}

    /* ===== BUTTONS ===== */
    button {{
        background-color: var(--primary);
        color: white;
        border: none;
        border-radius: {BORDER_RADIUS['md']};
        padding: {SPACING['sm']} {SPACING['md']};
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
    }}

    button:hover {{
        opacity: 0.9;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px var(--shadow);
    }}

    button:active {{
        transform: translateY(0);
    }}

    /* ===== TABS ===== */
    [data-testid="stTabs"] {{
        background-color: transparent;
    }}

    [role="tab"] {{
        border-bottom: 2px solid transparent;
        color: var(--text-secondary);
        font-weight: 500;
        transition: all 0.3s ease;
    }}

    [role="tab"]:hover {{
        color: var(--primary);
        border-bottom-color: var(--primary);
    }}

    [role="tab"][aria-selected="true"] {{
        color: var(--primary);
        border-bottom-color: var(--primary);
    }}

    /* ===== INPUTS ===== */
    input, select, textarea {{
        border: 1px solid var(--border);
        border-radius: {BORDER_RADIUS['md']};
        padding: {SPACING['sm']} {SPACING['md']};
        font-family: {FONTS['body']};
        transition: all 0.2s ease;
    }}

    input:focus, select:focus, textarea:focus {{
        outline: none;
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.1);
    }}

    /* ===== SELECT/MULTISELECT ===== */
    [data-testid="stMultiSelect"] {{
        background-color: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: {BORDER_RADIUS['md']};
    }}

    /* ===== SLIDERS ===== */
    [data-testid="stSlider"] {{
        padding: {SPACING['md']} 0;
    }}

    /* ===== ALERTS/CALLOUTS ===== */
    [data-testid="stAlert"] {{
        border-radius: {BORDER_RADIUS['lg']};
        border-left: 4px solid var(--primary);
        padding: {SPACING['md']};
    }}

    /* Success Alert */
    [data-testid="stAlert"]:has(svg[viewBox="0 0 18 18"]) {{
        border-left-color: var(--success);
        background-color: rgba(44, 160, 44, 0.1);
    }}

    /* Warning Alert */
    [data-testid="stAlert"]:has(svg[viewBox="0 0 24 24"]) {{
        border-left-color: var(--warning);
        background-color: rgba(214, 39, 40, 0.1);
    }}

    /* Info Alert */
    [data-testid="stAlert"]:has(svg[viewBox="0 0 24 24"]) {{
        border-left-color: var(--info);
        background-color: rgba(23, 190, 207, 0.1);
    }}

    /* ===== DATAFRAME ===== */
    [data-testid="stDataFrame"] {{
        border: 1px solid var(--border);
        border-radius: {BORDER_RADIUS['lg']};
        overflow: hidden;
    }}

    [data-testid="stDataFrame"] table {{
        font-size: 0.875rem;
    }}

    [data-testid="stDataFrame"] th {{
        background-color: var(--bg-secondary);
        color: var(--text-primary);
        font-weight: 600;
        border-bottom: 2px solid var(--border);
    }}

    [data-testid="stDataFrame"] td {{
        border-bottom: 1px solid var(--border);
        padding: {SPACING['sm']};
    }}

    /* ===== CHARTS ===== */
    [data-testid="stPlotlyChart"] {{
        border: 1px solid var(--border);
        border-radius: {BORDER_RADIUS['lg']};
        padding: {SPACING['md']};
        background-color: var(--bg-secondary);
    }}

    /* ===== COLUMNS LAYOUT ===== */
    [data-testid="column"] {{
        padding: 0 {SPACING['sm']};
    }}

    /* ===== EXPANDER ===== */
    [data-testid="stExpander"] {{
        border: 1px solid var(--border);
        border-radius: {BORDER_RADIUS['md']};
        padding: {SPACING['md']};
    }}

    /* ===== SPINNERS & LOADING ===== */
    [data-testid="stSpinner"] {{
        color: var(--primary) !important;
    }}

    /* ===== METRICS ===== */
    [data-testid="metric-container"] {{
        background-color: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: {BORDER_RADIUS['lg']};
        padding: {SPACING['lg']};
        text-align: center;
    }}

    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {{
        h1 {{
            font-size: 1.75rem;
        }}

        h2 {{
            font-size: 1.5rem;
        }}

        .main {{
            padding: {SPACING['lg']};
        }}
    }}

    /* ===== ANIMATIONS ===== */
    @keyframes fadeIn {{
        from {{
            opacity: 0;
            transform: translateY(10px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    @keyframes slideDown {{
        from {{
            opacity: 0;
            transform: translateY(-10px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    [data-testid="stMetric"] {{
        animation: fadeIn 0.5s ease;
    }}

    /* ===== UTILITY CLASSES ===== */
    .text-center {{
        text-align: center;
    }}

    .text-right {{
        text-align: right;
    }}

    .mt-1 {{ margin-top: {SPACING['sm']}; }}
    .mt-2 {{ margin-top: {SPACING['md']}; }}
    .mt-3 {{ margin-top: {SPACING['lg']}; }}

    .mb-1 {{ margin-bottom: {SPACING['sm']}; }}
    .mb-2 {{ margin-bottom: {SPACING['md']}; }}
    .mb-3 {{ margin-bottom: {SPACING['lg']}; }}

    .p-1 {{ padding: {SPACING['sm']}; }}
    .p-2 {{ padding: {SPACING['md']}; }}
    .p-3 {{ padding: {SPACING['lg']}; }}

    </style>
    """

    st.markdown(css, unsafe_allow_html=True)


def get_metric_card_html(title: str, value: str, delta: str = None, delta_color: str = "positive") -> str:
    """
    Generate HTML for a metric card

    Args:
        title: Card title
        value: Main value to display
        delta: Optional delta/change indicator
        delta_color: "positive" (green) or "negative" (red)

    Returns:
        HTML string for metric card
    """
    delta_html = ""
    if delta:
        delta_class = f"metric-card-delta {delta_color}"
        delta_html = f'<div class="{delta_class}">{delta}</div>'

    html = f"""
    <div class="metric-card">
        <div class="metric-card-title">{title}</div>
        <div class="metric-card-value">{value}</div>
        {delta_html}
    </div>
    """
    return html
