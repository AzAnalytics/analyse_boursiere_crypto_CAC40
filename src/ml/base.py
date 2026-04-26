"""
Base Forecaster Abstract Class

Defines the interface all forecasting models must implement.
Ensures consistency across ARIMA, Prophet, LSTM implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict
import pandas as pd
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseForecaster(ABC):
    """
    Abstract base class for all forecasting models.

    Ensures all forecasters implement:
    - fit(): Train the model
    - forecast(): Generate predictions
    - get_metrics(): Return model evaluation metrics
    """

    def __init__(self, series: pd.Series, name: str):
        """
        Initialize forecaster.

        Args:
            series: Time series data (pd.Series with DatetimeIndex)
            name: Model name (for logging)
        """
        self.series = series.copy()
        self.name = name
        self.fitted = False
        self.model = None

    @abstractmethod
    def fit(self, **kwargs) -> bool:
        """
        Train the forecasting model.

        Args:
            **kwargs: Model-specific parameters

        Returns:
            True if training successful, False otherwise
        """
        pass

    @abstractmethod
    def forecast(self, steps: int = 30, **kwargs) -> Optional[pd.DataFrame]:
        """
        Generate forecast.

        Args:
            steps: Number of steps to forecast
            **kwargs: Model-specific parameters

        Returns:
            DataFrame with columns:
            - Date: Future dates
            - Predicted_Price: Forecasted values
            - Lower_Bound: Lower confidence interval
            - Upper_Bound: Upper confidence interval
            - Model: Model name
        """
        pass

    @abstractmethod
    def get_metrics(self) -> Dict:
        """
        Get model evaluation metrics.

        Returns:
            Dictionary with model-specific metrics
            Common keys: AIC, BIC, RMSE, MAE, R2
        """
        pass

    def validate_input(self) -> bool:
        """Validate input series."""
        try:
            if self.series is None or len(self.series) < 10:
                logger.error(f"{self.name}: Series too short (min 10)")
                return False

            if self.series.isnull().sum() > len(self.series) * 0.3:
                logger.error(f"{self.name}: Too many NaN values")
                return False

            return True
        except Exception as e:
            logger.error(f"{self.name} validation error: {e}")
            return False

    def __repr__(self) -> str:
        return f"{self.name}(fitted={self.fitted})"
