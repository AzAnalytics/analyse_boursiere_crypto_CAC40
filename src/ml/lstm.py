"""
LSTM Neural Network Forecasting Model

Deep learning for capturing non-linear patterns.
EXCELLENT for crypto but requires GPU for speed.

Advantages:
- Captures non-linear patterns
- Excellent for crypto volatility
- Learns long-term dependencies

Disadvantages:
- Needs GPU for production speed
- Risk of overfitting
- Requires more data
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import warnings

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping
    from sklearn.preprocessing import MinMaxScaler
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

from src.ml.base import BaseForecaster
from utils.logger import setup_logger

logger = setup_logger(__name__)


class LSTMForecaster(BaseForecaster):
    """
    LSTM neural network for time series forecasting.

    EXCELLENT for crypto (captures non-linear patterns).

    Parameters:
    - lookback: Number of previous steps for prediction
    - lstm_units: LSTM layer size
    - dropout_rate: Dropout for regularization
    """

    def __init__(
        self,
        series: pd.Series,
        lookback: int = 60,
        lstm_units: int = 50,
        dropout_rate: float = 0.2
    ):
        """
        Initialize LSTM forecaster.

        Args:
            series: Time series data
            lookback: Previous steps to use
            lstm_units: LSTM layer units
            dropout_rate: Regularization dropout
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("tensorflow required: pip install tensorflow")

        super().__init__(series, "LSTM")
        self.lookback = lookback
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.scaler = MinMaxScaler()
        self.scaled_data = None

    def _prepare_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequences for LSTM."""
        self.scaled_data = self.scaler.fit_transform(self.series.values.reshape(-1, 1))

        X, y = [], []
        for i in range(len(self.scaled_data) - self.lookback):
            X.append(self.scaled_data[i:i + self.lookback])
            y.append(self.scaled_data[i + self.lookback])

        return np.array(X), np.array(y)

    def fit(self, epochs: int = 50, batch_size: int = 32, **kwargs) -> bool:
        """Train LSTM model."""
        if not self.validate_input():
            return False

        try:
            logger.info(f"LSTM: Preparing data (lookback={self.lookback})...")
            X, y = self._prepare_data()

            logger.info(f"LSTM: Training {epochs} epochs...")

            # Build model
            self.model = Sequential([
                LSTM(self.lstm_units, activation='relu', input_shape=(self.lookback, 1)),
                Dropout(self.dropout_rate),
                Dense(self.lstm_units // 2, activation='relu'),
                Dropout(self.dropout_rate),
                Dense(1)
            ])

            self.model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='mse',
                metrics=['mae']
            )

            # Early stopping
            early_stop = EarlyStopping(
                monitor='val_loss',
                patience=5,
                restore_best_weights=True
            )

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                self.model.fit(
                    X, y,
                    epochs=epochs,
                    batch_size=batch_size,
                    validation_split=0.2,
                    callbacks=[early_stop],
                    verbose=0
                )

            self.fitted = True
            logger.info("✓ LSTM training complete")
            return True

        except Exception as e:
            logger.error(f"LSTM fit error: {e}")
            return False

    def forecast(self, steps: int = 30, **kwargs) -> Optional[pd.DataFrame]:
        """Generate forecast with uncertainty."""
        if not self.fitted or self.scaled_data is None:
            logger.error("LSTM: Model not fitted")
            return None

        try:
            # Start with last sequence
            current_sequence = self.scaled_data[-self.lookback:].copy()
            predictions = []

            for _ in range(steps):
                # Predict
                next_pred = self.model.predict(
                    current_sequence.reshape(1, self.lookback, 1),
                    verbose=0
                )[0, 0]

                predictions.append(next_pred)

                # Update sequence
                current_sequence = np.append(current_sequence[1:], [[next_pred]], axis=0)

            # Inverse scale
            predictions_scaled = self.scaler.inverse_transform(
                np.array(predictions).reshape(-1, 1)
            ).flatten()

            # Uncertainty: ±5% of predicted value
            uncertainties = predictions_scaled * 0.05

            # Result
            last_date = self.series.index[-1]
            future_dates = pd.date_range(
                start=last_date + timedelta(days=1),
                periods=steps,
                freq='D'
            )

            result = pd.DataFrame({
                'Date': future_dates,
                'Predicted_Price': predictions_scaled,
                'Lower_Bound': predictions_scaled - uncertainties,
                'Upper_Bound': predictions_scaled + uncertainties,
                'Model': 'LSTM'
            })

            logger.info(f"✓ LSTM: Generated {len(result)} forecasts")
            return result

        except Exception as e:
            logger.error(f"LSTM forecast error: {e}")
            return None

    def get_metrics(self) -> Dict:
        """Get model metrics."""
        if not self.fitted or self.model is None:
            return {}

        try:
            return {
                'LSTM_Units': self.lstm_units,
                'Dropout_Rate': self.dropout_rate,
                'Lookback': self.lookback,
                'Total_Parameters': int(self.model.count_params())
            }
        except Exception as e:
            logger.error(f"LSTM metrics error: {e}")
            return {}
