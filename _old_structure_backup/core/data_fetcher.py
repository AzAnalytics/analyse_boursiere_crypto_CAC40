"""
Module de fetch de données GÉNÉRIQUE
Remplace API_bourses/ et API_crypto/ avec une abstraction unique

Avantages :
- Zero duplication de code
- Extensible facilement (ajouter une nouvelle source = juste faire un wrapper)
- Testable
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import yfinance as yf
import pandas as pd

from config.settings import settings
from config.constants import (
    OHLCV_COLUMNS,
    DATE_COLUMN,
    SYMBOL_COLUMN,
    COLUMNS_TO_DROP,
    ASSET_TYPE_STOCK,
    ASSET_TYPE_CRYPTO,
)
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DataFetcher:
    """
    Abstraction générique pour fetcher des données financières (stocks, crypto, indices)
    Wrapper autour de yfinance

    Attributes:
        asset_type: Type d'actif ("stock", "crypto", "index")
        symbols: Dict[str, str] - Mapping {nom_lisible: symbol_ticker}
    """

    def __init__(
        self,
        asset_type: str,
        symbols: Dict[str, str],
    ):
        """
        Initialiser le fetcher

        Args:
            asset_type: Type d'actif ("stock", "crypto", "index")
            symbols: Dict des symboles {nom: ticker}

        Raises:
            ValueError: Si asset_type n'est pas valide
        """
        if asset_type not in [ASSET_TYPE_STOCK, ASSET_TYPE_CRYPTO]:
            raise ValueError(f"asset_type invalide: {asset_type}")

        self.asset_type = asset_type
        self.symbols = symbols
        logger.info(f"DataFetcher créé pour {asset_type} avec {len(symbols)} symboles")

    def fetch_single(
        self,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        period: str = "max",
        interval: str = "1d",
    ) -> Optional[pd.DataFrame]:
        """
        Fetcher les données pour UN symbole

        Args:
            symbol: Ticker (ex: "BNP.PA", "BTC-USD")
            start: Date de début (YYYY-MM-DD)
            end: Date de fin (YYYY-MM-DD)
            period: "max", "1y", "5y", etc.
            interval: "1d", "1wk", "1mo"

        Returns:
            DataFrame avec colonnes OHLCV ou None si erreur

        Example:
            >>> fetcher = DataFetcher("stock", {"BNP": "BNP.PA"})
            >>> df = fetcher.fetch_single("BNP.PA", period="1y")
        """
        try:
            logger.debug(f"Fetching {symbol} (period={period}, interval={interval})")

            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=start,
                end=end,
                period=period if period != "max" else None,
                interval=interval,
            )

            if df.empty:
                logger.warning(f"Pas de données pour {symbol}")
                return None

            # Cleanup
            df = self._clean_dataframe(df, symbol)
            logger.info(f"✓ Fetched {symbol}: {len(df)} lignes")
            return df

        except Exception as e:
            logger.error(f"Erreur lors du fetch de {symbol}: {e}")
            return None

    def fetch_all(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        period: str = "max",
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Fetcher les données pour TOUS les symboles

        Args:
            start, end, period, interval: Voir fetch_single()

        Returns:
            DataFrame concaténé avec colonnes [Date, Symbole, Open, High, Low, Close, Volume]

        Example:
            >>> fetcher = DataFetcher("stock", {"BNP": "BNP.PA", "OR": "OR.PA"})
            >>> df = fetcher.fetch_all(period="1y")
        """
        logger.info(f"Fetching {len(self.symbols)} symboles ({self.asset_type})")
        dfs = []

        for name, symbol in self.symbols.items():
            df = self.fetch_single(symbol, start=start, end=end, period=period, interval=interval)
            if df is not None:
                dfs.append(df)

        if not dfs:
            logger.warning("Aucune donnée fetchée !")
            return pd.DataFrame()

        result = pd.concat(dfs, ignore_index=True)
        logger.info(f"Total: {len(result)} lignes pour {len(dfs)} actifs")
        return result

    @staticmethod
    def _clean_dataframe(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Nettoyer le DataFrame retourné par yfinance

        1. Réinitialiser l'index (Date devient colonne)
        2. Supprimer les colonnes inutiles (Dividends, Stock Splits)
        3. Convertir les dates au format string
        4. Ajouter colonne Symbole

        Args:
            df: DataFrame brut de yfinance
            symbol: Ticker du symbole

        Returns:
            DataFrame nettoyé
        """
        df = df.reset_index()

        # Supprimer les colonnes inutiles
        df = df.drop(columns=COLUMNS_TO_DROP, errors="ignore")

        # Convertir Date en string (format European)
        if pd.api.types.is_datetime64_any_dtype(df[DATE_COLUMN]):
            df[DATE_COLUMN] = df[DATE_COLUMN].dt.strftime("%d/%m/%Y")

        # Ajouter colonne Symbole
        df[SYMBOL_COLUMN] = symbol

        # Réorganiser les colonnes
        cols_order = [DATE_COLUMN, SYMBOL_COLUMN] + [col for col in OHLCV_COLUMNS if col in df.columns]
        df = df[[col for col in cols_order if col in df.columns]]

        return df


# ===== FACTORY FUNCTIONS =====


def create_stock_fetcher(symbols: Dict[str, str]) -> DataFetcher:
    """Créer un fetcher pour les actions/indices"""
    return DataFetcher(ASSET_TYPE_STOCK, symbols)


def create_crypto_fetcher(symbols: Dict[str, str]) -> DataFetcher:
    """Créer un fetcher pour les cryptomonnaies"""
    return DataFetcher(ASSET_TYPE_CRYPTO, symbols)
