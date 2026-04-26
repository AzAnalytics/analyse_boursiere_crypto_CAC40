# Architecture Refactorisée - Analyse Boursière & Crypto

## 📐 Vue d'ensemble

Le projet a été entièrement restructuré autour de **4 couches principales** :

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CONFIG & CONSTANTS                                        │
│    └─ Centralisé : settings.py, constants.py               │
├─────────────────────────────────────────────────────────────┤
│ 2. CORE (Logique métier)                                    │
│    ├─ data_fetcher.py      → Fetch stocks/crypto (yfinance)│
│    ├─ data_transformer.py  → Nettoyage & transformation    │
│    └─ portfolio_engine.py  → KPIs & backtesting            │
├─────────────────────────────────────────────────────────────┤
│ 3. DATA_LAYER (Persistence)                                 │
│    ├─ connection.py  → Singleton MongoDB                   │
│    └─ repository.py  → CRUD générique                      │
├─────────────────────────────────────────────────────────────┤
│ 4. APP (Streamlit UI)                                       │
│    ├─ pages/           → Onglets (bourses, crypto, etc.)   │
│    └─ components/      → Composants réutilisables          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Bénéfices de cette architecture

### ✅ Zero Duplication
- **Avant** : `API_bourses/` et `API_crypto/` avec ~90% de code dupliqué
- **Après** : Un seul `core.data_fetcher` générique pour tous les actifs

### ✅ Testabilité
- Chaque module a une seule responsabilité
- Fixtures réutilisables dans `tests/conftest.py`
- 70%+ couverture de tests facile à atteindre

### ✅ Maintenabilité
- Ajouter une nouvelle source (Alpha Vantage) = créer un nouveau wrapper dans `core/`
- Swapper MongoDB pour Parquet = modifier juste `data_layer/`
- Refactoring guidé par les types (`typing`)

### ✅ Scalabilité
- Configuration externalisée (`.env`)
- Logging centralisé (pas de `print()`)
- Error handling robuste

---

## 📦 Structure détaillée

### 1. `config/`
Centre de configuration du projet

```python
# config/settings.py
settings.MONGO_URI              # Connexion MongoDB
settings.YFINANCE_PERIOD        # Période par défaut
settings.LOG_LEVEL              # DEBUG, INFO, WARNING

# config/constants.py
CAC40_STOCKS                    # Dict des symboles actions
CRYPTOCURRENCIES                # Dict des symboles crypto
OHLCV_COLUMNS                   # ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
```

**Usage** :
```python
from config.settings import settings
from config.constants import CAC40_STOCKS, OHLCV_COLUMNS
```

---

### 2. `core/` - Cœur métier (independent de la BD et de l'UI)

#### `data_fetcher.py`
Abstraction générique pour fetch de données

```python
# Stocks
from core.data_fetcher import create_stock_fetcher
fetcher = create_stock_fetcher({"BNP": "BNP.PA", "OR": "OR.PA"})
df = fetcher.fetch_all(period="1y")

# Crypto
from core.data_fetcher import create_crypto_fetcher
fetcher = create_crypto_fetcher({"Bitcoin": "BTC-USD"})
df = fetcher.fetch_single("BTC-USD", period="max")
```

**Avantages** :
- Un seul `DataFetcher` classe pour tous les actifs
- Cleanup automatique (Dividends, Stock Splits, format dates)
- Gestion d'erreurs + logging

#### `data_transformer.py`
Transformer les données brutes

```python
from core.data_transformer import DataTransformer

# Normaliser les dates
df = DataTransformer.normalize_dates(df)

# Valider OHLCV
DataTransformer.validate_ohlcv(df)

# Calculer rendements
df = DataTransformer.calculate_returns(df)
df = DataTransformer.calculate_log_returns(df)

# Rééchantillonner (daily -> weekly)
df_weekly = DataTransformer.resample(df, freq="W")
```

#### `portfolio_engine.py`
Calculs de portefeuille et backtesting

