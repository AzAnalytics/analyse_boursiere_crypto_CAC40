# 🚀 Guide de lancement - Application Streamlit refactorisée

## Installation & Configuration

### 1. Installation des dépendances

```bash
# Créer un virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
pip install streamlit

# Dépendances ML (si pas encore installées)
pip install scikit-learn xgboost
```

### 2. Configuration (.env)

```bash
# Copier le template
cp .env.example .env

# Éditer .env avec vos credentials MongoDB
# MONGO_USER=your_username
# MONGO_PASSWORD=your_password
# MONGO_HOST=your_cluster.mongodb.net
# MONGO_DBNAME=finance_db
```

---

## Lancer l'app

### Méthode 1 : Streamlit CLI (Recommandé)

```bash
streamlit run app/main.py
```

L'app s'ouvrira à `http://localhost:8501`

### Méthode 2 : Avec Makefile

```bash
make streamlit
```

---

## 📄 Pages disponibles

### 1. **Home** (`app/main.py`)
Page d'accueil avec vue d'ensemble de l'architecture

**Accès** : Automatique au lancement

### 2. **📈 Bourses** (`app/pages/01_bourses.py`)
Analyse des actions CAC40

**Fonctionnalités** :
- Sélectionner les actions
- Fetch des données (yfinance)
- Visualisations : prix, rendements
- Stats : moyenne, volatilité, Sharpe Ratio

**Paramètres** :
- Symboles : BNP, OR, ORCP, etc. (voir `config/constants.py`)
- Période : 1mo, 3mo, 6mo, 1y, 2y, 5y, max

### 3. **🪙 Crypto** (`app/pages/02_crypto.py`)
Analyse des cryptomonnaies

**Fonctionnalités** :
- Sélectionner les cryptos
- Fetch des données (yfinance)
- Même visualisations que bourses.py
- Annualization = 365 jours (vs 252 pour stocks)

**Paramètres** :
- Cryptos : Bitcoin, Ethereum, Cardano, etc.
- Période : 1mo à max

### 4. **💼 Portfolio** (`app/pages/03_portfolio.py`)
Analyse de portefeuille

**Fonctionnalités** :
- Configuration du portefeuille
- Sélection des actifs + poids
- Agrégation du portefeuille
- 6 KPIs : Rendement, Volatilité, Sharpe, Sortino, Max Drawdown

**Workflow** :
1. Sélectionner type (Actions, Crypto, Mixte)
2. Choisir les actifs
3. Ajuster les poids (auto-normalisés)
4. Voir la performance et les KPIs

### 5. **🤖 ML Forecast** (`app/pages/04_ml_forecast.py`)
Prédictions avec machine learning

**Fonctionnalités** :
- Sélectionner un actif (stock ou crypto)
- Choisir un modèle ML (12 options)
- Prédire N jours dans le futur
- Intervalle de confiance (Monte Carlo)
- Benchmark de tous les modèles

**Modèles disponibles** :
- Linear Regression
- Random Forest (par défaut)
- Support Vector Regression
- Gradient Boosting
- XGBoost
- Ridge, Lasso, Elastic Net
- Decision Tree
- K-Nearest Neighbors
- Multilayer Perceptron
- AdaBoost

**Workflow** :
1. Charger données historiques
2. Sélectionner modèle
3. Définir horizon (jours)
4. Voir prédictions + intervalle de confiance

---

## 🔄 Data Flow

```
┌─────────────────────────────────────────┐
│ App Streamlit (pages/*.py)              │
│  - Sélection UI (sidebar)               │
│  - Visualisations                       │
│  - Caching (@st.cache_data)             │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│ Core modules                             │
│  - data_fetcher.py   (fetch yfinance)   │
│  - data_transformer.py (clean data)     │
│  - portfolio_engine.py (KPIs)           │
│  - forecaster.py (ML predictions)       │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│ Data Layer                               │
│  - connection.py (MongoDB singleton)    │
│  - repository.py (CRUD)                 │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│ MongoDB                                  │
│  - Collections: stocks_data, crypto_data│
└─────────────────────────────────────────┘
```

---

## 🧪 Tests

### Lancer les tests

```bash
# Tous les tests
pytest -v

# Tests du forecaster
pytest tests/test_forecaster.py -v

# Avec coverage
pytest --cov=core --cov-report=html
```

### Fixtures disponibles

- `sample_ohlcv_data` : Données OHLCV
- `sample_multi_asset_data` : Plusieurs actifs
- `sample_returns` : Série de rendements
- `sample_portfolio_weights` : Poids de portefeuille
- `sample_price_series` : Série de prix (pour forecaster)

---

## 🔧 Troubleshooting

### Erreur : "Module not found: streamlit"
```bash
pip install streamlit
```

### Erreur : "MongoDB connection failed"
```bash
# Vérifier le .env
cat .env

# Tester la connexion
python -c "from data_layer.connection import mongo; print(mongo.get_client())"
```

### Erreur : "No data found for symbol"
- Vérifier que les données sont chargées dans MongoDB
- Aller sur la page Bourses/Crypto et cliquer "Charger données"
- Attendre quelques secondes (yfinance peut être lent)

### Erreur : "sklearn not found"
```bash
pip install scikit-learn xgboost
```

---

## 💡 Conseils

### Performance
- Utiliser le caching (`@st.cache_data`) pour éviter les re-calculs
- Le premier fetch prend du temps (yfinance)
- Les données sont cachées 3600s (1 heure)

### Utilisation
- Commencer par la page Bourses pour charger les données
- Puis aller sur Portfolio pour analyser
- ML Forecast fonctionne mieux avec 2+ ans de données

### Optimisation
- Pour les cryptos, augmenter la période (3y recommandé)
- Pour le forecasting, choisir Random Forest ou XGBoost
- Évaluer plusieurs modèles avec le Benchmark

---

## 📚 Documentation

Voir aussi :
- **CLAUDE.md** : Architecture complète
- **TASK3_COMPLETION.md** : Détail Task #3
- **MIGRATION_GUIDE.md** : Usage des modules
- **Docstrings** : Dans le code même

---

## 🎯 Prochaines étapes

1. ✅ Tester les 4 pages Streamlit
2. ✅ Charger des données réelles
3. 🟡 Déployer l'app (Heroku, Streamlit Cloud)
4. 🟡 Ajouter CSS/UX avancé (Task #4)
5. 🟡 Ajouter API alternatives (Alpha Vantage)

---

**Bonne chance ! 🚀**
