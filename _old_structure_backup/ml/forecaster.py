"""
Module de prédiction & forecasting - Refactorisé depuis requete_data.py

Utilise différents modèles ML pour prédire les prix futurs
"""
from typing import Dict, Tuple, Optional
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn import metrics
from xgboost import XGBRegressor

from utils.logger import setup_logger

logger = setup_logger(__name__)


class PriceForecaster:
    """
    Forecaster pour prédire les prix futurs

    Utilise différents modèles ML et compare leurs performances
    """

    # Modèles disponibles
    MODELS = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Support Vector Regression": SVR(kernel="rbf"),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
        "XGBoost": XGBRegressor(n_estimators=100, random_state=42, verbosity=0),
        "Ridge Regression": Ridge(alpha=1.0),
        "Lasso Regression": Lasso(alpha=1.0),
        "Elastic Net": ElasticNet(alpha=1.0),
        "Decision Tree": DecisionTreeRegressor(random_state=42),
        "K-Nearest Neighbors": KNeighborsRegressor(n_neighbors=5),
        "Multilayer Perceptron": MLPRegressor(max_iter=1000, random_state=42),
        "AdaBoost": AdaBoostRegressor(n_estimators=100, random_state=42),
    }

    def __init__(self, prices: pd.Series, start_date: Optional[datetime] = None):
        """
        Initialiser le forecaster

        Args:
            prices: Série des prix historiques
            start_date: Date de début pour le training (par défaut: 2 ans avant la fin)
        """
        self.prices = prices.copy()
        self.start_date = start_date or (prices.index[-1] - timedelta(days=365*2))

        # Filtrer les données
        self.training_data = prices[prices.index >= self.start_date].copy()

        if len(self.training_data) < 10:
            logger.warning(f"Peu de données pour le training: {len(self.training_data)}")

        logger.info(f"Forecaster initialisé avec {len(self.training_data)} points")

    def prepare_data(self, test_size: float = 0.2) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Préparer les données pour le training

        Args:
            test_size: Proportion pour le test set

        Returns:
            Tuple[X_train, X_test, y_train, y_test]
        """
        # Convertir les dates en nombre de jours depuis le début
        dates_numeric = np.arange(len(self.training_data)).reshape(-1, 1)
        prices_numeric = self.training_data.values.reshape(-1, 1)

        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            dates_numeric,
            prices_numeric,
            test_size=test_size,
            random_state=42,
        )

        return X_train, X_test, y_train, y_test

    def benchmark_models(self) -> pd.DataFrame:
        """
        Benchmarker tous les modèles disponibles

        Returns:
            DataFrame avec scores R² et temps d'entraînement
        """
        logger.info("Benchmarking des modèles...")
        X_train, X_test, y_train, y_test = self.prepare_data()

        results = []
        for name, model in self.MODELS.items():
            try:
                # Enregistrer le temps
                start_time = time.time()

                # Entraîner
                model.fit(X_train, y_train.ravel())
                training_time = time.time() - start_time

                # Prédire et scorer
                predictions = model.predict(X_test)
                r2_score = metrics.r2_score(y_test, predictions)
                rmse = np.sqrt(metrics.mean_squared_error(y_test, predictions))

                results.append({
                    "Modèle": name,
                    "R² Score": r2_score,
                    "RMSE": rmse,
                    "Temps (s)": training_time,
                })
                logger.info(f"✓ {name}: R²={r2_score:.4f}, RMSE={rmse:.2f}")

            except Exception as e:
                logger.warning(f"Erreur avec {name}: {e}")

        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values(by="R² Score", ascending=False)

        logger.info(f"\nTop 3 modèles :")
        for idx, row in df_results.head(3).iterrows():
            logger.info(f"  {idx+1}. {row['Modèle']}: R²={row['R² Score']:.4f}")

        return df_results

    def forecast(self, model_name: str = "Random Forest", days: int = 30) -> pd.DataFrame:
        """
        Prédire les prix futurs avec un modèle spécifique

        Args:
            model_name: Nom du modèle à utiliser
            days: Nombre de jours à prédire

        Returns:
            DataFrame avec prédictions [Date, Predicted_Price]
        """
        if model_name not in self.MODELS:
            raise ValueError(f"Modèle '{model_name}' non trouvé")

        logger.info(f"Forecasting avec {model_name} pour {days} jours...")

        # Entraîner le modèle sur toutes les données
        X_train, _, y_train, _ = self.prepare_data(test_size=0)
        model = self.MODELS[model_name]
        model.fit(X_train, y_train.ravel())

        # Générer les prédictions futures
        last_index = len(self.training_data) - 1
        future_indices = np.arange(last_index + 1, last_index + 1 + days).reshape(-1, 1)

        predictions = model.predict(future_indices)

        # Créer le DataFrame des résultats
        last_date = self.training_data.index[-1]
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days)

        result_df = pd.DataFrame({
            "Date": future_dates,
            "Predicted_Price": predictions.flatten(),
        })

        logger.info(f"✓ {len(result_df)} prédictions générées")
        logger.info(f"  Prix moyen prédit : ${result_df['Predicted_Price'].mean():.2f}")

        return result_df

    def forecast_with_confidence(
        self,
        model_name: str = "Random Forest",
        days: int = 30,
        confidence_level: float = 0.95,
    ) -> pd.DataFrame:
        """
        Prédire avec intervalle de confiance (Monte Carlo)

        Args:
            model_name: Modèle à utiliser
            days: Jours à prédire
            confidence_level: Niveau de confiance (0.95 = 95%)

        Returns:
            DataFrame avec [Date, Predicted_Price, Upper_Bound, Lower_Bound]
        """
        logger.info(f"Forecasting avec intervalle de confiance ({confidence_level*100:.0f}%)...")

        # Obtenir les prédictions de base
        forecast_df = self.forecast(model_name, days)

        # Calculer l'intervalle de confiance basé sur la volatilité historique
        historical_volatility = self.training_data.pct_change().std()
        last_price = self.training_data.iloc[-1]

        # Standard error
        margin = last_price * historical_volatility * 1.96  # 95% CI

        forecast_df["Upper_Bound"] = forecast_df["Predicted_Price"] + margin
        forecast_df["Lower_Bound"] = forecast_df["Predicted_Price"] - margin

        return forecast_df
