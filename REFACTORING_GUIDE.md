# Refactoring Guide: Old Structure → New Structure

**Date:** 2026-04-26  
**Status:** Complete refactoring instructions  
**Purpose:** Clear migration path from old to new folder structure

---

## 📋 Overview

This guide explains how the project structure was refactored and provides instructions for moving existing code to the new structure.

---

## 🗺️ Structure Mapping

### Old → New

```
OLD STRUCTURE          →  NEW STRUCTURE
─────────────────────────────────────────────

config/                →  config/
├── settings.py       →  ├── settings.py
├── constants.py      →  └── constants.py
└── __init__.py       →

core/                  →  src/data/ + src/processing/
├── data_fetcher.py   →  src/data/fetchers.py
├── data_transformer  →  src/processing/transformer.py
└── portfolio_engine  →  src/processing/portfolio_engine.py

data_layer/           →  src/data/
├── connection.py     →  (removed - use cache.py)
├── repository.py     →  (removed - use cache.py)
└── cache.py          →  src/data/cache.py

ml/                    →  src/ml/
├── forecaster.py     →  src/ml/base.py (+ arima, prophet, lstm, ensemble)
└── __init__.py       →  src/ml/__init__.py

app/                   →  src/ui/
├── main.py           →  src/ui/main.py
├── components.py     →  src/ui/components.py
└── pages/            →  src/ui/pages/

utils/                 →  src/utils/
├── logger.py         →  src/utils/logger.py
└── __init__.py       →  src/utils/__init__.py

tests/                 →  tests/
├── conftest.py       →  conftest.py
└── test_*.py         →  test_*.py
```

---

## 🔄 Migration Steps

### Step 1: Create New Directory Structure

```bash
mkdir -p src/data
mkdir -p src/processing
mkdir -p src/ml
mkdir -p src/ui/pages
mkdir -p src/utils
mkdir -p docs
```

### Step 2: Move Config Files

```bash
# No changes needed - config/ stays as is
cp config/settings.py config/settings.py
cp config/constants.py config/constants.py
```

### Step 3: Move Data Files

```bash
# Move and rename
cp core/data_fetcher.py src/data/fetchers.py
cp data_layer/cache.py src/data/cache.py

# Create __init__.py
touch src/data/__init__.py
```

**Update imports in `src/data/fetchers.py`**:
```python
# OLD
from data_layer.cache import load_df, cache_df

# NEW
from src.data.cache import load_df, cache_df
```

### Step 4: Move Processing Files

```bash
cp core/data_transformer.py src/processing/transformer.py
cp core/portfolio_engine.py src/processing/portfolio_engine.py

touch src/processing/__init__.py
```

**Update imports**:
```python
# OLD
from data_layer.repository import get_stocks_repository

# NEW
from src.data.cache import load_df, cache_df
```

### Step 5: Move ML Files

```bash
# Phase 3: Create new ML structure
cp ml/base.py src/ml/base.py                    # NEW
cp ml/arima.py src/ml/arima.py                  # NEW
cp ml/prophet.py src/ml/prophet.py              # NEW
cp ml/lstm.py src/ml/lstm.py                    # NEW
cp ml/ensemble.py src/ml/ensemble.py            # NEW

# Update existing forecaster
cp ml/forecaster.py src/ml/forecaster.py        # Old implementation

touch src/ml/__init__.py
```

**Update imports**:
```python
# OLD
from ml.forecaster import PriceForecaster

# NEW
from src.ml import EnsembleForecaster, ProphetForecaster
```

### Step 6: Move UI Files

```bash
cp app/main.py src/ui/main.py
cp app/components.py src/ui/components.py
cp app/pages/* src/ui/pages/

touch src/ui/__init__.py
touch src/ui/pages/__init__.py
```

**Update imports in each page**:
```python
# OLD
from components import metric_card, chart_card

# NEW
from src.ui.components import metric_card, chart_card
```

### Step 7: Move Utils

```bash
cp utils/logger.py src/utils/logger.py
cp utils/validators.py src/utils/validators.py

touch src/utils/__init__.py
```

