"""
Page Cryptomonnaies - Analyse des principales cryptomonnaies

Utilise les composants réutilisables pour une UI cohérente et moderne.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.components import (
    page_layout, header, metrics_row, line_chart, bar_chart, data_table,
    alert_info, alert_success, alert_warning, kpi_section
)

def show():
    """Affiche la page des cryptomonnaies."""
    
    # Header
    header("Cryptomonnaies", 
           "Analyse des principales cryptomonnaies avec forecasting avancé",
           "🪙")
    
    # ====================================================================
    # SIDEBAR FILTERS
    # ====================================================================
    
    st.sidebar.markdown("### 🔍 Filtres Crypto")
    st.sidebar.divider()
    
    # Sélection des cryptos
    crypto_symbols = {
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD",
        "Cardano": "ADA-USD",
        "Solana": "SOL-USD",
        "Ripple": "XRP-USD"
    }
    
    selected_crypto = st.sidebar.selectbox(
        "Cryptomonnaie",
        options=list(crypto_symbols.keys()),
        index=0
    )
    
    # Période
    period = st.sidebar.radio(
        "Période",
        options=["1W", "1M", "3M", "1Y"],
        index=2,
        horizontal=True
    )
    
    # ====================================================================
    # MAIN CONTENT
    # ====================================================================
    
    # Données simulées pour démo
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=252, freq='D')
    close_price = 50000 + np.cumsum(np.random.randn(252) * 100)
    high_price = close_price + np.abs(np.random.randn(252) * 500)
    low_price = close_price - np.abs(np.random.randn(252) * 500)
    
    df = pd.DataFrame({
        'Date': dates,
        'Open': close_price + np.random.randn(252) * 50,
        'High': high_price,
        'Low': low_price,
        'Close': close_price,
        'Volume': np.random.randint(100000000, 500000000, 252)
    })
    
    # Métriques
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-30]
    change_pct = ((current_price - prev_price) / prev_price) * 100
    
    st.subheader(f"{selected_crypto} ({crypto_symbols[selected_crypto]})")
    
    metrics_row([
        ("Prix actuel", f"${current_price:,.0f}", "", None, "neutral"),
        ("Changement 30J", f"${current_price - prev_price:,.0f}", f"({change_pct:+.2f}%)", 
         change_pct, "positive" if change_pct >= 0 else "negative"),
        ("Plus haut (YTD)", f"${df['High'].max():,.0f}", "", None, "neutral"),
        ("Plus bas (YTD)", f"${df['Low'].min():,.0f}", "", None, "neutral"),
    ])
    
    st.divider()
    
    # ====================================================================
    # ALERTS
    # ====================================================================
    
    volatility = df['Close'].pct_change().std() * 100
    
    if volatility > 5:
        alert_warning(f"⚠️ Volatilité élevée détectée ({volatility:.1f}%)")
    else:
        alert_success(f"✓ Volatilité normale ({volatility:.1f}%)")
    
    st.divider()
    
    # ====================================================================
    # CHARTS
    # ====================================================================
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique de prix
        line_chart(
            df.set_index('Date'),
            x='Date',
            y='Close',
            title="Évolution du prix",
            height=400
        )
    
    with col2:
        # Volume
        bar_chart(
            df.set_index('Date'),
            x='Date',
            y='Volume',
            title="Volume d'échange",
            height=400
        )
    
    st.divider()
    
    # ====================================================================
    # STATISTICS
    # ====================================================================
    
    st.subheader("📊 Statistiques")
    
    stats_col1, stats_col2, stats_col3 = st.columns(3)
    
    returns = df['Close'].pct_change().dropna()
    annual_return = (1 + returns.mean()) ** 365 - 1
    volatility_annual = returns.std() * np.sqrt(365)
    sharpe = (annual_return / volatility_annual) if volatility_annual > 0 else 0
    
    with stats_col1:
        st.metric("Rendement annualisé", f"{annual_return:.2%}")
        st.metric("Volatilité (annualisée)", f"{volatility_annual:.2%}")
    
    with stats_col2:
        st.metric("Ratio Sharpe", f"{sharpe:.2f}")
        st.metric("Prix moyen", f"${df['Close'].mean():,.0f}")
    
    with stats_col3:
        st.metric("Rendement total", f"{((current_price/df['Close'].iloc[0])-1)*100:.2f}%")
        st.metric("Volume moyen", f"${df['Volume'].mean()/1e9:.1f}B")
    
    st.divider()
    
    # ====================================================================
    # MARKET OVERVIEW
    # ====================================================================
    
    st.subheader("🌍 Vue du marché crypto")
    
    # Simulation data pour plusieurs cryptos
    market_data = {
        'Crypto': ['Bitcoin', 'Ethereum', 'Cardano', 'Solana', 'Ripple'],
        'Prix': [50000, 3000, 0.65, 150, 2.5],
        'Changement 24H': [2.5, 1.8, -0.5, 3.2, -1.2],
        'Market Cap': ['$1.0T', '$360B', '$23B', '$53B', '$120B']
    }
    
    market_df = pd.DataFrame(market_data)
    data_table(market_df, title="", height=250)
    
    st.divider()
    
    # ====================================================================
    # ML FORECAST
    # ====================================================================
    
    st.subheader("🤖 Prédictions ML")
    
    with st.expander("Voir les prédictions (30 jours)", expanded=False):
        alert_info("**LSTM est recommandé pour les cryptomonnaies** car il capture les patterns non-linéaires et la volatilité")
        
        # Simulation de prédictions
        future_dates = pd.date_range(start=df['Date'].iloc[-1], periods=30, freq='D')
        
        # Plus de volatilité pour crypto
        prophet_forecast = current_price + np.cumsum(np.random.randn(30) * 200)
        lstm_forecast = current_price + np.cumsum(np.random.randn(30) * 300)  # Plus volatilité
        arima_forecast = current_price + np.cumsum(np.random.randn(30) * 150)
        ensemble_forecast = (prophet_forecast * 0.35 + lstm_forecast * 0.50 + arima_forecast * 0.15)
        
        forecast_df = pd.DataFrame({
            'Date': future_dates,
            'LSTM': lstm_forecast,
            'Ensemble': ensemble_forecast
        }).set_index('Date')
        
        line_chart(
            forecast_df,
            x='Date',
            y='LSTM',
            title="Prédictions LSTM (recommandé pour crypto)",
            height=350
        )
        
        alert_success("Le modèle LSTM capture mieux la volatilité des cryptomonnaies")
    
    st.divider()
    
    # ====================================================================
    # RECOMMENDATION BOX
    # ====================================================================
    
    col1, col2 = st.columns(2)
    
    with col1:
        alert_info("""
        **💡 Recommandation**: Utilisez **LSTM** pour les cryptomonnaies.
        
        ✓ Capture les patterns non-linéaires
        ✓ Gère la haute volatilité
        ✓ Excellent pour court terme
        ⚠️ Nécessite GPU pour performance
        """)
    
    with col2:
        alert_warning("""
        **⚠️ Attention**: Les cryptos sont très volatiles
        
        - Risque élevé/rendement potentiel élevé
        - Utilisez un modèle avec confiance intervals
        - Diversifiez votre portefeuille
        - Gestion du risque cruciale
        """)
