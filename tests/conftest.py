"""
Pytest fixtures - Données de test réutilisables
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_ohlcv_data() -> pd.DataFrame:
    """
    Créer des données OHLCV de test

    Returns:
        DataFrame avec colonnes [Date, Symbole, Open, High, Low, Close, Volume]
    """
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    prices = np.random.uniform(90, 110, 100)
    highs = prices + np.random.uniform(0, 5, 100)
    lows = prices - np.random.uniform(0, 5, 100)
    opens = np.roll(prices, 1)

    df = pd.DataFrame({
        "Date": dates,
        "Symbole": "TEST.PA",
        "Open": opens,
        "High": highs,
        "Low": lows,
        "Close": prices,
        "Volume": np.random.uniform(1000000, 10000000, 100),
    })

    return df


@pytest.fixture
def sample_multi_asset_data() -> pd.DataFrame:
    """
    Créer des données pour plusieurs actifs

    Returns:
        DataFrame avec 3 symboles, 100 jours chacun
    """
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    symbols = ["TEST1.PA", "TEST2.PA", "TEST3.PA"]

    dfs = []
    for symbol in symbols:
        prices = np.random.uniform(80, 120, 100)
        df = pd.DataFrame({
            "Date": dates,
            "Symbole": symbol,
            "Open": np.roll(prices, 1),
            "High": prices + np.random.uniform(0, 5, 100),
            "Low": prices - np.random.uniform(0, 5, 100),
            "Close": prices,
            "Volume": np.random.uniform(1000000, 10000000, 100),
        })
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)


@pytest.fixture
def sample_returns() -> pd.Series:
    """Créer une série de rendements de test"""
    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.02, 252)  # Rendements quotidiens
    return pd.Series(returns, index=pd.date_range(start="2024-01-01", periods=252, freq="D"))


@pytest.fixture
def sample_portfolio_weights() -> dict:
    """Créer des poids de portefeuille de test"""
    return {
        "TEST1.PA": 0.40,
        "TEST2.PA": 0.35,
        "TEST3.PA": 0.25,
    }


@pytest.fixture
def sample_price_series() -> pd.Series:
    """
    Créer une série de prix réaliste pour les tests de forecaster

    Returns:
        Series de prix historiques de 2024 à 2026
    """
    np.random.seed(42)
    dates = pd.date_range(start="2024-01-01", end="2026-04-26", freq="D")
    # Simuler une marche aléatoire géométrique
    returns = np.random.normal(0.0005, 0.02, len(dates))
    prices = 100 * np.exp(np.cumsum(returns))
    return pd.Series(prices, index=dates)
