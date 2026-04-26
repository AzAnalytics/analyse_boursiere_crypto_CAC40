"""
Script d'orchestration - Exemple complet d'utilisation de la nouvelle architecture

Ce script montre comment:
1. Fetcher les données (stocks + crypto)
2. Transformer/nettoyer les données
3. Insérer dans MongoDB
4. Lire les données et calculer KPIs de portefeuille
5. Afficher les résultats
"""
import sys
from typing import Dict

import pandas as pd

from config.settings import settings
from config.constants import (
    CAC40_STOCKS,
    CRYPTOCURRENCIES,
    CAC40_INDEX,
    ASSET_TYPE_STOCK,
    ASSET_TYPE_CRYPTO,
)
from core.data_fetcher import create_stock_fetcher, create_crypto_fetcher
from core.data_transformer import DataTransformer
from core.portfolio_engine import PortfolioEngine
from data_layer.repository import get_stocks_repository, get_crypto_repository
from utils.logger import setup_logger

logger = setup_logger(__name__)


def fetch_and_store_stocks(period: str = "1y") -> pd.DataFrame:
    """
    Fetcher les données d'actions et les stocker dans MongoDB

    Args:
        period: Période ("max", "1y", "5y", etc.)

    Returns:
        DataFrame avec les données
    """
    logger.info("=" * 60)
    logger.info("ÉTAPE 1 : Fetcher les données d'actions")
    logger.info("=" * 60)

    # Ajouter l'indice CAC40
    symbols = {**CAC40_STOCKS, "CAC40": CAC40_INDEX}

    # Créer et utiliser le fetcher
    fetcher = create_stock_fetcher(symbols)
    df_stocks = fetcher.fetch_all(period=period)

    if df_stocks.empty:
        logger.error("Aucune donnée d'actions fetchée !")
        return df_stocks

    # Transformer
    logger.info("Nettoyage des données...")
    df_stocks = DataTransformer.normalize_dates(df_stocks)
    df_stocks = DataTransformer.drop_duplicates(df_stocks)

    # Stocker dans MongoDB
    logger.info("Stockage dans MongoDB...")
    repo = get_stocks_repository()
    records = df_stocks.to_dict("records")
    repo.insert_many(records, ignore_duplicates=True)

    logger.info(f"✓ {len(df_stocks)} enregistrements stocks stockés")
    return df_stocks


def fetch_and_store_crypto(period: str = "1y") -> pd.DataFrame:
    """
    Fetcher les données de crypto et les stocker dans MongoDB

    Args:
        period: Période ("max", "1y", etc.)

    Returns:
        DataFrame avec les données
    """
    logger.info("=" * 60)
    logger.info("ÉTAPE 2 : Fetcher les données de crypto")
    logger.info("=" * 60)

    fetcher = create_crypto_fetcher(CRYPTOCURRENCIES)
    df_crypto = fetcher.fetch_all(period=period)

    if df_crypto.empty:
        logger.error("Aucune donnée de crypto fetchée !")
        return df_crypto

    # Transformer
    logger.info("Nettoyage des données...")
    df_crypto = DataTransformer.normalize_dates(df_crypto)
    df_crypto = DataTransformer.drop_duplicates(df_crypto)

    # Stocker
    logger.info("Stockage dans MongoDB...")
    repo = get_crypto_repository()
    records = df_crypto.to_dict("records")
    repo.insert_many(records, ignore_duplicates=True)

    logger.info(f"✓ {len(df_crypto)} enregistrements crypto stockés")
    return df_crypto


def calculate_portfolio_kpis(
    symbols: Dict[str, float],
    asset_type: str = ASSET_TYPE_STOCK,
    risk_free_rate: float = 0.02,
) -> Dict:
    """
    Calculer les KPIs d'un portefeuille

    Args:
        symbols: Dict{symbole: poids}
        asset_type: "stock" ou "crypto"
        risk_free_rate: Taux sans risque

    Returns:
        Dict avec KPIs
    """
    logger.info("=" * 60)
    logger.info("ÉTAPE 3 : Calculer les KPIs du portefeuille")
    logger.info("=" * 60)

    # Récupérer les données
    repo = get_stocks_repository() if asset_type == ASSET_TYPE_STOCK else get_crypto_repository()
    df = repo.find_to_dataframe({})

    if df.empty:
        logger.error(f"Aucune donnée {asset_type} trouvée !")
        return {}

    # Transformer
    df = DataTransformer.normalize_dates(df)
    df = DataTransformer.set_datetime_index(df)

    # Créer engine et calculer
    engine = PortfolioEngine(df, symbols)
    portfolio = engine.aggregate_portfolio()

    # Calculer rendements et KPIs
    returns = portfolio["Portfolio_Value"].pct_change().dropna()
    kpis = engine.compute_metrics(returns, risk_free_rate=risk_free_rate)

    logger.info("✓ KPIs calculés:")
    for key, value in kpis.items():
        if isinstance(value, float):
            logger.info(f"  {key}: {value:.4f}")

    return {
        "kpis": kpis,
        "portfolio": portfolio,
        "returns": returns,
    }


def main():
    """Orchestration complète"""
    try:
        logger.info("🚀 Démarrage du pipeline")

        # 1. Fetcher et stocker stocks
        df_stocks = fetch_and_store_stocks(period="1y")

        # 2. Fetcher et stocker crypto
        df_crypto = fetch_and_store_crypto(period="1y")

        # 3. Calculer KPIs portefeuille (exemple: 60/40 stocks/CAC40)
        portfolio_weights = {
            "BNP.PA": 0.20,
            "OR.PA": 0.20,
            "MC.PA": 0.20,
            "CAC40": 0.40,
        }
        result = calculate_portfolio_kpis(portfolio_weights, asset_type=ASSET_TYPE_STOCK)

        logger.info("✓ Pipeline terminé avec succès !")
        return result

    except Exception as e:
        logger.error(f"❌ Erreur dans le pipeline: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
