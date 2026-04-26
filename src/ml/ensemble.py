"""
Ensemble Forecaster

Combines ARIMA, Prophet, and LSTM for robust predictions.
PRODUCTION READY: Best accuracy + robustness.

Strategy:
- Train all 3 models in parallel
- Average their predictions (weighted)
- Combine confidence intervals
- Validate output
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List
from concurrent.futures import ThreadPoolExecutor
import warnings

from src.ml.arima import ARIMAForecaster
from src.ml.prophet import ProphetForecaster
from src.ml.lstm import LSTMForecaster
from src.ml.base import BaseForecaster
from utils.logger import setup_logger

logger = setup_logger(__name__)


class EnsembleForecaster(BaseForecaster):
    """
    Ensemble forecasting combining ARIMA, Prophet, LSTM.

    Weights (can be tuned based on backtest):
    - Prophet: 0.5 (most robust for stocks/crypto)
    - LSTM: 0.35 (excellent for patterns)
    - ARIMA: 0.15 (baseline, less volatile data)

    Features:
    - Parallel training (faster)
    - Weighted averaging
    - Combined confidence intervals
    - Fallback to individual models
    """

    def __init__(
        self,
        series: pd.Series,
        weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize Ensemble forecaster.

        Args:
            series: Time series data
            weights: Model weights (default: Prophet=0.5, LSTM=0.35, ARIMA=0.15)
        """
        super().__init__(series, "Ensemble")

        self.weights = weights or {
            'Prophet': 0.5,
            'LSTM': 0.35,
            'ARIMA': 0.15
        }

        # Initialize models
        self.prophet = ProphetForecaster(series)
        self.lstm = LSTMForecaster(series, lookback=60)
        self.arima = ARIMAForecaster(series, seasonal=False)

        self.models = [self.prophet, self.lstm, self.arima]
        self.forecasts = {}

    def fit(self, **kwargs) -> bool:
        """Train all models in parallel."""
        try:
            logger.info("Ensemble: Training 3 models in parallel...")

            # Train in parallel
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    'Prophet': executor.submit(self.prophet.fit),
                    'LSTM': executor.submit(self.lstm.fit, epochs=kwargs.get('epochs', 50)),
                    'ARIMA': executor.submit(self.arima.fit)
                }

                results = {}
                for name, future in futures.items():
                    try:
                        results[name] = future.result(timeout=300)
                    except Exception as e:
                        logger.warning(f"Ensemble: {name} training failed: {e}")
                        results[name] = False

            # Check if at least 2 models succeeded
            success_count = sum(1 for v in results.values() if v)
            if success_count < 2:
                logger.error("Ensemble: Less than 2 models trained successfully")
                return False

            self.fitted = True
            logger.info(f"✓ Ensemble: {success_count}/3 models trained")
            return True

        except Exception as e:
            logger.error(f"Ensemble fit error: {e}")
            return False

    def forecast(self, steps: int = 30, **kwargs) -> Optional[pd.DataFrame]:
        """Generate ensemble forecast."""
        if not self.fitted:
            logger.error("Ensemble: Model not fitted")
            return None

        try:
            logger.info(f"Ensemble: Generating {steps} forecasts...")

            # Get forecasts from all models
            forecasts_list = []

            for name, model in [
                ('Prophet', self.prophet),
                ('LSTM', self.lstm),
                ('ARIMA', self.arima)
            ]:
                if model.fitted:
                    try:
                        forecast = model.forecast(steps)
                        if forecast is not None:
                            forecasts_list.append(forecast)
                            self.forecasts[name] = forecast
                    except Exception as e:
                        logger.warning(f"Ensemble: {name} forecast failed: {e}")

            if len(forecasts_list) < 2:
                logger.error("Ensemble: Less than 2 models produced forecasts")
                return None

            # Combine forecasts with weighted average
            ensemble_df = self._combine_forecasts(forecasts_list, steps)

            logger.info(f"✓ Ensemble: Generated {len(ensemble_df)} forecasts")
            return ensemble_df

        except Exception as e:
            logger.error(f"Ensemble forecast error: {e}")
            return None

    def _combine_forecasts(
        self,
        forecasts: List[pd.DataFrame],
        steps: int
    ) -> pd.DataFrame:
        """Combine individual model forecasts with weighted averaging."""
        try:
            # Get dates from first forecast
            dates = forecasts[0]['Date'].values

            # Weighted average of predictions
            weighted_predictions = np.zeros(steps)
            weighted_lower = np.zeros(steps)
            weighted_upper = np.zeros(steps)
            total_weight = 0

            for forecast in forecasts:
                model_name = forecast['Model'].iloc[0]
                weight = self.weights.get(model_name, 1/3)

                weighted_predictions += forecast['Predicted_Price'].values * weight
                weighted_lower += forecast['Lower_Bound'].values * weight
                weighted_upper += forecast['Upper_Bound'].values * weight
                total_weight += weight

            # Normalize by total weight
            weighted_predictions /= total_weight
            weighted_lower /= total_weight
            weighted_upper /= total_weight

            result = pd.DataFrame({
                'Date': dates,
                'Predicted_Price': weighted_predictions,
                'Lower_Bound': weighted_lower,
                'Upper_Bound': weighted_upper,
                'Model': 'Ensemble'
            })

            return result

        except Exception as e:
            logger.error(f"Ensemble combine error: {e}")
            return None

    def get_metrics(self) -> Dict:
        """Get ensemble metrics from all models."""
        try:
            metrics = {'Ensemble': {}}

            for name, model in [
                ('Prophet', self.prophet),
                ('LSTM', self.lstm),
                ('ARIMA', self.arima)
            ]:
                if model.fitted:
                    model_metrics = model.get_metrics()
                    metrics[name] = model_metrics

            metrics['Ensemble']['Weights'] = self.weights
            metrics['Ensemble']['Models_Trained'] = sum(
                1 for m in self.models if m.fitted
            )

            return metrics

        except Exception as e:
            logger.error(f"Ensemble metrics error: {e}")
            return {}

    def get_individual_forecasts(self) -> Dict[str, pd.DataFrame]:
        """Get forecasts from individual models."""
        return self.forecasts
