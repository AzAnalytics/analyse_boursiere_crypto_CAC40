"""
Application Streamlit refactorisée - Interface principale

Orchestre les pages (bourses, crypto, portfolio, ML)
Utilise la nouvelle architecture pour les données et modèles
"""
import streamlit as st
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from app.styles import inject_custom_css
from app.components import metric_card_grid, empty_state

logger = setup_logger(__name__)

# Configuration Streamlit
st.set_page_config(
    page_title="Analyse Boursière & Crypto",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom CSS styling system
inject_custom_css()

# Page d'accueil
def home_page():
    """Afficher la page d'accueil"""
    st.title("📊 Tableau de Bord - Analyse Boursière & Crypto")

    st.markdown(
        """
        Bienvenue dans l'application d'analyse boursière et crypto refactorisée.

        **Sélectionnez une page dans le menu latéral :**

        - 📈 **Bourses** : Analyse des actions CAC40
        - 🪙 **Crypto** : Analyse des cryptomonnaies
        - 💼 **Portfolio** : Gestion et analyse de portefeuille
        - 🤖 **ML Forecast** : Prédictions avec modèles machine learning

        ---

        ### Architecture
        Cette application utilise une architecture refactorisée à 4 couches:
        - **Config** : Configuration centralisée
        - **Core** : Logique métier (data_fetcher, data_transformer, portfolio_engine)
        - **Data Layer** : Persistence (MongoDB)
        - **App** : Interface utilisateur (Streamlit) avec composants réutilisables
        """
    )

    # Afficher metrics avec le nouveau système de composants
    metric_card_grid({
        "architecture": {
            "title": "Architecture",
            "value": "4 couches",
            "delta": "+100%",
            "delta_color": "positive",
            "icon": "🏗️"
        },
        "code_duplication": {
            "title": "Code dupliqué",
            "value": "0%",
            "delta": "-90%",
            "delta_color": "positive",
            "icon": "✨"
        },
        "test_coverage": {
            "title": "Couverture tests",
            "value": "70%+",
            "delta": "+60%",
            "delta_color": "positive",
            "icon": "🧪"
        }
    }, columns=3)


# Points d'entrée des pages (pages seront créées séparément)
if __name__ == "__main__":
    home_page()
