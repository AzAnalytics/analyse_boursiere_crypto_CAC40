"""
ARIMA Forecasting Model

AutoARIMA with automatic parameter selection.
Best for stationary/differenced time series with trend.

Limitations:
- Univariate only
- Assumes linear relationship
- Poor for highly volatile crypto
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict
from datetime import datetime, timedelta
import warnings

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
    from pmdarima import auto_arima
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

from src.ml.base import BaseForecaster
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ARIMAForecaster(BaseForecaster):
    """
    ARIMA forecasting model with auto parameter selection.

    Parameters:
    - p: AR order
    - d: Differencing order
    - q: MA order

    Features:
    - Auto parameter selection
    - Stationarity testing
    - Confidence intervals
    """

    def __init__(self, series: pd.Series, seasonal: bool = False):
        """
        Initialize ARIMA forecaster.

        Args:
            series: Time series (pd.Series with DatetimeIndex)
            seasonal: Use SARIMA for seasonal data
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels and pmdarima required")

        super().__init__(series, "ARIMA")
        self.seasonal = seasonal
        self.order = None
        self.seasonal_order = None

    def _test_stationarity(self) -> bool:
        """Test stationarity with ADF test."""
        try:
            result = adfuller(self.series.dropna(), autolag='AIC')
            is_stationary = result[1] < 0.05
            logger.info(f"ARIMA: ADF p-value={result[1]:.4f}, stationary={is_stationary}")
            return is_stationary
        except Exception as e:
            logger.warning(f"ARIMA stationarity test failed: {e}")
            return False

    def fit(self, **kwargs) -> bool:
        """Fit ARIMA model using auto_arima."""
        if not self.validate_input():
            return False

        try:
            logger.info("ARIMA: Fitting model...")

            # Test stationarity
            self._test_stationarity()

            # Auto ARIMA
            if self.seasonal:
                self.model = auto_arima(
                    self.series,
                    seasonal=True,
                    m=12,
                    max_p=5, max_q=5, max_d=2,
                    max_P=2, max_Q=2, max_D=1,
                    stepwise=True,
                    trace=False
                )
            else:
                self.model = auto_arima(
                    self.series,
                    seasonal=False,
                    max_p=5, max_q=5, max_d=2,
                    stepwise=True,
                    trace=False
                )

            self.order = self.model.order
            self.seasonal_order = getattr(self.model, 'seasonal_order', None)
            self.fitted = True

            logger.info(f"✓ ARIMA fit complete. Order: {self.order}")
            return True

        except Exception as e:
            logger.error(f"ARIMA fit error: {e}")
            return False

    def forecast(self, steps: int = 30, **kwargs) -> Optional[pd.DataFrame]:
        """Generate forecast with confidence intervals."""
        if not self.fitted:
            logger.error("ARIMA: Model not fitted")
            return None

        try:
            # Get forecast
            forecast_result = self.model.get_forecast(steps=steps)
            forecast_ci = forecast_result.conf_int(alpha=0.05)

            # Create result
            last_date = self.series.index[-1]
            future_dates = pd.date_range(
                start=last_date + timedelta(days=1),
                periods=steps,
                freq='D'
            )

            result = pd.DataFrame({
                'Date': future_dates,
                'Predicted_Price': forecast_result.predicted_mean.values,
                'Lower_Bound': forecast_ci.iloc[:, 0].values,
                'Upper_Bound': forecast_ci.iloc[:, 1].values,
                'Model': 'ARIMA'
            })

            logger.info(f"✓ ARIMA: Generated {len(result)} forecasts")
            return result

        except Exception as e:
            logger.error(f"ARIMA forecast error: {e}")
            return None

    def get_metrics(self) -> Dict:
        """Get model metrics."""
        if not self.fitted:
            return {}

        try:
            return {
                'AIC': float(self.model.aic),
                'BIC': float(self.model.bic),
                'Order': str(self.order),
                'Seasonal': str(self.seasonal_order) if self.seasonal_order else 'None'
            }
        except Exception as e:
            logger.error(f"ARIMA metrics error: {e}")
            return {}