```python
from core.portfolio_engine import PortfolioEngine

weights = {"BNP.PA": 0.5, "OR.PA": 0.5}
engine = PortfolioEngine(df, weights)

# Agrégér le portefeuille
portfolio = engine.aggregate_portfolio()

# Calculer KPIs
kpis = engine.compute_metrics(returns)
# → {
#     "total_return": 0.15,
#     "annual_return": 0.12,
#     "volatility": 0.18,
#     "sharpe_ratio": 0.67,
#     "max_drawdown": -0.08,
#     "sortino_ratio": 0.95,
#   }

# Rééquilibrer
transactions = engine.rebalance(
    target_weights={"BNP.PA": 0.6, "OR.PA": 0.4},
    current_prices={"BNP.PA": 100, "OR.PA": 50},
    current_holdings={"BNP.PA": 10, "OR.PA": 20},
)
```

---

### 3. `data_layer/` - Persistence

#### `connection.py`
Singleton pour la connexion MongoDB

```python
from data_layer.connection import mongo

# Obtenir la collection
collection = mongo.get_collection("stocks_data")

# Fermer la connexion
mongo.close()
```

#### `repository.py`
CRUD générique

```python
from data_layer.repository import get_stocks_repository

repo = get_stocks_repository()

# Insert
repo.insert_many([{"Symbole": "BNP.PA", "Close": 100}, ...])

# Read
df = repo.find_to_dataframe({"Symbole": "BNP.PA"})

# Update
repo.update_many({"Symbole": "BNP.PA"}, {"$set": {"Close": 105}})

# Delete
repo.delete_many({"Symbole": "BNP.PA"})

# Symboles uniques
symbols = repo.get_unique_symbols()
```

---

### 4. `utils/`
Utilitaires partagés

#### `logger.py`
Logging centralisé

```python
from utils.logger import setup_logger

logger = setup_logger(__name__)

logger.info("Message")
logger.warning("Attention")
logger.error("Erreur")
```

**Configuration** :
```env
LOG_LEVEL=INFO
```

---

### 5. `tests/`
Suite de tests

```
tests/
├── conftest.py                  # Fixtures pytest
├── test_data_fetcher.py         # Tests du fetcher
├── test_data_transformer.py     # Tests du transformer
├── test_portfolio_engine.py     # Tests du portfolio engine
└── test_repository.py           # Tests du repository
```

**Lancer les tests** :
```bash
pytest -v                       # Tous les tests
pytest tests/test_data_transformer.py -v
pytest --cov=core              # Coverage
```

---

### 6. `ml/` ✅ (Nouveau - Task #3)
Module de prédiction et forecasting

```
ml/
├── __init__.py               # Package marker
└── forecaster.py             # PriceForecaster avec 12 modèles ML
```

**Classe : PriceForecaster**

```python
from ml.forecaster import PriceForecaster
import pandas as pd

# Créer le forecaster avec une série de prix
prices = pd.Series([100, 102, 101, ...], index=pd.date_range('2024-01-01', periods=500))
forecaster = PriceForecaster(prices)

# 1. Benchmarker tous les modèles
results = forecaster.benchmark_models()
# → DataFrame avec R², RMSE, Temps pour chaque modèle

# 2. Faire une prédiction
forecast = forecaster.forecast(model_name="Random Forest", days=30)
# → DataFrame avec Date et Predicted_Price pour 30 jours

# 3. Prédiction avec intervalle de confiance
forecast_ci = forecaster.forecast_with_confidence(
    model_name="XGBoost",
    days=30,
    confidence_level=0.95
)
# → DataFrame avec Date, Predicted_Price, Upper_Bound, Lower_Bound
```

**Modèles disponibles** :
- Linear Regression, Random Forest, SVR, Gradient Boosting, XGBoost
- Ridge, Lasso, Elastic Net, Decision Tree, KNN, MLP, AdaBoost

---

### 7. `app/` ✅ (Refactorisée - Task #3)
Application Streamlit refactorisée avec 4 pages professionnelles

```
app/
├── main.py                           # Page d'accueil
├── pages/
│   ├── 01_bourses.py                # Analyse actions CAC40
│   ├── 02_crypto.py                 # Analyse cryptomonnaies
│   ├── 03_portfolio.py              # Analyse portefeuille
│   └── 04_ml_forecast.py            # Prédictions avec forecaster.py
└── components/
    └── (à créer : composants réutilisables)
```

**Features** :
- 📈 Fetch dynamique des actions CAC40 via `create_stock_fetcher()`
- 🪙 Fetch des cryptomonnaies via `create_crypto_fetcher()`
- 💼 Agrégation portefeuille avec `PortfolioEngine`
- 🤖 Forecasting avec `PriceForecaster` (12 modèles ML)
- 📊 Visualisations Streamlit
- 🔄 Caching pour performance (`@st.cache_data`)
- 📦 Stockage MongoDB via `get_stocks_repository()` et `get_crypto_repository()`

