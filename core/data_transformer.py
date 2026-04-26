"""
Transformation et normalisation des données
"""
from typing import Optional
import pandas as pd
import numpy as np

from config.constants import DATE_COLUMN, SYMBOL_COLUMN
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DataTransformer:
    """Transformer les données brutes en données prêtes pour l'analyse"""

    @staticmethod
    def normalize_dates(df: pd.DataFrame, date_col: str = DATE_COLUMN) -> pd.DataFrame:
        """
        Convertir les dates au format ISO et définir comme index

        Args:
            df: DataFrame
            date_col: Nom de la colonne date

        Returns:
            DataFrame avec dates normalisées
        """
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col], format="%d/%m/%Y", errors="coerce")

        # Vérifier les dates invalides
        invalid = df[date_col].isna().sum()
        if invalid > 0:
            logger.warning(f"⚠ {invalid} dates invalides détectées")
            df = df.dropna(subset=[date_col])

        df = df.sort_values(date_col).reset_index(drop=True)
        return df

    @staticmethod
    def set_datetime_index(df: pd.DataFrame, date_col: str = DATE_COLUMN) -> pd.DataFrame:
        """Définir la colonne Date comme index"""
        df = df.copy()
        df = DataTransformer.normalize_dates(df, date_col)
        df = df.set_index(date_col)
        return df

    @staticmethod
    def align_timeseries(dfs: list, method: str = "inner") -> dict:
        """
        Aligner plusieurs séries temporelles (utile pour portefeuille)

        Args:
            dfs: Liste de DataFrames
            method: "inner" (intersection) ou "outer" (union)

        Returns:
            Dict avec DataFrames alignées
        """
        if not dfs:
            return {}

        # Prendre la première comme référence
        aligned = dfs[0].copy()
        for df in dfs[1:]:
            aligned = aligned.join(df, how=method)

        return {"aligned": aligned}

    @staticmethod
    def resample(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
        """
        Rééchantillonner une série (ex: daily -> weekly, monthly)

        Args:
            df: DataFrame avec index datetime
            freq: Fréquence ("D", "W", "M", "Y")

        Returns:
            DataFrame rééchantillonnée

        Example:
            >>> df_monthly = DataTransformer.resample(df, freq="M")
        """
        if not isinstance(df.index, pd.DatetimeIndex):
            logger.warning("⚠ Index n'est pas datetime, tentative de conversion...")
            df.index = pd.to_datetime(df.index)

        # Rééchantillonner avec OHLC
        resampled = df.resample(freq).agg({
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum",
        })

        return resampled.dropna()

    @staticmethod
    def fill_missing_values(df: pd.DataFrame, method: str = "ffill") -> pd.DataFrame:
        """
        Remplir les valeurs manquantes

        Args:
            df: DataFrame
            method: "ffill" (forward fill) ou "bfill" (backward fill)

        Returns:
            DataFrame rempli
        """
        df = df.copy()
        missing_before = df.isnull().sum().sum()

        if method == "ffill":
            df = df.fillna(method="ffill")
        elif method == "bfill":
            df = df.fillna(method="bfill")
        else:
            raise ValueError(f"Méthode invalide: {method}")

        missing_after = df.isnull().sum().sum()
        logger.info(f"Valeurs manquantes: {missing_before} → {missing_after}")

        return df

    @staticmethod
    def drop_duplicates(df: pd.DataFrame, subset=None) -> pd.DataFrame:
        """Supprimer les doublons"""
        if subset is None:
            subset = [DATE_COLUMN, SYMBOL_COLUMN]

        before = len(df)
        df = df.drop_duplicates(subset=subset, keep="first")
        after = len(df)

        if before > after:
            logger.info(f"Doublons supprimés: {before - after}")

        return df

    @staticmethod
    def validate_ohlcv(df: pd.DataFrame) -> bool:
        """
        Valider que les données OHLCV sont cohérentes

        Returns:
            True si valide

        Checks:
            - High >= Low
            - High >= Open, Close
            - Low <= Open, Close
        """
        required_cols = ["Open", "High", "Low", "Close"]
        if not all(col in df.columns for col in required_cols):
            logger.error("Colonnes OHLCV manquantes")
            return False

        # High >= Low
        invalid_high_low = (df["High"] < df["Low"]).sum()
        if invalid_high_low > 0:
            logger.warning(f"⚠ {invalid_high_low} lignes avec High < Low")

        # High >= max(Open, Close)
        invalid_high = (df["High"] < df[["Open", "Close"]].max(axis=1)).sum()
        if invalid_high > 0:
            logger.warning(f"⚠ {invalid_high} lignes avec High < max(Open, Close)")

        return invalid_high_low == 0 and invalid_high == 0

    @staticmethod
    def calculate_returns(df: pd.DataFrame, price_col: str = "Close") -> pd.DataFrame:
        """
        Calculer les rendements à partir des prix

        Args:
            df: DataFrame avec colonnes de prix
            price_col: Colonne à utiliser pour le calcul

        Returns:
            DataFrame avec colonne "Returns"
        """
        df = df.copy()
        df["Returns"] = df[price_col].pct_change()
        return df

    @staticmethod
    def calculate_log_returns(df: pd.DataFrame, price_col: str = "Close") -> pd.DataFrame:
        """
        Calculer les log-rendements (plus robustes)

        Args:
            df: DataFrame avec colonnes de prix
            price_col: Colonne à utiliser pour le calcul

        Returns:
            DataFrame avec colonne "LogReturns"
        """
        df = df.copy()
        df["LogReturns"] = np.log(df[price_col] / df[price_col].shift(1))
        return df
