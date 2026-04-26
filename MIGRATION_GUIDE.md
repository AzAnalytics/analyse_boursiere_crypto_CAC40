# 🚀 Guide de migration vers la nouvelle architecture

## Bienvenue ! Voici comment utiliser le code refactorisé

### Étape 1 : Installation

```bash
# Cloner ou mettre à jour le repo
git clone https://github.com/AzAnalytics/analyse_boursiere_crypto_CAC40.git
cd analyse_boursiere_crypto_CAC40

# Créer un virtual env
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
pip install -e ".[dev]"  # Optionnel : pour les outils de dev
```

### Étape 2 : Configuration

```bash
# Copier et configurer le fichier .env
cp .env.example .env
# Éditer .env avec tes credentials MongoDB
```

### Étape 3 : Lancer les tests (optionnel mais recommandé)

```bash
# Tous les tests
pytest -v

# Avec coverage
pytest --cov=core --cov-report=html

# Un test spécifique
pytest tests/test_portfolio_engine.py::TestComputeMetrics::test_compute_metrics_positive_returns -v
```

### Étape 4 : Lancer le pipeline d'orchestration

```bash
# Lancer le script principal
python orchestrate.py

# Cela va :
# 1. Fetcher les actions CAC40 (1 an)
# 2. Fetcher les cryptos (1 an)
# 3. Stocker dans MongoDB
# 4. Calculer les KPIs du portefeuille
# 5. Afficher les résultats
```

---

## 📚 Utilisation dans ton code

### Cas d'usage 1 : Fetcher des données

**Avant** :
```python
from API_bourses.insert_data import symboles, collection
import yfinance as yf

for symbole in symboles.values():
    action = yf.Ticker(symbole)
    historique = action.history(period="max")
    # ... nettoyage manuel ...
    collection.insert_many(records)
```

**Après** :
```python
from config.constants import CAC40_STOCKS
from core.data_fetcher import create_stock_fetcher
from data_layer.repository import get_stocks_repository

fetcher = create_stock_fetcher(CAC40_STOCKS)
df = fetcher.fetch_all(period="1y")

repo = get_stocks_repository()
repo.insert_many(df.to_dict("records"), ignore_duplicates=True)
```

### Cas d'usage 2 : Analyser un portefeuille

**Avant** :
```python
from portefeuille import compute_metrics, aggregate_portfolio

prices = pd.read_csv("data.csv")
weights = {"BNP.PA": 0.5, "OR.PA": 0.5}
portfolio = aggregate_portfolio(prices, weights)
kpis = compute_metrics(portfolio["Close"])
```

**Après** :
```python
from core.portfolio_engine import PortfolioEngine
from core.data_transformer import DataTransformer
from data_layer.repository import get_stocks_repository

repo = get_stocks_repository()
df = repo.find_to_dataframe({})
df = DataTransformer.set_datetime_index(df)

weights = {"BNP.PA": 0.5, "OR.PA": 0.5}
engine = PortfolioEngine(df, weights)
portfolio = engine.aggregate_portfolio()
kpis = engine.compute_metrics(portfolio["Portfolio_Value"].pct_change().dropna())

print(f"Sharpe Ratio: {kpis['sharpe_ratio']:.2f}")
```

### Cas d'usage 3 : Transformer les données

**Avant** :
```python
df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y")
df = df.drop_duplicates()
df['Returns'] = df['Close'].pct_change()
```

**Après** :
```python
from core.data_transformer import DataTransformer

df = DataTransformer.normalize_dates(df)
df = DataTransformer.drop_duplicates(df)
df = DataTransformer.calculate_returns(df)
```

---

## 🧪 Tester ton code custom

```python
# tests/test_my_feature.py
import pytest
from config.constants import CAC40_STOCKS
from core.data_fetcher import create_stock_fetcher

class TestMyFeature:
    def test_fetch_stocks(self):
        fetcher = create_stock_fetcher({"BNP": "BNP.PA"})
        df = fetcher.fetch_single("BNP.PA", period="1mo")
        
        assert df is not None
        assert len(df) > 0
        assert "Close" in df.columns

    def test_with_fixture(self, sample_ohlcv_data):
        # Utiliser les fixtures du conftest
        from core.data_transformer import DataTransformer
        
        df = DataTransformer.validate_ohlcv(sample_ohlcv_data)
        assert df is True
```

```bash
pytest tests/test_my_feature.py -v
```

---

## 🔄 Migrer depuis l'ancien code

### Ancien fichier : API_bourses/insert_data.py
→ **Nouveau** : core/data_fetcher.py + data_layer/repository.py

### Ancien fichier : API_bourses/read_data.py
→ **Nouveau** : data_layer/repository.py

### Ancien fichier : portefeuille.py
→ **Nouveau** : core/portfolio_engine.py