---

## 🔄 Exemple complet

### Pipeline d'orchestration
```python
from config.constants import CAC40_STOCKS, CRYPTOCURRENCIES
from core.data_fetcher import create_stock_fetcher, create_crypto_fetcher
from core.data_transformer import DataTransformer
from core.portfolio_engine import PortfolioEngine
from data_layer.repository import get_stocks_repository

# 1. Fetcher stocks
stock_fetcher = create_stock_fetcher(CAC40_STOCKS)
df_stocks = stock_fetcher.fetch_all(period="1y")

# 2. Transformer
df_stocks = DataTransformer.normalize_dates(df_stocks)
df_stocks = DataTransformer.drop_duplicates(df_stocks)

# 3. Stocker
repo = get_stocks_repository()
repo.insert_many(df_stocks.to_dict("records"), ignore_duplicates=True)

# 4. Lire et analyser
df = repo.find_to_dataframe({})
df = DataTransformer.set_datetime_index(df)

# 5. Portefeuille
weights = {"BNP.PA": 0.5, "OR.PA": 0.5}
engine = PortfolioEngine(df, weights)
portfolio = engine.aggregate_portfolio()
kpis = engine.compute_metrics(portfolio["Portfolio_Value"].pct_change().dropna())
```

Voir `orchestrate.py` pour l'implémentation complète.

---

## ⚙️ Configuration

### Variables d'environnement (.env)
```env
# MongoDB
MONGO_USER=user
MONGO_PASSWORD=password
MONGO_HOST=cluster0.mongodb.net
MONGO_DBNAME=finance_db

# Logging
LOG_LEVEL=INFO

# Cache
USE_CACHE=True
CACHE_TTL_HOURS=24
```

Charger depuis `.env` :
```bash
export $(cat .env | xargs)
python orchestrate.py
```

---

## 🧪 Ajouter un nouveau test

```python
# tests/test_my_feature.py
import pytest
from core.my_module import MyClass

class TestMyClass:
    def test_something(self, sample_ohlcv_data):
        # Utiliser les fixtures du conftest
        result = MyClass.do_something(sample_ohlcv_data)
        assert result is not None
```

---

## 🚀 Roadmap

### Phase 1 ✅ (Fait)
- [x] Architecture refactorisée
- [x] Config centralisée
- [x] Core modules (fetcher, transformer, engine)
- [x] Data layer (connection, repository)
- [x] Tests + fixtures

### Phase 1.5 ✅ (Task #3 - Refactoring data & ML)
- [x] ML module : PriceForecaster avec 12 modèles
- [x] Refactor Streamlit app (4 pages professionnelles)
- [x] Tests pour forecaster (20+ tests)
- [x] Documentation (TASK3_COMPLETION.md)

### Phase 2 (À faire)
- [ ] GitHub Actions CI/CD
- [ ] Ajouter des API alternatives (Alpha Vantage, CryptoCompare)
- [ ] Interface UX/CSS avancée (Task #4)
- [ ] Composants Streamlit réutilisables

### Phase 3 (Futur)
- [ ] WebSocket streaming (real-time data)
- [ ] ML avancé : ARIMA, Prophet, LSTM
- [ ] Notifications (email, SMS)
- [ ] Historique des décisions (audit log)

---

## 🎓 Conventions

### Noms de variables
- `df` : DataFrame pandas
- `repo` : Repository (MongoDB)
- `fetcher` : DataFetcher
- `engine` : PortfolioEngine
- `logger` : logging.Logger

### Patterns
- **Singleton** : `MongoDBConnection` (une seule instance)
- **Factory** : `create_stock_fetcher()`, `get_stocks_repository()`
- **Repository** : CRUD générique pour MongoDB

### Logging
```python
logger.info(f"✓ {count} records processed")
logger.warning(f"⚠ No data for {symbol}")
logger.error(f"❌ Failed to fetch: {e}")
```

---

## 📚 Ressources

- **pandas** : https://pandas.pydata.org
- **pymongo** : https://pymongo.readthedocs.io
- **yfinance** : https://github.com/ranaroussi/yfinance
- **pytest** : https://docs.pytest.org

---

**Dernière mise à jour** : 2026-04-26  
**Version** : 2.0 (Architecture refactorisée)
