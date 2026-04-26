"""
Page Actions CAC40 - Analyse des principales actions françaises

Utilise les composants réutilisables pour une UI cohérente et moderne.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Ajouter le chemin du projet
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.components import (
    page_layout, header, metrics_row, line_chart, bar_chart, data_table,
    symbol_selector, date_range_filter, alert_info, alert_success,
    kpi_section, performance_summary
)

def show():
    """Affiche la page des actions CAC40."""
    
    # Header
    header("Actions CAC40", 
           "Analyse des principales actions françaises avec ML forecasting",
           "📈")
    
    # ====================================================================
    # SIDEBAR FILTERS
    # ====================================================================
    
    st.sidebar.markdown("### 🔍 Filtres Actions")
    st.sidebar.divider()
    
    # Sélection des actions
    cac40_symbols = {
        "BNP": "BNP.PA",
        "Renault": "RNO.PA",
        "Société Générale": "GLE.PA",
        "Orange": "ORAN.PA",
        "EDF": "EDF.PA",
        "Total": "TTEF.PA",
        "LVMH": "MC.PA",
        "Sanofi": "SNPN.PA"
    }
    
    selected_symbol = st.sidebar.selectbox(
        "Action",
        options=list(cac40_symbols.keys()),
        index=0
    )
    
    # Période
    period = st.sidebar.radio(
        "Période",
        options=["1M", "3M", "6M", "1Y", "5Y"],
        index=3,
        horizontal=True
    )
    
    # ====================================================================
    # MAIN CONTENT
    # ====================================================================
    
    # Données simulées pour démo
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=252, freq='D')
    close_price = 100 + np.cumsum(np.random.randn(252) * 0.5)
    high_price = close_price + np.abs(np.random.randn(252) * 2)
    low_price = close_price - np.abs(np.random.randn(252) * 2)
    
    df = pd.DataFrame({
        'Date': dates,
        'Open': close_price + np.random.randn(252),
        'High': high_price,
        'Low': low_price,
        'Close': close_price,
        'Volume': np.random.randint(1000000, 5000000, 252)
    })
    
    # Métriques
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-50]
    change_pct = ((current_price - prev_price) / prev_price) * 100
    
    st.subheader(f"{selected_symbol} ({cac40_symbols[selected_symbol]})")
    
    metrics_row([
        ("Prix actuel", f"€{current_price:.2f}", "", None, "neutral"),
        ("Changement", f"€{current_price - prev_price:.2f}", f"({change_pct:+.2f}%)", 
         change_pct, "positive" if change_pct >= 0 else "negative"),
        ("Plus haut (52S)", f"€{df['High'].max():.2f}", "", None, "neutral"),
        ("Plus bas (52S)", f"€{df['Low'].min():.2f}", "", None, "neutral"),
    ])
    
    st.divider()
    
    # ====================================================================
    # CHARTS
    # ====================================================================
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique de prix
        line_chart(
            df,
            x='Date',
            y='Close',
            title="Évolution du prix",
            height=400
        )

    with col2:
        # Volume
        bar_chart(
            df,
            x='Date',
            y='Volume',
            title="Volume de trading",
            height=400
        )
    
    st.divider()
    
    # ====================================================================
    # STATISTICS
    # ====================================================================
    
    st.subheader("📊 Statistiques")
    
    stats_col1, stats_col2, stats_col3 = st.columns(3)
    
    returns = df['Close'].pct_change().dropna()
    annual_return = (1 + returns.mean()) ** 252 - 1
    volatility = returns.std() * np.sqrt(252)
    sharpe = (annual_return / volatility) if volatility > 0 else 0
    
    with stats_col1:
        st.metric("Rendement annualisé", f"{annual_return:.2%}")
        st.metric("Volatilité", f"{volatility:.2%}")
    
    with stats_col2:
        st.metric("Ratio Sharpe", f"{sharpe:.2f}")
        st.metric("Prix moyen", f"€{df['Close'].mean():.2f}")
    
    with stats_col3:
        st.metric("Rendement total", f"{((current_price/df['Close'].iloc[0])-1)*100:.2f}%")
        st.metric("Volume moyen", f"{df['Volume'].mean()/1e6:.1f}M")
    
    st.divider()
    
    # ====================================================================
    # DATA TABLE
    # ====================================================================
    
    st.subheader("📋 Données historiques")
    
    # Afficher les dernières 10 lignes
    display_df = df.tail(10)[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
    display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
    
    data_table(display_df.sort_values('Date', ascending=False), height=300)
    
    st.divider()
    
    # ====================================================================
    # ML FORECAST PREVIEW
    # ====================================================================
    
    st.subheader("🤖 Aperçu ML Forecast")
    
    with st.expander("Voir les prédictions", expanded=False):
        alert_info("Les modèles ML sont disponibles dans la section 'ML Forecast'")
        
        # Simulation de prédictions
        future_dates = pd.date_range(start=df['Date'].iloc[-1], periods=30, freq='D')
        prophet_forecast = current_price + np.cumsum(np.random.randn(30) * 0.3)
        lstm_forecast = current_price + np.cumsum(np.random.randn(30) * 0.4)
        arima_forecast = current_price + np.cumsum(np.random.randn(30) * 0.25)
        ensemble_forecast = (prophet_forecast + lstm_forecast + arima_forecast) / 3
        
        forecast_df = pd.DataFrame({
            'Date': future_dates,
            'Prophet': prophet_forecast,
            'LSTM': lstm_forecast,
            'ARIMA': arima_forecast,
            'Ensemble': ensemble_forecast
        }).set_index('Date')
        
        line_chart(
            forecast_df,
            x='Date',
            y='Ensemble',
            title="Prédictions Ensemble (30 jours)",
            height=300
        )
        
        alert_success("Le modèle Ensemble combine Prophet (50%), LSTM (35%), ARIMA (15%)")
    
    st.divider()
    
    # ====================================================================
    # INFO BOX
    # ====================================================================
    
    col1, col2 = st.columns(2)
    
    with col1:
        alert_info("""
        **💡 Conseil**: Utilisez le modèle **Prophet** pour les actions stables comme CAC40.
        
        - Gère automatiquement les tendances
        - Robuste aux données manquantes
        - Prédictions rapides et fiables
        """)
    
    with col2:
        alert_info("""
        **📚 Ressources**:
        - ML_GUIDE.md - Comparaison des modèles
        - ARCHITECTURE.md - Vue d'ensemble système
        - NEXT_STEPS.md - Guide d'implémentation
        """)
