# Analyse Boursière & Crypto – CAC40

Outils Python pour **récupérer, analyser et tester** des données de marchés (actions/indices CAC 40 et cryptomonnaies). Le projet propose des modules pour interroger des API (`yfinance`, endpoints crypto), transformer les données, calculer des indicateurs de performance de portefeuille et exécuter des tests automatisés via CI.

---

##  Fonctionnalités

- Récupération de données **marchés actions / indices** via `yfinance`
- Récupération de données **cryptomonnaies**
- Préparation et nettoyage des données : structuration des colonnes OHLCV, index temporel, gestion des trouées
- Calculs de portefeuille : rendement, volatilité, PnL, agrégations multi-actifs
- Tests : unitaires, non-régression, test Streamlit
- CI automatisée via GitHub Actions (`.github/workflows/`)

---

##  Structure du dépôt

```
.
├─ API_bourses/           # Récupération & manipulation données actions/indices
├─ API_crypto/            # Récupération & manipulation données crypto
├─ data/                  # (optionnel) jeux de données locaux
├─ data_bourses.py        # Pipeline fetch → clean → transform
├─ yfinance_structure.py  # Abstraction autour de yfinance
├─ portefeuille.py        # Calculs de portefeuille (KPIs, agrégations)
├─ requete_data.py        # Appels "bas niveau" vers les API
├─ main.py                # Orchestration de bout en bout
├─ test_*.py              # Tests (unitaires, régression, Streamlit)
└─ .github/workflows/     # Workflows CI (tests, lint, etc.)
```

---

##  Prérequis

- Python 3.10 ou supérieur
- Dépendances listées dans `requirements.txt`

---

##  Installation

```bash
git clone https://github.com/AzAnalytics/analyse_boursiere_crypto_CAC40.git
cd analyse_boursiere_crypto_CAC40
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

---

##  Configuration (facultative)

Si tu ajoutes d’autres sources (ex : Alpha Vantage), tu peux utiliser un fichier `.env` :

```env
API_KEY=ta_clé_ici
```

Et charger la variable d’environnement dans les modules concernés.

---

## ▶ Utilisation

### 1) Pipeline actions / indices

```bash
python data_bourses.py   --tickers "^FCHI,BNP.PA,OR.PA,MC.PA"   --start 2018-01-01   --end 2025-08-20   --interval 1d   --out data/cac40.parquet
```

- `--tickers` : liste d’actifs séparée par virgules (`^FCHI`, `BNP.PA`, etc.)
- `--start`, `--end` : dates de début et fin
- `--interval` : `1d`, `1wk`, `1mo`, etc.
- `--out` : fichier de sortie (`.csv` ou `.parquet`)

Le module `yfinance_structure.py` standardise l'appel à `yfinance` (colonnes OHLCV, index datetime, etc.)

### 2) Pipeline cryptomonnaies

```bash
python -m API_crypto.fetch   --symbols "BTC-USD,ETH-USD,SOL-USD"   --start 2020-01-01   --interval 1d   --out data/crypto.parquet
```

Le dossier `API_crypto/` contient les fonctions de récupération et transformation des données crypto.

### 3) Calculs de portefeuille

```python
from pathlib import Path
import pandas as pd
from portefeuille import compute_metrics, aggregate_portfolio

prices = pd.read_parquet(Path("data/cac40.parquet"))
weights = {"BNP.PA": 0.25, "OR.PA": 0.25, "MC.PA": 0.25, "^FCHI": 0.25}

portfolio = aggregate_portfolio(prices, weights, price_col="Close")
kpis = compute_metrics(portfolio["Close"])

print(kpis)  # Affiche rendement, volatilité, Sharpe, max drawdown, etc.
```

### 4) Lancement complet avec `main.py`

```bash
python main.py
```

Ce script orchestre un flux complet (collecte, calculs, export). Les paramètres peuvent être codés dans le script ou lus depuis un fichier de configuration.

---

##  Interface Streamlit (optionnelle)

Un fichier de test `test_streamlit.py` montre que l’app est fonctionnelle. Pour lancer :

```bash
streamlit run app.py
```

---

##  Tests

- `pytest` gère les tests unitaires, non-régression et Streamlit
- Commande pour lancer tous les tests :

```bash
pytest -q
```

- Les workflows CI (`.github/workflows/`) exécutent les tests à chaque push ou PR

---

##  Modèle de données & conventions

- Index temporel sur Date ou Datetime
- Colonnes : `Open`, `High`, `Low`, `Close`, `Adj Close`, `Volume`
- Données multi-actifs : colonne `Ticker` ou multi-index (`Ticker × Champ`)
- Fréquences supportées : `1d` (par défaut), autres selon `yfinance`

---

##  Exemples rapides (recipes)

### A) CAC 40 complet

```bash
python data_bourses.py   --tickers "^FCHI,ACA.PA,AI.PA,AIR.PA,ALO.PA,ORA.PA,BNP.PA,BN.PA,BVI.PA,CAPR.PA,CS.PA,CA.PA,ENGI.PA,EL.PA,ERF.PA,MC.PA,ML.PA,OR.PA,PUB.PA,RMS.PA,SAF.PA,SGO.PA,SU.PA,SW.PA,STM.PA,TEP.PA,TTE.PA,URW.AS,VIE.PA,VIV.PA"   --start 2018-01-01   --interval 1d   --out data/cac40.parquet
```

### B) Crypto principale

```bash
python -m API_crypto.fetch   --symbols "BTC-USD,ETH-USD,SOL-USD"   --start 2020-01-01   --interval 1d   --out data/crypto.parquet
```

### C) Portefeuille 60/40 actions / indice

```python
weights = {"^FCHI": 0.40, "MC.PA": 0.20, "OR.PA": 0.20, "BNP.PA": 0.20}
```

---

##  Bonnes pratiques & optimisation

- Utilise du cache local (`parquet`/`csv`) pour éviter les téléchargements inutiles
- Aligne les séries temporelles et fais du resampling avant agrégations portefeuille
- Gère les jours fériés (fermeture des marchés) et les différences de fuseau jour crypto vs bourse
- Ajoute des tests non-régression pour verrouiller la structure des sorties

---

##  Exports & intégration

- Formats d’export : **Parquet** recommandé, **CSV** possible
- Prêt pour BI (Power BI, Tableau) ou notebooks Data Science

---

##  Qualité & CI

- Linting et tests automatisés via GitHub Actions
- Travail structuré dès la mise en place des tests

---

##  Roadmap (idées d’évolution)

- Intégrer d'autres APIs (Alpha Vantage, Polygon, CryptoCompare…)
- KPIs avancés : bêta, tracking error, VaR / CVaR, etc.
- Ajout de facteurs d’investissement (momentum, value, quality)
- Backtesting/backtest d’allocations avec rééquilibrage, contraintes

---
