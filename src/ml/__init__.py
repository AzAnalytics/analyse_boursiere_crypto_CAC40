"""
ML Module: Forecasting Models

Available Models:
- ARIMAForecaster: Good for stocks, weak for crypto
- ProphetForecaster: RECOMMENDED - robust for all
- LSTMForecaster: Excellent for crypto patterns
- EnsembleForecaster: PRODUCTION - combines all 3

Usage:
    from src.ml import EnsembleForecaster

    forecaster = EnsembleForecaster(price_series)
    forecaster.fit(epochs=50)
    forecast_df = forecaster.forecast(steps=30)
"""

from src.ml.base import BaseForecaster
from src.ml.arima import ARIMAForecaster
from src.ml.prophet import ProphetForecaster
from src.ml.lstm import LSTMForecaster
from src.ml.ensemble import EnsembleForecaster

__all__ = [
    'BaseForecaster',
    'ARIMAForecaster',
    'ProphetForecaster',
    'LSTMForecaster',
    'EnsembleForecaster'
]
