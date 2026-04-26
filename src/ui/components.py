"""
Streamlit Components Library - Modern Minimalist Design

Composants réutilisables pour l'app avec design cohérent, spacing propre, et animations fluides.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional, Callable, Any

# ============================================================================
# STYLING & THEME
# ============================================================================

def apply_modern_theme():
    """Configure le thème moderne minimalist."""
    st.set_page_config(
        page_title="Finance Dashboard",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS personnalisé pour style moderne
    st.markdown("""
    <style>
    :root {
        --primary: #1f77b4;      /* Bleu professionnel */
        --secondary: #ff7f0e;    /* Orange accent */
        --success: #2ca02c;      /* Vert */
        --danger: #d62728;       /* Rouge */
        --info: #17becf;         /* Cyan */
        --light: #f8f9fa;        /* Gris très clair */
        --dark: #2c3e50;         /* Bleu-gris foncé */
    }
    
    /* Spacing & Layout */
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 16px rgba(31, 119, 180, 0.15);
        transform: translateY(-2px);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--dark);
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--primary);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: #1560a0;
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.3);
    }
    
    /* Cards */
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid var(--primary);
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# HEADER & NAVIGATION
# ============================================================================

def header(title: str, description: str = "", icon: str = ""):
    """Header principal avec titre et description."""
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"# {icon} {title}" if icon else f"# {title}")
    if description:
        st.markdown(f"<p style='color: #666; font-size: 0.95rem; margin-top: -0.5rem;'>{description}</p>", 
                   unsafe_allow_html=True)
    st.divider()


def tabs_section(tab_names: list, default: int = 0):
    """Crée des onglets modernes."""
    return st.tabs(tab_names)


# ============================================================================
# METRIC CARDS
# ============================================================================

def metric_card(label: str, value: Any, unit: str = "", 
                change: Optional[float] = None, change_type: str = "neutral"):
    """Carte métrique moderne avec valeur et changement."""
    
    # Déterminer la couleur du changement
    change_color = "#2ca02c" if change_type == "positive" else "#d62728" if change_type == "negative" else "#666"
    change_arrow = "📈" if change_type == "positive" else "📉" if change_type == "negative" else ""
    
    html = f"""
    <div class="metric-card">
        <div style="color: #888; font-size: 0.9rem; font-weight: 500; margin-bottom: 0.5rem;">
            {label}
        </div>
        <div style="color: #2c3e50; font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">
            {value} <span style="font-size: 0.8rem; color: #999;">{unit}</span>
        </div>
    """
    
    if change is not None:
        html += f"""
        <div style="color: {change_color}; font-size: 0.85rem; font-weight: 600;">
            {change_arrow} {change:+.2f}%
        </div>
        """
    
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def metrics_row(metrics: list):
    """Affiche plusieurs métriques en ligne."""
    cols = st.columns(len(metrics))
    for col, (label, value, unit, change, change_type) in zip(cols, metrics):
        with col:
            metric_card(label, value, unit, change, change_type)


# ============================================================================
# DATA TABLES
# ============================================================================

def data_table(df: pd.DataFrame, title: str = "", height: int = 400):
    """Table de données stylisée avec scrolling."""
    if title:
        st.subheader(title)
    
    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        column_config={col: st.column_config.NumberColumn(format="%.2f") 
                      for col in df.select_dtypes(['float64', 'int64']).columns}
    )


# ============================================================================
# CHARTS
# ============================================================================

