"""
Gestion centralisée de la connexion MongoDB
Remplace API_bourses/connection.py et API_crypto/connection_crypto.py

Le pattern Singleton garantit une seule connexion active.
"""
from typing import Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionError, ServerSelectionTimeoutError

from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MongoDBConnection:
    """Singleton pour gérer la connexion MongoDB"""

    _instance: Optional["MongoDBConnection"] = None
    _client: Optional[MongoClient] = None

    def __new__(cls) -> "MongoDBConnection":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_client(cls) -> MongoClient:
        """
        Obtenir (ou créer) le client MongoDB

        Returns:
            MongoClient

        Raises:
            ConnectionError: Si impossible de se connecter
        """
        if cls._client is None:
            try:
                logger.info(f"Connexion à MongoDB: {settings.MONGO_HOST}")
                cls._client = MongoClient(
                    settings.MONGO_URI,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                )
                # Test de connexion
                cls._client.admin.command("ping")
                logger.info("✓ Connexion MongoDB réussie")
            except (ConnectionError, ServerSelectionTimeoutError) as e:
                logger.error(f"Impossible de se connecter à MongoDB: {e}")
                raise

        return cls._client

    @classmethod
    def get_database(cls, db_name: Optional[str] = None):
        """Obtenir une base de données"""
        client = cls.get_client()
        db_name = db_name or settings.MONGO_DBNAME
        return client[db_name]

    @classmethod
    def get_collection(cls, collection_name: str, db_name: Optional[str] = None):
        """Obtenir une collection"""
        db = cls.get_database(db_name)
        return db[collection_name]

    @classmethod
    def close(cls) -> None:
        """Fermer la connexion"""
        if cls._client:
            cls._client.close()
            cls._client = None
            logger.info("Connexion MongoDB fermée")


# Instance globale
mongo = MongoDBConnection()
