"""
Setup centralisé du logging pour tout le projet
Remplace les print() par des logs structurés
"""
import logging
import sys
from config.settings import settings


def setup_logger(name: str, level: str = None) -> logging.Logger:
    """
    Créer et configurer un logger pour un module

    Args:
        name: Nom du module (__name__)
        level: Niveau de log (DEBUG, INFO, WARNING, ERROR)

    Returns:
        logging.Logger: Logger configuré

    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Mon message")
    """
    if level is None:
        level = settings.LOG_LEVEL

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))

    # Éviter les doublons si le logger est déjà configuré
    if logger.handlers:
        return logger

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level))

    # Formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


# Logger par défaut
logger = setup_logger("analyse_boursiere")