def line_chart(df: pd.DataFrame, x: str, y: str, title: str = "",
               height: int = 400, show_legend: bool = True):
    """Graphique linéaire moderne."""
    # Reset index if x is the index name
    if df.index.name == x:
        df = df.reset_index()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df[x],
        y=df[y],
        mode='lines',
        name=y,
        line=dict(color='#1f77b4', width=3),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.1)'
    ))
    
    fig.update_layout(
        title=title,
        height=height,
        hovermode='x unified',
        template='plotly_white',
        margin=dict(l=50, r=50, t=50, b=50),
        showlegend=show_legend
    )
    
    st.plotly_chart(fig, use_container_width=True)


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str = "",
              height: int = 400, orientation: str = 'v'):
    """Graphique en barres moderne."""
    # Reset index if x is the index name
    if df.index.name == x:
        df = df.reset_index()

    fig = go.Figure()

    if orientation == 'v':
        fig.add_trace(go.Bar(
            x=df[x],
            y=df[y],
            marker=dict(color='#1f77b4'),
            name=y
        ))
    else:
        fig.add_trace(go.Bar(
            y=df[x],
            x=df[y],
            orientation='h',
            marker=dict(color='#1f77b4'),
            name=y
        ))
    
    fig.update_layout(
        title=title,
        height=height,
        template='plotly_white',
        margin=dict(l=50, r=50, t=50, b=50),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def candlestick_chart(df: pd.DataFrame, title: str = "", height: int = 500):
    """Graphique candlestick (OHLC) pour stocks/crypto."""
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df.get('Open', df['o']),
        high=df.get('High', df['h']),
        low=df.get('Low', df['l']),
        close=df.get('Close', df['c'])
    )])
    
    fig.update_layout(
        title=title,
        height=height,
        template='plotly_white',
        xaxis_rangeslider_visible=False,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# ALERTS & MESSAGES
# ============================================================================

def alert_success(message: str, icon: str = "✓"):
    """Alerte succès moderne."""
    st.markdown(f"""
    <div style="background: #d4edda; border-left: 4px solid #28a745; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        <span style="color: #155724; font-weight: 600;">{icon} {message}</span>
    </div>
    """, unsafe_allow_html=True)


def alert_warning(message: str, icon: str = "⚠"):
    """Alerte warning moderne."""
    st.markdown(f"""
    <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        <span style="color: #856404; font-weight: 600;">{icon} {message}</span>
    </div>
    """, unsafe_allow_html=True)


def alert_error(message: str, icon: str = "✕"):
    """Alerte erreur moderne."""
    st.markdown(f"""
    <div style="background: #f8d7da; border-left: 4px solid #dc3545; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        <span style="color: #721c24; font-weight: 600;">{icon} {message}</span>
    </div>
    """, unsafe_allow_html=True)


def alert_info(message: str, icon: str = "ℹ"):
    """Alerte info moderne."""
    st.markdown(f"""
    <div style="background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        <span style="color: #0c5460; font-weight: 600;">{icon} {message}</span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# FILTERS & INPUTS
# ============================================================================

def filter_section(title: str = "Filtres"):
    """Section de filtres moderne."""
    with st.expander(f"🔍 {title}", expanded=False):
        return st.columns(3)


def date_range_filter():
    """Filtre de plage de dates."""
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Date début")
    with col2:
        end_date = st.date_input("Date fin")
    return start_date, end_date


def symbol_selector(symbols: list, default_idx: int = 0, 
                   multi: bool = False, key: str = None):
    """Sélecteur de symboles (actions/crypto)."""
    if multi:
        return st.multiselect("Symboles", options=symbols, key=key)
    else:
        return st.selectbox("Symbole", options=symbols, index=default_idx, key=key)


# ============================================================================
# STATS & KPIs
# ============================================================================

def kpi_section(kpis: dict):
    """Affiche les KPIs dans une section organisée."""
    st.subheader("📊 Indicateurs clés")
    
    cols = st.columns(len(kpis))
    for col, (label, value) in zip(cols, kpis.items()):
        with col:
            st.metric(label, f"{value:.2%}" if isinstance(value, float) else value)


def performance_summary(data: dict):
    """Résumé de performance avec plusieurs métriques."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Rendement total", data.get('total_return', 0), f"{data.get('return_pct', 0):.2%}")
    with col2:
        st.metric("Volatilité", data.get('volatility', 0), "annualisée")
    with col3:
        st.metric("Ratio Sharpe", data.get('sharpe_ratio', 0), "")
    with col4:
        st.metric("Max Drawdown", data.get('max_drawdown', 0), "")


# ============================================================================
# LOADING & PROGRESS
# ============================================================================

def loading_spinner(message: str = "Chargement..."):
    """Spinner de chargement."""
    with st.spinner(message):
        return None


def progress_bar(value: float, total: float = 100, label: str = ""):
    """Barre de progression."""
    st.progress(int((value / total) * 100))
    if label:
        st.caption(label)


# ============================================================================
# SIDEBAR HELPERS
# ============================================================================

def sidebar_header(title: str, icon: str = ""):
    """Header pour la sidebar."""
    st.sidebar.markdown(f"### {icon} {title}" if icon else f"### {title}")


def sidebar_divider():
    """Diviseur dans la sidebar."""
    st.sidebar.divider()


# ============================================================================
# MAIN PAGE LAYOUT
# ============================================================================

def page_layout(title: str, description: str = "", icon: str = ""):
    """Layout standard pour une page."""
    apply_modern_theme()
    header(title, description, icon)
    return st.container()