### Step 8: Move Tests

```bash
# Tests stay mostly the same
cp tests/* tests/
```

**Update test imports**:
```python
# OLD
from core.data_fetcher import create_stock_fetcher

# NEW
from src.data.fetchers import create_stock_fetcher
```

---

## 🔧 Import Updates

### Find All Old Imports

```bash
# Find files with old imports
grep -r "from core\." --include="*.py"
grep -r "from data_layer\." --include="*.py"
grep -r "from ml\." --include="*.py"
grep -r "from app\." --include="*.py"
grep -r "from utils\." --include="*.py"
```

### Update Patterns

```python
# Data Layer
OLD: from data_layer.cache import load_df
NEW: from src.data.cache import load_df

OLD: from data_layer.repository import get_stocks_repository
NEW: from src.data.cache import load_df  # (replaces repository)

# Processing
OLD: from core.data_transformer import DataTransformer
NEW: from src.processing.transformer import DataTransformer

OLD: from core.portfolio_engine import PortfolioEngine
NEW: from src.processing.portfolio_engine import PortfolioEngine

# ML
OLD: from ml.forecaster import PriceForecaster
NEW: from src.ml import EnsembleForecaster, ProphetForecaster

# UI
OLD: from app.components import metric_card
NEW: from src.ui.components import metric_card

OLD: from pages.01_stocks import stock_page
NEW: from src.ui.pages import stock_page
```

---

## ✅ Verification Checklist

After migration, verify:

- [ ] All imports work (`python -c "from src.ml import EnsembleForecaster"`)
- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Linting passes (`pylint src/`)
- [ ] App starts (`streamlit run src/ui/main.py`)
- [ ] No old imports remain in codebase
- [ ] All __init__.py files exist
- [ ] Documentation updated (ARCHITECTURE.md, ML_GUIDE.md)

---

## 🎯 Before vs After

### BEFORE

Importing was confusing:
```python
from core import data_fetcher              # From where?
from data_layer.repository import repo     # What's available?
from ml.forecaster import model            # Which model?
from app.pages.01_stocks import render     # What's the pattern?
```

### AFTER

Imports are clear:
```python
from src.data.fetchers import create_stock_fetcher    # Clearly in data layer
from src.data.cache import load_df, cache_df          # Cache functionality
from src.ml import EnsembleForecaster                  # Specific model
from src.ui.pages import StockPage                     # UI page
```

---

## 🚨 Common Mistakes

### ❌ WRONG: Circular Imports

```python
# src/ml/ensemble.py
from src.ui.components import metric_card  # ❌ Creates circular dependency

# src/ui/components.py
from src.ml import EnsembleForecaster  # ❌ Creates circular dependency
```

### ✅ CORRECT: Uni-directional Dependencies

```
UI Layer  ← (depends on)
  ↓
ML Layer  ← (depends on)
  ↓
Processing Layer  ← (depends on)
  ↓
Data Layer

(No upward dependencies)
```

---

## 📝 Update Checklist

- [ ] Move all files to new locations
- [ ] Update all imports in source files
- [ ] Update all imports in test files
- [ ] Create __init__.py files
- [ ] Remove old empty directories
- [ ] Update PYTHONPATH (if needed)
- [ ] Test imports work correctly
- [ ] Run full test suite
- [ ] Update documentation

---

## 🧹 Cleanup

After migration, remove old directories:

```bash
rm -rf core/                    # Moved to src/
rm -rf data_layer/              # Moved to src/data/
rm -rf ml/                       # Moved to src/ml/
rm -rf app/                      # Moved to src/ui/
```

But keep:
```
config/       # Still there
utils/        # Moved to src/utils/
tests/        # Still there
.github/      # Still there
```

---

## 🔗 See Also

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - New architecture
- [ML_GUIDE.md](docs/ML_GUIDE.md) - ML models
- [CODE_REVIEW_PHASE3.md](CODE_REVIEW_PHASE3.md) - Quality review

---

*Last Updated: 2026-04-26*
