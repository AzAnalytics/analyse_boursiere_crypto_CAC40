"""
Configuration centralisée du projet analyse_boursiere_crypto_CAC40
Utilise les variables d'environnement pour la sécurité
"""
import os
from typing import Dict
from pathlib import Path


class Settings:
    """Configuration du projet"""

    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"

    # MongoDB
    MONGO_USER = os.environ.get("MONGO_USER", "default_user")
    MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "default_pwd")
    MONGO_HOST = os.environ.get("MONGO_HOST", "cluster0.mongodb.net")
    MONGO_DBNAME = os.environ.get("MONGO_DBNAME", "finance_db")
    MONGO_APP_NAME = os.environ.get("MONGO_APP_NAME", "analyse_boursiere")

    # Collections
    MONGO_COLLECTION_STOCKS = os.environ.get("MONGO_COLLECTION_NAME", "stocks_data")
    MONGO_COLLECTION_CRYPTO = os.environ.get("MONGO_COLLECTION_NAME_CRYPTO", "crypto_data")

    @property
    def MONGO_URI(self) -> str:
        """Construire l'URI de connexion MongoDB"""
        return (
            f"mongodb+srv://{self.MONGO_USER}:{self.MONGO_PASSWORD}"
            f"@{self.MONGO_HOST}/{self.MONGO_DBNAME}"
            f"?retryWrites=true&w=majority&appName={self.MONGO_APP_NAME}&tls=true"
        )

    # API yfinance
    YFINANCE_TIMEOUT = 30
    YFINANCE_PERIOD = "max"  # "max" ou "ytd", "1y", "5y", etc.

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Feature flags
    USE_CACHE = os.environ.get("USE_CACHE", "True").lower() == "true"
    CACHE_TTL_HOURS = int(os.environ.get("CACHE_TTL_HOURS", "24"))


# Instance globale
settings = Settings()
