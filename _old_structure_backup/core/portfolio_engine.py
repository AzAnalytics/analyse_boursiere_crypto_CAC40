"""
Portfolio Engine - Calculs de KPIs et backtesting
Remplace portefeuille.py (avant c'était une simple classe, maintenant c'est un vrai engine)
"""
from typing import Dict, Tuple, Optional
import pandas as pd
import numpy as np

from config.constants import SYMBOL_COLUMN
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PortfolioEngine:
    """
    Engine pour les calculs de portefeuille (KPIs, agrégation, backtesting)

    Attributes:
        prices: DataFrame avec colonnes [Date, Symbole, Close]
        weights: Dict{symbole: poids} - doit sommer à 1.0
    """

    def __init__(self, prices: pd.DataFrame, weights: Dict[str, float]):
        """
        Initialiser l'engine

        Args:
            prices: DataFrame avec colonnes [Date, Symbole, Close]
            weights: Dict des poids par symbole

        Raises:
            ValueError: Si les poids ne somment pas à 1.0
        """
        self.prices = prices.copy()
        self.weights = weights

        # Validation
        total_weight = sum(weights.values())
        if not np.isclose(total_weight, 1.0):
            raise ValueError(f"Poids doivent sommer à 1.0, actuellement: {total_weight}")

        # Normaliser les dates
        if "Date" in self.prices.columns:
            self.prices["Date"] = pd.to_datetime(self.prices["Date"])
            self.prices = self.prices.set_index("Date")

        logger.info(f"PortfolioEngine créé avec {len(weights)} actifs")

    def aggregate_portfolio(self, price_col: str = "Close") -> pd.DataFrame:
        """
        Calculer la valeur du portefeuille au fil du temps

        Formula:
            Portfolio_t = Σ (weight_i × price_i_t)

        Args:
            price_col: Colonne à utiliser pour l'agrégation

        Returns:
            DataFrame avec colonne "Portfolio_Value"

        Example:
            >>> engine = PortfolioEngine(prices, {"BNP.PA": 0.5, "OR.PA": 0.5})
            >>> portfolio = engine.aggregate_portfolio()
        """
        portfolio = pd.DataFrame(index=self.prices.index)

        for symbol, weight in self.weights.items():
            symbol_data = self.prices[self.prices[SYMBOL_COLUMN] == symbol] \
                if SYMBOL_COLUMN in self.prices.columns \
                else self.prices

            if symbol_data.empty:
                logger.warning(f"Pas de données pour {symbol}")
                continue

            symbol_data = symbol_data.set_index("Date") if "Date" in symbol_data.columns else symbol_data
            portfolio[symbol] = symbol_data[price_col] * weight

        portfolio["Portfolio_Value"] = portfolio.sum(axis=1)
        return portfolio

    def compute_metrics(
        self,
        returns: pd.Series,
        risk_free_rate: float = 0.02,
        periods_per_year: int = 252,
    ) -> Dict[str, float]:
        """
        Calculer les KPIs du portefeuille

        Args:
            returns: Série des rendements périodiques
            risk_free_rate: Taux sans risque (défaut: 2% annuel)
            periods_per_year: Jours de trading par an (défaut: 252)

        Returns:
            Dict avec KPIs:
                - total_return: Rendement total
                - annual_return: Rendement annualisé
                - volatility: Volatilité annualisée
                - sharpe_ratio: Ratio de Sharpe
                - max_drawdown: Perte maximale
                - sortino_ratio: Ratio de Sortino

        Example:
            >>> returns = (prices["Close"].pct_change()).dropna()
            >>> kpis = engine.compute_metrics(returns)
            >>> print(kpis["sharpe_ratio"])
        """
        returns = returns.dropna()

        if returns.empty:
            logger.error("Pas de rendements à calculer")
            return {}

        # Rendement total
        total_return = (1 + returns).prod() - 1

        # Rendement annualisé
        n_periods = len(returns)
        annual_return = (1 + total_return) ** (periods_per_year / n_periods) - 1

        # Volatilité annualisée
        volatility = returns.std() * np.sqrt(periods_per_year)

        # Ratio de Sharpe
        excess_return = annual_return - risk_free_rate
        sharpe_ratio = excess_return / volatility if volatility > 0 else 0

        # Drawdown cumulatif
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        # Rendements négatifs (pour Sortino)
        negative_returns = returns[returns < 0]
        downside_vol = negative_returns.std() * np.sqrt(periods_per_year)
        sortino_ratio = excess_return / downside_vol if downside_vol > 0 else 0

        return {
            "total_return": total_return,
            "annual_return": annual_return,
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "sortino_ratio": sortino_ratio,
            "n_periods": n_periods,
        }

    def backtest(
        self,
        prices: pd.DataFrame,
        price_col: str = "Close",
        risk_free_rate: float = 0.02,
    ) -> Dict:
        """
        Backtester une allocation

        Args:
            prices: DataFrame avec colonnes [Date, Symbole, Close]
            price_col: Colonne de prix
            risk_free_rate: Taux sans risque

        Returns:
            Dict avec résultats du backtest
        """
        # Recalculer le portefeuille
        portfolio = self.aggregate_portfolio(price_col=price_col)
        portfolio_prices = portfolio["Portfolio_Value"]

        # Calculer rendements
        returns = portfolio_prices.pct_change().dropna()

        # Calculer KPIs
        metrics = self.compute_metrics(returns, risk_free_rate=risk_free_rate)

        # PnL en valeur absolue
        initial_value = portfolio_prices.iloc[0]
        final_value = portfolio_prices.iloc[-1]
        pnl = final_value - initial_value

        return {
            "metrics": metrics,
            "pnl": pnl,
            "initial_value": initial_value,
            "final_value": final_value,
            "portfolio_value": portfolio_prices,
            "returns": returns,
        }

    @staticmethod
    def calculate_weights_from_values(
        current_values: Dict[str, float],
        normalize: bool = True,
    ) -> Dict[str, float]:
        """
        Calculer les poids à partir des valeurs actuelles

        Args:
            current_values: Dict{symbole: valeur}
            normalize: Normaliser pour sommer à 1.0

        Returns:
            Dict{symbole: poids}

        Example:
            >>> weights = PortfolioEngine.calculate_weights_from_values(
            ...     {"BNP.PA": 10000, "OR.PA": 5000}
            ... )
            >>> # Résultat: {"BNP.PA": 0.667, "OR.PA": 0.333}
        """
        total_value = sum(current_values.values())
        if total_value == 0:
            logger.error("Valeur totale = 0")
            return {}

        weights = {k: v / total_value for k, v in current_values.items()}

        if normalize:
            total_weight = sum(weights.values())
            weights = {k: v / total_weight for k, v in weights.items()}

        return weights

    def rebalance(
        self,
        target_weights: Dict[str, float],
        current_prices: Dict[str, float],
        current_holdings: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Calculer les transactions pour rééquilibrer le portefeuille

        Args:
            target_weights: Poids cibles
            current_prices: Prix actuels {symbole: prix}
            current_holdings: Nombre d'actions actuelles {symbole: qty}

        Returns:
            Transactions à faire {symbole: delta_qty}
        """
        # Valeur totale du portefeuille
        total_value = sum(
            current_holdings.get(s, 0) * current_prices.get(s, 0)
            for s in target_weights.keys()
        )

        if total_value == 0:
            logger.error("Portefeuille vide, impossible de rééquilibrer")
            return {}

        transactions = {}
        for symbol, target_weight in target_weights.items():
            target_value = total_value * target_weight
            current_qty = current_holdings.get(symbol, 0)
            current_value = current_qty * current_prices.get(symbol, 0)
            delta_value = target_value - current_value
            delta_qty = delta_value / current_prices.get(symbol, 1)
            transactions[symbol] = delta_qty

        return transactions
