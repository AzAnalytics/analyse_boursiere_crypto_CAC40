"""
Facebook Prophet Forecasting Model

Robust forecasting with automatic seasonality detection.
BEST for crypto + stocks (handles volatility, trend changes, seasonality).

Advantages:
- Automatic seasonality detection
- Robust to missing data
- Handles trend breaks well
- Great for crypto volatility
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict
from datetime import datetime, timedelta
import warnings

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

from src.ml.base import BaseForecaster
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ProphetForecaster(BaseForecaster):
    """
    Facebook Prophet forecasting model.

    RECOMMENDED for this project:
    - Handles trend changes
    - Auto seasonality detection
    - Good for crypto volatility
    - Robust to missing data

    Parameters:
    - daily_seasonality: Include daily patterns
    - yearly_seasonality: Include yearly patterns
    - weekly_seasonality: Include weekly patterns
    """

    def __init__(self, series: pd.Series, daily_seasonality: bool = True):
        """
        Initialize Prophet forecaster.

        Args:
            series: Time series (pd.Series with DatetimeIndex)
            daily_seasonality: Include daily seasonality
        """
        if not PROPHET_AVAILABLE:
            raise ImportError("prophet required: pip install prophet")

        super().__init__(series, "Prophet")

        # Prophet requires 'ds' and 'y' columns
        self.df = pd.DataFrame({
            'ds': series.index,
            'y': series.values
        })
        self.daily_seasonality = daily_seasonality

    def fit(self, **kwargs) -> bool:
        """Fit Prophet model."""
        if not self.validate_input():
            return False

        try:
            logger.info("Prophet: Fitting model...")

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                self.model = Prophet(
                    daily_seasonality=self.daily_seasonality,
                    yearly_seasonality=True,
                    weekly_seasonality=True,
                    interval_width=0.95,
                    changepoint_prior_scale=0.05
                )

                self.model.fit(self.df)

            self.fitted = True
            logger.info("✓ Prophet fit complete")
            return True

        except Exception as e:
            logger.error(f"Prophet fit error: {e}")
            return False

    def forecast(self, steps: int = 30, **kwargs) -> Optional[pd.DataFrame]:
        """Generate forecast with confidence intervals."""
        if not self.fitted:
            logger.error("Prophet: Model not fitted")
            return None

        try:
            # Create future dataframe
            future = self.model.make_future_dataframe(periods=steps)

            # Forecast
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                forecast_df = self.model.predict(future)

            # Extract future forecasts only
            future_forecast = forecast_df[forecast_df['ds'] > self.df['ds'].max()].copy()

            result = pd.DataFrame({
                'Date': future_forecast['ds'].values,
                'Predicted_Price': future_forecast['yhat'].values,
                'Lower_Bound': future_forecast['yhat_lower'].values,
                'Upper_Bound': future_forecast['yhat_upper'].values,
                'Model': 'Prophet'
            })

            logger.info(f"✓ Prophet: Generated {len(result)} forecasts")
            return result

        except Exception as e:
            logger.error(f"Prophet forecast error: {e}")
            return None

    def get_metrics(self) -> Dict:
        """Get model metrics."""
        if not self.fitted:
            return {}

        try:
            # Calculate MAPE on training data
            train_forecast = self.model.predict(self.df[['ds']])
            mape = np.mean(np.abs((self.df['y'] - train_forecast['yhat']) / self.df['y'])) * 100

            return {
                'MAPE_%': round(mape, 2),
                'Daily_Seasonality': self.daily_seasonality,
                'Yearly_Seasonality': True,
                'Weekly_Seasonality': True
            }
        except Exception as e:
            logger.error(f"Prophet metrics error: {e}")
            return {}
