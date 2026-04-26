"""
Page Streamlit : ML Forecasting

Refactorisée avec composants réutilisables et CSS moderne minimalist
"""
import streamlit as st
import pandas as pd
import numpy as np

from config.constants import CAC40_STOCKS, CRYPTOCURRENCIES
from core.data_transformer import DataTransformer
from data_layer.repository import get_stocks_repository, get_crypto_repository
from ml.forecaster import PriceForecaster
from utils.logger import setup_logger
from app.styles import inject_custom_css
from app.components import (
    metric_card_grid,
    chart_card,
    comparison_table,
    data_table,
    empty_state,
    error_message,
    success_message,
)

logger = setup_logger(__name__)

st.set_page_config(page_title="ML Forecast", page_icon="🤖", layout="wide")
inject_custom_css()

st.title("🤖 Prédictions ML - Forecasting")

# Sidebar : Configuration du forecasting
st.sidebar.header("Configuration du forecast")

# Sélectionner le type d'actif
asset_type = st.sidebar.radio(
    "Type d'actif",
    options=["Actions", "Crypto"],
    help="Sélectionner le type d'actif",
)

# Charger la liste des actifs disponibles
if asset_type == "Actions":
    available_assets = list(CAC40_STOCKS.keys())
    asset_map = CAC40_STOCKS
    repo = get_stocks_repository()
else:
    available_assets = list(CRYPTOCURRENCIES.keys())
    asset_map = CRYPTOCURRENCIES
    repo = get_crypto_repository()

# Sélectionner un actif
selected_asset = st.sidebar.selectbox(
    "Sélectionner un actif",
    options=available_assets,
    help="Choisir l'actif à prédir",
)

symbol = asset_map[selected_asset]

# Paramètres du forecasting
st.sidebar.subheader("Paramètres du forecast")
forecast_days = st.sidebar.slider(
    "Nombre de jours à prédir",
    min_value=1,
    max_value=365,
    value=30,
    step=1,
)

model_name = st.sidebar.selectbox(
    "Modèle ML",
    options=[
        "Linear Regression",
        "Random Forest",
        "Support Vector Regression",
        "Gradient Boosting",
        "XGBoost",
        "Ridge Regression",
        "Lasso Regression",
        "Elastic Net",
        "Decision Tree",
        "K-Nearest Neighbors",
        "Multilayer Perceptron",
        "AdaBoost",
    ],
    index=1,  # Random Forest par défaut
)

confidence_level = st.sidebar.slider(
    "Niveau de confiance",
    min_value=0.80,
    max_value=0.99,
    value=0.95,
    step=0.01,
)

# Fonctions


@st.cache_data
def load_historical_data(symbol: str, asset_type: str) -> pd.Series:
    """
    Charger les données historiques

    Args:
        symbol: Symbole de l'actif
        asset_type: Type d'actif (Actions ou Crypto)

    Returns:
        Series de prix historiques
    """
    try:
        if asset_type == "Actions":
            repo = get_stocks_repository()
        else:
            repo = get_crypto_repository()

        df = repo.find_to_dataframe({"Symbole": symbol})

        if df is not None and len(df) > 0:
            # Préparer les données
            df = DataTransformer.normalize_dates(df)
            df = df.sort_values("Date")

            # Créer une série de prix
            prices = pd.Series(
                df["Close"].values, index=pd.to_datetime(df["Date"])
            )
            return prices

        return None

    except Exception as e:
        logger.error(f"Error loading historical data: {e}")
        st.error(f"Erreur lors du chargement des données: {e}")
        return None


# Charger les données
prices = load_historical_data(symbol, asset_type)

if prices is None or len(prices) < 10:
    error_message(
        "Données insuffisantes",
        icon="❌",
        details=f"Besoin d'au moins 10 jours de données pour {selected_asset}. "
                f"Chargez les données dans les pages Bourses ou Crypto d'abord."
    )
    st.stop()

# Onglets
tab1, tab2, tab3 = st.tabs(["📊 Données historiques", "🔮 Prédictions", "📊 Benchmark"])

with tab1:
    st.subheader("Données historiques")

    # Calculer les statistiques
    price_change_pct = ((prices.iloc[-1] / prices.iloc[0] - 1) * 100)

    # Afficher les KPIs
    metric_card_grid({
        "days": {
            "title": "Nombre de jours",
            "value": f"{len(prices):,}",
            "delta": "observations",
            "delta_color": "positive",
            "icon": "📅"
        },
        "current": {
            "title": "Prix actuel",
            "value": f"${prices.iloc[-1]:.2f}",
            "delta": f"${prices.iloc[-1] - prices.iloc[-2]:.2f}" if len(prices) > 1 else "N/A",
            "delta_color": "positive" if prices.iloc[-1] > prices.iloc[-2] else "negative" if len(prices) > 1 else "positive",
            "icon": "💰"
        },
        "change": {
            "title": "Variation totale",
            "value": f"{price_change_pct:.2f}%",
            "delta": f"depuis {len(prices)} jours",
            "delta_color": "positive" if price_change_pct > 0 else "negative",
            "icon": "📈"
        },
    }, columns=3)

    st.divider()

    # Graphique des prix historiques
    def draw_historical_prices():
        st.line_chart(prices, use_container_width=True)

    chart_card(
        title="Historique des prix",
        chart_func=draw_historical_prices,
        description=f"Évolution du prix de {selected_asset} ({asset_type})"
    )