### Ancien fichier : data_bourses.py
→ **Nouveau** : app/ (à créer) ou orchestrate.py

---

## 💡 Bonnes pratiques

### 1. Toujours utiliser le logger
```python
from utils.logger import setup_logger

logger = setup_logger(__name__)

# ✅ BON
logger.info("✓ 100 records processed")
logger.warning("⚠ No data for BTC")
logger.error("❌ Failed to connect")

# ❌ MAUVAIS
print("100 records processed")
```

### 2. Centraliser la config
```python
from config.settings import settings
from config.constants import CAC40_STOCKS

# ✅ BON
period = settings.YFINANCE_PERIOD
symbols = CAC40_STOCKS

# ❌ MAUVAIS
period = "max"  # Hardcoded
symbols = {"BNP": "BNP.PA"}  # Hardcoded
```

### 3. Utiliser les type hints
```python
from typing import Dict, Optional
import pandas as pd

# ✅ BON
def my_function(df: pd.DataFrame, symbol: str) -> Optional[dict]:
    pass

# ❌ MAUVAIS
def my_function(df, symbol):
    pass
```

### 4. Écrire des tests
```python
# ✅ BON
def test_fetch_single():
    fetcher = create_stock_fetcher({"TEST": "TEST.PA"})
    result = fetcher.fetch_single("TEST.PA")
    assert result is not None

# ❌ MAUVAIS (pas de tests)
```

---

## 🎯 Structure de dossier (après migration)

```
analyse_boursiere_crypto_CAC40/
├── config/                    # ✅ Configuration
│   ├── settings.py
│   └── constants.py
│
├── core/                      # ✅ Logique métier
│   ├── data_fetcher.py
│   ├── data_transformer.py
│   └── portfolio_engine.py
│
├── data_layer/               # ✅ Persistence
│   ├── connection.py
│   └── repository.py
│
├── utils/                    # ✅ Utilitaires
│   └── logger.py
│
├── app/                      # 🟡 À créer : Streamlit
│   ├── main.py
│   ├── pages/
│   └── components/
│
├── tests/                    # ✅ Tests
│   ├── conftest.py
│   ├── test_data_fetcher.py
│   ├── test_portfolio_engine.py
│   └── ...
│
├── CLAUDE.md                 # 📖 Architecture
├── REFACTORING_SUMMARY.md    # 📖 Résumé
├── REVIEW.md                 # 🔍 Code review
├── MIGRATION_GUIDE.md        # 📖 Ce fichier
├── pyproject.toml            # ⚙️ Config pytest/black
├── Makefile                  # 🔧 Commandes
├── .env.example              # 🔐 Config template
├── requirements.txt          # 📦 Dépendances
└── requirements-dev.txt      # 📦 Dev dependencies
```

---

## ⚠️ Problèmes courants

### Problème 1 : MongoClient ne se connecte pas
```
❌ Erreur: Impossible de se connecter à MongoDB
```

**Solution** :
```bash
# Vérifier que .env est correct
cat .env

# Vérifier la connexion MongoDB
python -c "from data_layer.connection import mongo; print(mongo.get_client())"
```

### Problème 2 : yfinance timeout
```
❌ Erreur: Timeout fetching data
```

**Solution** :
```python
# Augmenter le timeout
df = fetcher.fetch_single("BNP.PA", timeout=60)

# Ou relancer (il y a un retry intégré)
df = fetcher.fetch_all(period="1y")
```

### Problème 3 : Tests échouent
```
❌ FAILED tests/test_data_transformer.py::test_normalize_dates
```

**Solution** :
```bash
# Lancer le test en verbose
pytest tests/test_data_transformer.py::test_normalize_dates -v -s

# Vérifier les fixtures
pytest tests/test_data_transformer.py --fixtures
```

---

## 🚀 Prochaines étapes

### Court terme (1-2 jours)
1. ✅ **FAIT** : Architecture refactorisée
2. ✅ **FAIT** : Tests + documentation
3. 🔲 **TODO** : Créer app Streamlit refactorisée (Task #3 & #4)
4. 🔲 **TODO** : GitHub Actions CI/CD

### Moyen terme (1-2 semaines)
5. 🔲 Ajouter caching (Redis ou Parquet)
6. 🔲 Support pour Alpha Vantage
7. 🔲 Notifications email

### Long terme (1-3 mois)
8. 🔲 ML models (ARIMA, Prophet, LSTM)
9. 🔲 WebSocket real-time streaming
10. 🔲 Dashboard avancé avec Plotly

---

## 📞 Besoin d'aide ?

Voir :
- **CLAUDE.md** : Architecture complète
- **REVIEW.md** : Analyse détaillée du code
- **REFACTORING_SUMMARY.md** : Avant/après
- **Docstrings** : Dans le code même

---

**Bienvenue dans le nouveau codebase ! 🚀**

Bonne chance !
