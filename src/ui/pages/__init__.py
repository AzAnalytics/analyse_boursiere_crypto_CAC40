"""
Pages Module - Pages individuelles de l'app

- bourses.py: Analyse des actions CAC40
- crypto.py: Analyse des cryptomonnaies
- portfolio.py: Gestion du portefeuille
- ml_forecast.py: Prédictions avec 4 modèles ML
"""

from . import bourses
from . import crypto
from . import portfolio
from . import ml_forecast

__all__ = ['bourses', 'crypto', 'portfolio', 'ml_forecast']
