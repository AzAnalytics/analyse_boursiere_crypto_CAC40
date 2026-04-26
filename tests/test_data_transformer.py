"""
Tests pour le module DataTransformer
"""
import pytest
import pandas as pd
import numpy as np
from core.data_transformer import DataTransformer


class TestNormalizeDates:
    """Tests pour la normalisation des dates"""

    def test_normalize_dates_converts_string_to_datetime(self, sample_ohlcv_data):
        """Les dates string doivent être converties en datetime"""
        df = sample_ohlcv_data.copy()
        df["Date"] = df["Date"].dt.strftime("%d/%m/%Y")  # Convertir en string

        result = DataTransformer.normalize_dates(df)
        assert pd.api.types.is_datetime64_any_dtype(result["Date"])

    def test_normalize_dates_sorts_by_date(self, sample_ohlcv_data):
        """Les dates doivent être triées en ordre croissant"""
        df = sample_ohlcv_data.sample(frac=1, random_state=42).reset_index(drop=True)

        result = DataTransformer.normalize_dates(df)
        assert (result["Date"] == result["Date"].sort_values()).all()

    def test_normalize_dates_removes_invalid_dates(self):
        """Les dates invalides doivent être supprimées"""
        df = pd.DataFrame({
            "Date": ["01/01/2024", "invalid", "03/01/2024"],
            "Close": [100, 101, 102],
        })

        result = DataTransformer.normalize_dates(df)
        assert len(result) == 2  # La ligne invalide doit être supprimée


class TestDropDuplicates:
    """Tests pour la suppression des doublons"""

    def test_drop_duplicates_removes_exact_duplicates(self, sample_ohlcv_data):
        """Les doublons exacts doivent être supprimés"""
        df = pd.concat([sample_ohlcv_data, sample_ohlcv_data.head(5)], ignore_index=True)
        assert len(df) > len(sample_ohlcv_data)

        result = DataTransformer.drop_duplicates(df, subset=["Date", "Symbole"])
        assert len(result) == len(sample_ohlcv_data)

    def test_drop_duplicates_keeps_first(self, sample_ohlcv_data):
        """Pour les doublons, la première ligne doit être gardée"""
        df = sample_ohlcv_data.copy()
        df.loc[0, "Close"] = 999

        df = pd.concat([df, df.head(1)], ignore_index=True)
        df.loc[len(df) - 1, "Close"] = 888

        result = DataTransformer.drop_duplicates(df)
        assert result.iloc[0]["Close"] == 999  # Première valeur conservée


class TestValidateOHLCV:
    """Tests pour la validation OHLCV"""

    def test_validate_ohlcv_returns_true_for_valid_data(self, sample_ohlcv_data):
        """Les données valides doivent passer la validation"""
        assert DataTransformer.validate_ohlcv(sample_ohlcv_data)

    def test_validate_ohlcv_returns_false_for_invalid_high_low(self):
        """Si High < Low, la validation doit échouer"""
        df = pd.DataFrame({
            "Open": [100],
            "High": [90],  # High < Low
            "Low": [95],
            "Close": [92],
        })
        assert not DataTransformer.validate_ohlcv(df)

    def test_validate_ohlcv_returns_false_for_missing_columns(self):
        """Les colonnes manquantes doivent causer l'échec"""
        df = pd.DataFrame({
            "Open": [100],
            "Close": [105],
        })
        assert not DataTransformer.validate_ohlcv(df)


class TestCalculateReturns:
    """Tests pour le calcul des rendements"""

    def test_calculate_returns_creates_returns_column(self, sample_ohlcv_data):
        """Une colonne Returns doit être créée"""
        result = DataTransformer.calculate_returns(sample_ohlcv_data)
        assert "Returns" in result.columns

    def test_calculate_returns_first_is_nan(self, sample_ohlcv_data):
        """Le premier rendement doit être NaN"""
        result = DataTransformer.calculate_returns(sample_ohlcv_data)
        assert pd.isna(result["Returns"].iloc[0])

    def test_calculate_returns_values_are_correct(self):
        """Les rendements doivent être calculés correctement"""
        df = pd.DataFrame({
            "Date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "Close": [100, 110, 99],
        })

        result = DataTransformer.calculate_returns(df)

        # Rendement 110/100 - 1 = 0.10
        assert np.isclose(result["Returns"].iloc[1], 0.10)
        # Rendement 99/110 - 1 = -0.10
        assert np.isclose(result["Returns"].iloc[2], -0.10)


class TestCalculateLogReturns:
    """Tests pour les log-rendements"""

    def test_calculate_log_returns_creates_column(self, sample_ohlcv_data):
        """Une colonne LogReturns doit être créée"""
        result = DataTransformer.calculate_log_returns(sample_ohlcv_data)
        assert "LogReturns" in result.columns

    def test_calculate_log_returns_first_is_nan(self, sample_ohlcv_data):
        """Le premier log-rendement doit être NaN"""
        result = DataTransformer.calculate_log_returns(sample_ohlcv_data)
        assert pd.isna(result["LogReturns"].iloc[0])
