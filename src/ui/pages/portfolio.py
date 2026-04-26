"""
Page Portefeuille - Gestion et analyse de portefeuille

Analyse de performance, répartition d'actifs, et optimisation.
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
    """Affiche la page de portefeuille."""
    
    # Header
    header("Portefeuille", 
           "Gestion, analyse et optimisation de portefeuille",
           "💼")
    
    # ====================================================================
    # SIDEBAR - COMPOSITION
    # ====================================================================
    
    st.sidebar.markdown("### 💼 Composition du portefeuille")
    st.sidebar.divider()
    
    # Composition d'exemple
    holdings = {
        "BNP.PA": 10,
        "RNO.PA": 5,
        "BTC-USD": 0.5,
        "ETH-USD": 2.0
    }
    
    prices = {
        "BNP.PA": 52.5,
        "RNO.PA": 32.1,
        "BTC-USD": 50000,
        "ETH-USD": 3000
    }
    
    # Afficher la composition
    total_value = 0
    for symbol, quantity in holdings.items():
        value = quantity * prices[symbol]
        total_value += value
        st.sidebar.metric(f"{symbol}", f"{quantity} × ${prices[symbol]:,.0f}")
    
    st.sidebar.divider()
    st.sidebar.info(f"**Valeur totale**: ${total_value:,.0f}")
    
    # ====================================================================
    # MAIN CONTENT
    # ====================================================================
    
    # KPIs principaux
    st.subheader("📊 Indicateurs clés")
    
    kpi_data = {
        'Valeur totale': f"${total_value:,.0f}",
        'Gain/Perte': f"${total_value * 0.15:,.0f} (+15.2%)",
        'Rendement annualisé': "12.5%",
        'Volatilité': "14.8%"
    }
    
    kpi_section(kpi_data)
    
    st.divider()
    
    # ====================================================================
    # PORTFOLIO ALLOCATION
    # ====================================================================
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Répartition d'actifs")
        
        # Données de répartition
        allocation = {
            'Actions CAC40': total_value * 0.45,
            'Crypto': total_value * 0.25,
            'Cash': total_value * 0.30
        }
        
        allocation_df = pd.DataFrame({
            'Classe': list(allocation.keys()),
            'Valeur': list(allocation.values())
        })
        
        # Pie chart simulation
        col_allocation_pct = allocation_df.copy()
        col_allocation_pct['Pourcentage'] = (col_allocation_pct['Valeur'] / col_allocation_pct['Valeur'].sum() * 100).round(1)
        
        st.markdown("""
        | Classe | Valeur | % |
        |--------|--------|-----|
        | Actions CAC40 | $4,500 | 45% |
        | Crypto | $2,500 | 25% |
        | Cash | $3,000 | 30% |
        """)
    
    with col2:
        st.subheader("📊 Performance par actif")
        
        holdings_perf = pd.DataFrame({
            'Symbole': list(holdings.keys()),
            'Quantité': list(holdings.values()),
            'Prix': [prices[s] for s in holdings.keys()],
            'Valeur': [holdings[s] * prices[s] for s in holdings.keys()],
            'Changement': [1.2, 0.8, 5.3, 2.1]  # %
        })
        
        data_table(holdings_perf, height=200)
    
    st.divider()
    
    # ====================================================================
    # PERFORMANCE OVER TIME
    # ====================================================================
    
    st.subheader("📈 Évolution du portefeuille")
    
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=252, freq='D')
    portfolio_values = total_value + np.cumsum(np.random.randn(252) * 50)
    
    perf_df = pd.DataFrame({
        'Date': dates,
        'Valeur': portfolio_values
    }).set_index('Date')
    
    line_chart(
        perf_df,
        x='Date',
        y='Valeur',
        title="Valeur du portefeuille (252 jours)",
        height=400
    )
    
    st.divider()
    
    # ====================================================================
    # STATISTICS
    # ====================================================================
    
    st.subheader("📊 Statistiques de performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    returns = perf_df['Valeur'].pct_change().dropna()
    total_return = ((perf_df['Valeur'].iloc[-1] / perf_df['Valeur'].iloc[0]) - 1) * 100
    annual_return = (1 + returns.mean()) ** 252 - 1
    volatility = returns.std() * np.sqrt(252)
    sharpe = (annual_return / volatility) if volatility > 0 else 0
    max_drawdown = (perf_df['Valeur'] / perf_df['Valeur'].cummax() - 1).min() * 100
    
    with col1:
        st.metric("Rendement total", f"{total_return:+.2f}%")
    with col2:
        st.metric("Rendement annualisé", f"{annual_return:.2%}")
    with col3:
        st.metric("Volatilité", f"{volatility:.2%}")
    with col4:
        st.metric("Ratio Sharpe", f"{sharpe:.2f}")
    
    col5, col6 = st.columns(2)
    with col5:
        st.metric("Max Drawdown", f"{max_drawdown:.2f}%")
    with col6:
        st.metric("Valeur actuelle", f"${perf_df['Valeur'].iloc[-1]:,.0f}")
    
    st.divider()
    
    # ====================================================================
    # OPTIMIZATION
    # ====================================================================
    
    st.subheader("⚙️ Optimisation du portefeuille")
    
    with st.expander("Voir les recommandations", expanded=False):
        alert_success("Votre portefeuille est **bien diversifié**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### ✓ Points positifs
            
            - Bonne diversification CAC40/Crypto/Cash
            - Ratio risque/rendement acceptable
            - Volatilité contrôlée
            """)
        
        with col2:
            st.markdown("""
            ### 💡 Recommandations
            
            - Augmenter position LSTM forecast (crypto)
            - Rééquilibrer trimestriellement
            - Utiliser Ensemble model pour décisions
            """)
    
    st.divider()
    
    # ====================================================================
    # REBALANCING
    # ====================================================================
    
    st.subheader("🔄 Rééquilibrage")
    
    with st.expander("Stratégie de rééquilibrage", expanded=False):
        alert_info("""
        **Fréquence**: Trimestrielle ou quand déviation > 5%
        
        **Méthode**: Utiliser les modèles ML pour timing
        - **Prophet**: Pour actions CAC40
        - **LSTM**: Pour cryptomonnaies
        - **Ensemble**: Pour décisions critiques
        """)
        
        st.markdown("""
        ### Exemple de rééquilibrage
        
        | Classe | Actual | Target | Action |
        |--------|--------|--------|--------|
        | Actions | 48% | 45% | Vendre 3% |
        | Crypto | 22% | 25% | Acheter 3% |
        | Cash | 30% | 30% | Neutre |
        """)
    
    st.divider()
    
    # ====================================================================
    # BACKTEST RESULTS
    # ====================================================================
    
    st.subheader("📊 Résultats backtest")
    
    backtest_data = {
        'Stratégie': ['Buy & Hold', 'Rebalance 3M', 'ML-Driven'],
        'Rendement': [12.5, 14.2, 16.8],
        'Volatilité': [14.8, 13.2, 12.1],
        'Ratio Sharpe': [0.84, 1.07, 1.38]
    }
    
    backtest_df = pd.DataFrame(backtest_data)
    data_table(backtest_df, title="", height=200)
    
    alert_success("**Stratégie ML-Driven recommandée** pour meilleur rendement ajusté au risque")
