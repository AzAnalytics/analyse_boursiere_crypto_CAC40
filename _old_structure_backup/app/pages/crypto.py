"""
Page Streamlit : Analyse des Cryptomonnaies

Refactorisée avec composants réutilisables et CSS moderne minimalist
"""
import streamlit as st
import pandas as pd
import numpy as np

from config.constants import CRYPTOCURRENCIES
from core.data_fetcher import create_crypto_fetcher
from core.data_transformer import DataTransformer
from data_layer.repository import get_crypto_repository
from utils.logger import setup_logger
from app.styles import inject_custom_css
from app.components import (
    chart_card,
    data_table,
    metric_card_grid,
    success_message,
    empty_state,
)

logger = setup_logger(__name__)

# Configuration Streamlit
st.set_page_config(page_title="Crypto Analysis", page_icon="🪙", layout="wide")

# Inject custom styling
inject_custom_css()

st.title("🪙 Analyse des Cryptomonnaies")

# Sidebar : Configuration
st.sidebar.header("⚙️ Paramètres")

cryptos_to_fetch = st.sidebar.multiselect(
    "Sélectionner les cryptomonnaies",
    options=list(CRYPTOCURRENCIES.keys()),
    default=["Bitcoin", "Ethereum"],
    help="Choisir les cryptos à analyser",
)

period = st.sidebar.select_slider(
    "Période de données",
    options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
    value="1y",
)

refresh_data = st.sidebar.button("🔄 Rafraîchir les données", use_container_width=True)

# Fonctions utilitaires


@st.cache_data(ttl=3600)
def fetch_and_store_crypto(symbols: dict, period: str):
    """
    Fetcher et stocker les données crypto

    Args:
        symbols: Dict des cryptos à fetcher
        period: Période de données

    Returns:
        DataFrame avec les données
    """
    try:
        logger.info(f"Fetching {len(symbols)} cryptos for period {period}...")
        fetcher = create_crypto_fetcher(symbols)
        df = fetcher.fetch_all(period=period)

        # Transformer les données
        df = DataTransformer.normalize_dates(df)
        df = DataTransformer.drop_duplicates(df)

        # Stocker dans MongoDB
        repo = get_crypto_repository()
        repo.insert_many(df.to_dict("records"), ignore_duplicates=True)

        logger.info(f"✓ {len(df)} records stored successfully")
        return df

    except Exception as e:
        logger.error(f"Error fetching crypto data: {e}")
        st.error(f"Erreur lors du fetch: {e}")
        return None


@st.cache_data
def get_stored_crypto(symbols: dict):
    """
    Récupérer les données crypto stockées dans MongoDB

    Args:
        symbols: Dict des cryptos à récupérer

    Returns:
        DataFrame avec les données
    """
    try:
        repo = get_crypto_repository()
        symbol_values = list(symbols.values())

        # Fetch pour chaque symbole
        all_data = []
        for symbol in symbol_values:
            df = repo.find_to_dataframe({"Symbole": symbol})
            if df is not None and len(df) > 0:
                all_data.append(df)

        if all_data:
            result = pd.concat(all_data, ignore_index=True)
            return result.sort_values("Date")
        return None

    except Exception as e:
        logger.warning(f"Could not load stored crypto data: {e}")
        return None


# Main app
if not cryptos_to_fetch:
    empty_state(
        title="Aucune cryptomonnaie sélectionnée",
        message="Sélectionnez au moins une cryptomonnaie dans les paramètres",
        icon="🪙"
    )
    st.stop()

selected_cryptos = {k: v for k, v in CRYPTOCURRENCIES.items() if k in cryptos_to_fetch}

# Onglets
tab1, tab2, tab3 = st.tabs(["📊 Données", "📈 Graphiques", "📋 Statistiques"])

