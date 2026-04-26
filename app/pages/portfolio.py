"""
Page Streamlit : Analyse de Portefeuille

Refactorisée avec composants réutilisables et CSS moderne minimalist
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from config.constants import CAC40_STOCKS, CRYPTOCURRENCIES
from core.data_transformer import DataTransformer
from core.portfolio_engine import PortfolioEngine
from data_layer.repository import get_stocks_repository, get_crypto_repository
from utils.logger import setup_logger
from app.styles import inject_custom_css
from app.components import (
    metric_card_grid,
    chart_card,
    key_value_table,
    data_table,
    empty_state,
    error_message,
)

logger = setup_logger(__name__)

st.set_page_config(page_title="Portfolio", page_icon="💼", layout="wide")
inject_custom_css()

st.title("💼 Analyse de Portefeuille")

# Sidebar : Configuration du portefeuille
st.sidebar.header("Configuration du portefeuille")

# Sélectionner les actifs
portfolio_type = st.sidebar.radio(
    "Type de portefeuille",
    options=["Actions", "Crypto", "Mixte"],
    help="Sélectionner le type d'actifs",
)

# Récupérer les données appropriées
@st.cache_data
def load_portfolio_data(portfolio_type: str) -> tuple[pd.DataFrame, list, dict]:
    """
    Charger les données pour le portefeuille

    Args:
        portfolio_type: Type de portefeuille (Actions, Crypto, Mixte)

    Returns:
        Tuple (DataFrame, liste des symboles, dict des symboles)
    """
    repo_stocks = get_stocks_repository()
    repo_crypto = get_crypto_repository()

    all_data = []
    available_symbols = {}

    try:
        if portfolio_type in ["Actions", "Mixte"]:
            for name, symbol in CAC40_STOCKS.items():
                df = repo_stocks.find_to_dataframe({"Symbole": symbol})
                if df is not None and len(df) > 0:
                    all_data.append(df)
                    available_symbols[name] = symbol

        if portfolio_type in ["Crypto", "Mixte"]:
            for name, symbol in CRYPTOCURRENCIES.items():
                df = repo_crypto.find_to_dataframe({"Symbole": symbol})
                if df is not None and len(df) > 0:
                    all_data.append(df)
                    available_symbols[name] = symbol

        if all_data:
            combined = pd.concat(all_data, ignore_index=True).sort_values("Date")
            return combined, list(available_symbols.keys()), available_symbols
        else:
            return None, [], {}

    except Exception as e:
        logger.error(f"Error loading portfolio data: {e}")
        st.error(f"Erreur lors du chargement des données: {e}")
        return None, [], {}


# Charger les données
df, available_assets, symbol_map = load_portfolio_data(portfolio_type)

if not available_assets:
    empty_state(
        title="Aucune donnée disponible",
        message=f"Chargez des données dans les pages Bourses ou Crypto d'abord ({portfolio_type})",
        icon="💾"
    )
    st.stop()

# Sélectionner les actifs
selected_assets = st.sidebar.multiselect(
    "Sélectionner les actifs",
    options=available_assets,
    default=available_assets[:3] if len(available_assets) >= 3 else available_assets,
)

if not selected_assets:
    empty_state(
        title="Aucun actif sélectionné",
        message="Sélectionnez au moins un actif dans les paramètres",
        icon="📊"
    )
    st.stop()

# Définir les poids
st.sidebar.subheader("Poids du portefeuille")
weights = {}
total_weight = 0

for asset in selected_assets:
    weight = st.sidebar.slider(
        f"Poids de {asset}",
        min_value=0.0,
        max_value=1.0,
        value=1.0 / len(selected_assets),
        step=0.01,
    )
    weights[symbol_map[asset]] = weight
    total_weight += weight

# Normaliser les poids
if total_weight > 0:
    weights = {k: v / total_weight for k, v in weights.items()}

st.sidebar.info(f"Total des poids: {sum(weights.values()):.2%}")

# Filtrer les données pour les actifs sélectionnés
selected_symbols = [symbol_map[asset] for asset in selected_assets]
df_portfolio = df[df["Symbole"].isin(selected_symbols)].copy()

if len(df_portfolio) == 0:
    error_message(
        "Pas de données disponibles",
        icon="❌",
        details="Vérifiez que les actifs ont des données chargées"
    )
    st.stop()

# Préparer les données
df_portfolio = DataTransformer.normalize_dates(df_portfolio)
df_portfolio = DataTransformer.drop_duplicates(df_portfolio)
df_portfolio = DataTransformer.set_datetime_index(df_portfolio)

# Créer le moteur de portefeuille
try:
    engine = PortfolioEngine(df_portfolio, weights)
except Exception as e:
    logger.error(f"Error creating portfolio engine: {e}")
    error_message(
        "Erreur lors de la création du portefeuille",
        icon="❌",
        details=str(e)
    )
    st.stop()

# Onglets
tab1, tab2, tab3 = st.tabs(["📊 Portefeuille", "📈 Performance", "🎯 Métriques"])

with tab1:
    st.subheader("Composition du portefeuille")

    # Afficher les poids avec composants
    weights_df = pd.DataFrame(
        list(weights.items()), columns=["Symbole", "Poids"]
    ).sort_values("Poids", ascending=False)

    col1, col2 = st.columns([2, 3])
    with col1:
        data_table(
            weights_df,
            title="Allocation des actifs",
            description=f"{len(weights)} actif(s) dans le portefeuille",
            format_rules={"Poids": lambda x: f"{float(x):.2%}"},
            show_index=False
        )

    with col2:
        def draw_weights_chart():
            st.bar_chart(weights)

        chart_card(
            title="Distribution des poids",
            chart_func=draw_weights_chart,
            description="Allocation visuelle du portefeuille"
        )

with tab2:
    st.subheader("Performance du portefeuille")

    try:
        # Agréger le portefeuille
        portfolio = engine.aggregate_portfolio()

        # Graphique des valeurs du portefeuille
        def draw_portfolio_value():
            st.line_chart(portfolio["Portfolio_Value"], use_container_width=True)

        chart_card(
            title="Valeur du portefeuille",
            chart_func=draw_portfolio_value,
            description="Évolution de la valeur totale"
        )

        # Rendements cumulés
        portfolio["Cumulative_Return"] = (
            (1 + portfolio["Portfolio_Return"]).cumprod() - 1
        )

        def draw_cumulative_returns():
            st.line_chart(portfolio["Cumulative_Return"], use_container_width=True)

        chart_card(
            title="Rendements cumulés",
            chart_func=draw_cumulative_returns,
            description="Performance cumulée depuis le début"
        )

    except Exception as e:
        logger.error(f"Error calculating portfolio performance: {e}")
        error_message(
            "Erreur lors du calcul de la performance",
            icon="❌",
            details=str(e)
        )

with tab3:
    st.subheader("Métriques de risque/rendement")

    try:
        portfolio = engine.aggregate_portfolio()
        returns = portfolio["Portfolio_Return"].dropna()

        if len(returns) > 0:
            # Calculer les KPIs
            periods_per_year = 252 if portfolio_type == "Actions" else 365
            kpis = engine.compute_metrics(returns, periods_per_year=periods_per_year)

            # Afficher les KPIs avec metric_card_grid
            metric_card_grid({
                "annual_return": {
                    "title": "Rendement annualisé",
                    "value": f"{kpis['annual_return']:.2%}",
                    "delta": f"{kpis['total_return']:.2%}",
                    "delta_color": "positive" if kpis['annual_return'] > 0 else "negative",
                    "icon": "📈"
                },
                "volatility": {
                    "title": "Volatilité annualisée",
                    "value": f"{kpis['volatility']:.2%}",
                    "delta": "écart-type annuel",
                    "delta_color": "warning",
                    "icon": "🌊"
                },
                "sharpe_ratio": {
                    "title": "Sharpe Ratio",
                    "value": f"{kpis['sharpe_ratio']:.2f}",
                    "delta": "risque/rendement",
                    "delta_color": "positive" if kpis['sharpe_ratio'] > 0 else "negative",
                    "icon": "⚖️"
                },
                "sortino_ratio": {
                    "title": "Sortino Ratio",
                    "value": f"{kpis['sortino_ratio']:.2f}",
                    "delta": "risque baissier",
                    "delta_color": "positive" if kpis['sortino_ratio'] > 0 else "negative",
                    "icon": "📊"
                },
            }, columns=4)

            st.divider()

            # Métriques supplémentaires avec key_value_table
            key_value_table({
                "Max Drawdown": f"{kpis['max_drawdown']:.2%}",
                "Nombre de jours": f"{len(returns):,}",
                "Rendement total": f"{kpis['total_return']:.2%}",
                "Rendement annuel": f"{kpis['annual_return']:.2%}",
            }, title="Métriques détaillées")

    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        error_message(
            "Erreur lors du calcul des métriques",
            icon="❌",
            details=str(e)
        )