with tab2:
    st.subheader("Prédictions")

    try:
        # Créer le forecaster
        forecaster = PriceForecaster(prices)

        # Afficher les top modèles
        with st.spinner("Analyse des modèles..."):
            benchmark_results = forecaster.benchmark_models()

        st.markdown("**Top 3 modèles performants:**")
        comparison_table(
            benchmark_results.head(3),
            title="Meilleurs modèles"
        )

        st.divider()

        # Faire les prédictions
        with st.spinner(f"Prédiction avec {model_name}..."):
            forecast_df = forecaster.forecast(model_name=model_name, days=forecast_days)
            forecast_with_ci = forecaster.forecast_with_confidence(
                model_name=model_name,
                days=forecast_days,
                confidence_level=confidence_level,
            )

        success_message(f"Prédictions complétées avec {model_name}!", icon="✅")

        # Afficher les prédictions avec graphique
        def draw_forecast_chart():
            forecast_for_plot = forecast_with_ci.set_index("Date")
            st.line_chart(
                forecast_for_plot[["Predicted_Price", "Upper_Bound", "Lower_Bound"]],
                use_container_width=True
            )

        chart_card(
            title=f"Prédictions pour les {forecast_days} prochains jours",
            chart_func=draw_forecast_chart,
            description=f"Modèle: {model_name} | Confiance: {confidence_level:.0%}"
        )

        st.divider()

        # Statistiques des prédictions
        metric_card_grid({
            "mean": {
                "title": "Prix moyen prédit",
                "value": f"${forecast_df['Predicted_Price'].mean():.2f}",
                "delta": "moyenne sur période",
                "delta_color": "positive",
                "icon": "📊"
            },
            "min": {
                "title": "Prix minimum",
                "value": f"${forecast_df['Predicted_Price'].min():.2f}",
                "delta": "valeur basse",
                "delta_color": "warning",
                "icon": "📉"
            },
            "max": {
                "title": "Prix maximum",
                "value": f"${forecast_df['Predicted_Price'].max():.2f}",
                "delta": "valeur haute",
                "delta_color": "positive",
                "icon": "📈"
            },
            "volatility": {
                "title": "Volatilité prédite",
                "value": f"${forecast_df['Predicted_Price'].std():.2f}",
                "delta": "écart-type",
                "delta_color": "warning",
                "icon": "🌊"
            },
        }, columns=4)

        st.divider()

        # Tableau détaillé des prédictions
        data_table(
            forecast_with_ci,
            title="Détail des prédictions",
            description=f"Prédictions avec intervalle de confiance {confidence_level:.0%}",
            format_rules={
                "Predicted_Price": lambda x: f"${x:.2f}",
                "Upper_Bound": lambda x: f"${x:.2f}",
                "Lower_Bound": lambda x: f"${x:.2f}",
            }
        )

    except Exception as e:
        logger.error(f"Error making forecast: {e}")
        error_message(
            "Erreur lors de la prédiction",
            icon="❌",
            details=str(e)
        )

with tab3:
    st.subheader("Comparaison des modèles")

    try:
        forecaster = PriceForecaster(prices)

        with st.spinner("Benchmarking tous les modèles..."):
            benchmark_results = forecaster.benchmark_models()

        # Tableau complet avec composant
        comparison_table(
            benchmark_results,
            title="Benchmark de tous les modèles ML"
        )

        st.divider()

        # Graphiques de comparaison
        col1, col2 = st.columns(2)

        with col1:
            def draw_r2_chart():
                r2_data = benchmark_results.set_index("Modèle")["R² Score"].sort_values(ascending=True)
                st.bar_chart(r2_data)

            chart_card(
                title="R² Score par modèle",
                chart_func=draw_r2_chart,
                description="Qualité d'ajustement (plus haut = mieux)"
            )

        with col2:
            def draw_rmse_chart():
                rmse_data = benchmark_results.set_index("Modèle")["RMSE"].sort_values(ascending=True)
                st.bar_chart(rmse_data)

            chart_card(
                title="RMSE par modèle",
                chart_func=draw_rmse_chart,
                description="Erreur moyenne (plus bas = mieux)"
            )

    except Exception as e:
        logger.error(f"Error benchmarking models: {e}")
        error_message(
            "Erreur lors du benchmark",
            icon="❌",
            details=str(e)
        )
