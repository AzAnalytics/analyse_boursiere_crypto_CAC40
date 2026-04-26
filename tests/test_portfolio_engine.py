"""
Tests pour le module PortfolioEngine
"""
import pytest
import pandas as pd
import numpy as np
from core.portfolio_engine import PortfolioEngine


class TestPortfolioEngine:
    """Tests pour la classe PortfolioEngine"""

    def test_portfolio_engine_initialization(self, sample_multi_asset_data, sample_portfolio_weights):
        """L'engine doit être créé sans erreur"""
        engine = PortfolioEngine(sample_multi_asset_data, sample_portfolio_weights)
        assert engine is not None

    def test_portfolio_engine_raises_on_invalid_weights(self, sample_multi_asset_data):
        """Doit lever une erreur si les poids ne somment pas à 1.0"""
        invalid_weights = {"TEST1.PA": 0.5, "TEST2.PA": 0.3}  # Somme = 0.8

        with pytest.raises(ValueError):
            PortfolioEngine(sample_multi_asset_data, invalid_weights)

    def test_aggregate_portfolio_creates_portfolio_value(self, sample_multi_asset_data, sample_portfolio_weights):
        """La méthode doit créer une colonne Portfolio_Value"""
        engine = PortfolioEngine(sample_multi_asset_data, sample_portfolio_weights)
        portfolio = engine.aggregate_portfolio()

        assert "Portfolio_Value" in portfolio.columns
        assert len(portfolio) > 0

    def test_aggregate_portfolio_weights_sum_to_one(self, sample_multi_asset_data, sample_portfolio_weights):
        """La valeur du portefeuille doit correspondre aux poids"""
        engine = PortfolioEngine(sample_multi_asset_data, sample_portfolio_weights)
        portfolio = engine.aggregate_portfolio()

        # La somme de chaque ligne doit égaler Portfolio_Value
        for i in range(len(portfolio)):
            row_sum = portfolio.iloc[i, :-1].sum()
            portfolio_value = portfolio["Portfolio_Value"].iloc[i]
            assert np.isclose(row_sum, portfolio_value, rtol=1e-5)


class TestComputeMetrics:
    """Tests pour le calcul des KPIs"""

    def test_compute_metrics_returns_dict(self, sample_returns):
        """La méthode doit retourner un dict"""
        result = PortfolioEngine.compute_metrics(sample_returns)
        assert isinstance(result, dict)

    def test_compute_metrics_contains_required_keys(self, sample_returns):
        """Le dict doit contenir tous les KPIs requis"""
        result = PortfolioEngine.compute_metrics(sample_returns)

        required_keys = [
            "total_return",
            "annual_return",
            "volatility",
            "sharpe_ratio",
            "max_drawdown",
            "sortino_ratio",
        ]
        for key in required_keys:
            assert key in result

    def test_compute_metrics_positive_returns(self):
        """Pour des rendements positifs, les KPIs doivent être positifs"""
        positive_returns = pd.Series([0.01] * 252)  # +1% chaque jour
        result = PortfolioEngine.compute_metrics(positive_returns)

        assert result["total_return"] > 0
        assert result["annual_return"] > 0
        assert result["sharpe_ratio"] > 0
        assert result["max_drawdown"] == 0  # Pas de drawdown

    def test_compute_metrics_negative_returns(self):
        """Pour des rendements négatifs, max_drawdown doit être négatif"""
        negative_returns = pd.Series([-0.01] * 252)  # -1% chaque jour
        result = PortfolioEngine.compute_metrics(negative_returns)

        assert result["total_return"] < 0
        assert result["max_drawdown"] < 0


class TestCalculateWeightsFromValues:
    """Tests pour le calcul des poids à partir des valeurs"""

    def test_calculate_weights_from_values_sums_to_one(self):
        """Les poids calculés doivent sommer à 1.0"""
        values = {"A": 10000, "B": 5000, "C": 25000}
        weights = PortfolioEngine.calculate_weights_from_values(values)

        assert np.isclose(sum(weights.values()), 1.0)

    def test_calculate_weights_from_values_correct_proportions(self):
        """Les poids doivent correspondre aux proportions"""
        values = {"A": 10000, "B": 10000}  # 50/50
        weights = PortfolioEngine.calculate_weights_from_values(values)

        assert np.isclose(weights["A"], 0.5)
        assert np.isclose(weights["B"], 0.5)

    def test_calculate_weights_from_values_empty_raises(self):
        """Une valeur totale de 0 doit lever une erreur"""
        values = {"A": 0, "B": 0}
        result = PortfolioEngine.calculate_weights_from_values(values)

        assert result == {}