with tab1:
    st.subheader("Données brutes")

    col1, col2 = st.columns([3, 1])
    with col2:
        load_btn = st.button("📥 Charger", key="load_crypto", use_container_width=True)

    if refresh_data or load_btn:
        with st.spinner("⏳ Chargement des données..."):
            df = fetch_and_store_crypto(selected_cryptos, period)
            if df is not None:
                success_message("Données chargées avec succès!", icon="✅")
                data_table(
                    df.sort_values("Date", ascending=False).head(20),
                    title="Dernières données",
                    description=f"{len(df)} enregistrements au total",
                    format_rules={
                        "Close": lambda x: f"${x:.2f}" if pd.notna(x) else "N/A",
                        "Volume": lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A",
                    }
                )
    else:
        df = get_stored_crypto(selected_cryptos)
        if df is not None:
            data_table(
                df.sort_values("Date", ascending=False).head(20),
                title="Dernières données (cached)",
                description=f"{len(df)} enregistrements au total",
                format_rules={
                    "Close": lambda x: f"${x:.2f}" if pd.notna(x) else "N/A",
                    "Volume": lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A",
                }
            )
        else:
            empty_state(
                title="Pas de données disponibles",
                message="Cliquez sur 'Charger' pour récupérer les données",
                icon="💾"
            )

with tab2:
    st.subheader("Graphiques de performance")
    df = get_stored_crypto(selected_cryptos)

    if df is not None and "Close" in df.columns:
        # Graphique des prix
        def draw_price_chart():
            st.line_chart(
                data=df.set_index("Date")[["Close"]],
                use_container_width=True
            )

        chart_card(
            title="Prix de marché",
            chart_func=draw_price_chart,
            description="Évolution du prix des cryptomonnaies (USD)",
        )

        # Graphique des rendements
        if len(df) > 1:
            df_copy = df.copy()
            df_copy = DataTransformer.calculate_returns(df_copy)

            def draw_returns_chart():
                st.area_chart(
                    data=df_copy.set_index("Date")[["Daily_Return"]],
                    use_container_width=True
                )

            chart_card(
                title="Rendements quotidiens",
                chart_func=draw_returns_chart,
                description="Distribution des rendements journaliers (volatilité)",
            )
    else:
        empty_state(
            title="Pas de données disponibles",
            message="Chargez les données dans l'onglet précédent",
            icon="📈"
        )

with tab3:
    st.subheader("Analyse statistique")
    df = get_stored_crypto(selected_cryptos)

    if df is not None and "Close" in df.columns:
        # Calculer les statistiques (annualization = 365 jours pour les cryptos)
        df_analysis = df.copy()
        df_analysis = DataTransformer.calculate_returns(df_analysis)

        annual_return = df_analysis["Daily_Return"].mean() * 365 if "Daily_Return" in df_analysis.columns else 0
        volatility = df_analysis["Daily_Return"].std() * np.sqrt(365) if "Daily_Return" in df_analysis.columns else 0
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0

        # KPIs
        metric_card_grid({
            "annual_return": {
                "title": "Rendement annualisé",
                "value": f"{annual_return:.2%}",
                "delta": "sur la période",
                "delta_color": "positive" if annual_return > 0 else "negative",
                "icon": "📈"
            },
            "volatility": {
                "title": "Volatilité annualisée",
                "value": f"{volatility:.2%}",
                "delta": "écart-type annuel",
                "delta_color": "warning",
                "icon": "🌊"
            },
            "sharpe_ratio": {
                "title": "Sharpe Ratio",
                "value": f"{sharpe_ratio:.2f}",
                "delta": "ratio risque/rendement",
                "delta_color": "positive" if sharpe_ratio > 0 else "negative",
                "icon": "⚖️"
            }
        }, columns=3)

        st.divider()

        # Statistiques descriptives
        st.markdown("### Statistiques des prix")
        stats = df["Close"].describe().round(2)
        st.dataframe(stats, use_container_width=True)

        # Stats par symbole
        if "Symbole" in df.columns:
            st.markdown("### Statistiques par cryptomonnaie")
            symbol_stats = df.groupby("Symbole")["Close"].agg([
                ("Observations", "count"),
                ("Moyenne", "mean"),
                ("Min", "min"),
                ("Max", "max"),
                ("Écart-type", "std")
            ]).round(2)
            st.dataframe(symbol_stats, use_container_width=True)

    else:
        empty_state(
            title="Pas de données disponibles",
            message="Chargez les données dans l'onglet 'Données'",
            icon="📋"
        )

st.divider()
st.caption("💡 Note : L'annualisation pour les cryptos utilise 365 jours (vs 252 pour les actions)")
