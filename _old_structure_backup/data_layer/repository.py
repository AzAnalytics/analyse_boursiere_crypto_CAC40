"""
Repository pattern - CRUD générique pour MongoDB
Remplace API_bourses/{insert,read,update,delete}_data.py et équivalents crypto
"""
from typing import Dict, List, Optional, Any
import pandas as pd
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from data_layer.connection import mongo
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MongoRepository:
    """
    Abstraction générique pour les opérations CRUD sur une collection MongoDB

    Example:
        >>> repo = MongoRepository(settings.MONGO_COLLECTION_STOCKS)
        >>> repo.insert_many([{"Symbole": "BNP.PA", "Close": 100}, ...])
        >>> repo.find({"Symbole": "BNP.PA"})
    """

    def __init__(self, collection_name: str, db_name: Optional[str] = None):
        """
        Initialiser le repository

        Args:
            collection_name: Nom de la collection MongoDB
            db_name: Nom de la base (par défaut: settings.MONGO_DBNAME)
        """
        self.collection_name = collection_name
        self.db_name = db_name or settings.MONGO_DBNAME
        self._collection: Optional[Collection] = None

    @property
    def collection(self) -> Collection:
        """Lazy-load la collection"""
        if self._collection is None:
            self._collection = mongo.get_collection(self.collection_name, self.db_name)
        return self._collection

    def insert_many(self, records: List[Dict], ignore_duplicates: bool = False) -> int:
        """
        Insérer plusieurs documents

        Args:
            records: Liste de dictionnaires
            ignore_duplicates: Ignorer les erreurs de clé dupliquée

        Returns:
            Nombre de documents insérés

        Example:
            >>> records = [{"Symbole": "BNP.PA", "Close": 100}, ...]
            >>> repo.insert_many(records)
        """
        if not records:
            logger.warning(f"Pas de records à insérer dans {self.collection_name}")
            return 0

        try:
            result = self.collection.insert_many(records)
            logger.info(f"✓ {len(result.inserted_ids)} documents insérés dans {self.collection_name}")
            return len(result.inserted_ids)
        except DuplicateKeyError as e:
            if ignore_duplicates:
                logger.warning(f"Doublons ignorés: {e}")
                return 0
            else:
                logger.error(f"Erreur de clé dupliquée: {e}")
                raise

    def find(self, query: Dict, limit: Optional[int] = None) -> List[Dict]:
        """
        Chercher des documents

        Args:
            query: Requête MongoDB (ex: {"Symbole": "BNP.PA"})
            limit: Nombre max de résultats

        Returns:
            Liste de documents

        Example:
            >>> repo.find({"Symbole": "BNP.PA"})
        """
        cursor = self.collection.find(query)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    def find_to_dataframe(self, query: Dict, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Chercher et retourner comme DataFrame

        Args:
            query: Requête MongoDB
            limit: Nombre max de résultats

        Returns:
            DataFrame pandas

        Example:
            >>> df = repo.find_to_dataframe({"Symbole": "BNP.PA"})
        """
        records = self.find(query, limit=limit)
        if not records:
            logger.warning(f"Aucun résultat pour query: {query}")
            return pd.DataFrame()

        df = pd.DataFrame(records)
        # Supprimer l'ID MongoDB si présent
        if "_id" in df.columns:
            df = df.drop(columns=["_id"])

        return df

    def update_many(self, query: Dict, update: Dict) -> int:
        """
        Mettre à jour plusieurs documents

        Args:
            query: Requête de sélection
            update: Opérations de mise à jour (ex: {"$set": {"Close": 100}})

        Returns:
            Nombre de documents modifiés

        Example:
            >>> repo.update_many(
            ...     {"Symbole": "BNP.PA"},
            ...     {"$set": {"Close": 100}}
            ... )
        """
        result = self.collection.update_many(query, update)
        logger.info(f"✓ {result.modified_count} documents modifiés dans {self.collection_name}")
        return result.modified_count

    def delete_many(self, query: Dict) -> int:
        """
        Supprimer plusieurs documents

        Args:
            query: Requête de sélection

        Returns:
            Nombre de documents supprimés

        Example:
            >>> repo.delete_many({"Symbole": "BNP.PA"})
        """
        result = self.collection.delete_many(query)
        logger.warning(f"⚠ {result.deleted_count} documents supprimés dans {self.collection_name}")
        return result.deleted_count

    def get_unique_symbols(self) -> List[str]:
        """Obtenir la liste des symboles uniques"""
        return self.collection.distinct("Symbole")

    def count(self, query: Optional[Dict] = None) -> int:
        """Compter les documents"""
        query = query or {}
        return self.collection.count_documents(query)

    def drop(self) -> None:
        """Supprimer toute la collection"""
        self.collection.drop()
        logger.warning(f"⚠ Collection {self.collection_name} supprimée")


# ===== FACTORY FUNCTIONS =====


def get_stocks_repository() -> MongoRepository:
    """Repository pour les données d'actions"""
    return MongoRepository(settings.MONGO_COLLECTION_STOCKS)


def get_crypto_repository() -> MongoRepository:
    """Repository pour les données de crypto"""
    return MongoRepository(settings.MONGO_COLLECTION_CRYPTO)
