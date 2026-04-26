# 🎨 Reusable Component Library - Modern Minimalist Design

Comprehensive guide to the new reusable Streamlit components for Task #4.

---

## 📋 Overview

The component library provides **5 modular, composable** UI components that leverage the centralized CSS styling system in `app/styles.py`. All components follow the Modern Minimalist design theme with professional colors, smooth animations, and responsive layouts.

### Key Features:
- ✅ **Zero duplication** - Composable, reusable across all pages
- ✅ **Consistent styling** - All components use `app/styles.py` CSS variables
- ✅ **Type hints** - Full type annotations for IDE support
- ✅ **Responsive** - Mobile-friendly with breakpoints
- ✅ **Animations** - Smooth transitions and hover states

---

## 📦 Components

### 1. **MetricCard** (`app/components/metric_card.py`)

Display KPIs and statistics with optional delta indicators.

#### `metric_card()`
Display a single metric in a styled card.

```python
from app.components import metric_card

metric_card(
    title="Sharpe Ratio",
    value="0.67",
    delta="+0.05",
    delta_color="positive",  # "positive" (green) or "negative" (red)
    icon="📊"
)
```

**Parameters:**
- `title` (str): Card title
- `value` (str): Main metric value
- `delta` (str, optional): Change indicator (e.g., "+2.3%")
- `delta_color` (str): "positive" or "negative"
- `icon` (str, optional): Emoji icon

**Styling:**
- Uses CSS class: `.metric-card`
- Hover animation: translateY(-2px) with enhanced shadow
- Color-coded delta based on delta_color

---

#### `metric_card_grid()`
Display multiple metrics in a responsive grid.

```python
from app.components import metric_card_grid

metric_card_grid({
    "sharpe": {
        "title": "Sharpe Ratio",
        "value": "0.67",
        "delta": "+0.05",
        "delta_color": "positive",
        "icon": "📊"
    },
    "volatility": {
        "title": "Volatility",
        "value": "18.5%",
        "delta": "-1.2%",
        "delta_color": "positive",
        "icon": "📈"
    },
    "return": {
        "title": "Annual Return",
        "value": "12.1%",
        "delta": "+2.3%",
        "delta_color": "positive",
        "icon": "💰"
    }
}, columns=3)
```

**Parameters:**
- `metrics` (dict): Dict of metric_id -> metric_data
- `columns` (int): Number of columns (default: 3)

**Use Cases:**
- Dashboard KPI sections
- Portfolio performance summaries
- Statistics pages

---

### 2. **ChartCard** (`app/components/chart_card.py`)

Styled container for charts with titles and descriptions.

#### `chart_card()`
Display a chart within a styled card.

```python
from app.components import chart_card
import streamlit as st

def draw_price_chart():
    st.line_chart(df.set_index("Date")[["Close"]])

chart_card(
    title="Stock Price History",
    chart_func=draw_price_chart,
    description="Last 12 months",
    help_text="Data from yfinance"
)
```

**Parameters:**
- `title` (str): Card title
- `chart_func` (callable): Function that renders the chart
- `description` (str, optional): Subtitle
- `help_text` (str, optional): Tooltip

**Styling:**
- Uses CSS class: `.stPlotlyChart` container styles
- Border, rounded corners, padding, background
- Title with markdown formatting

---

#### `chart_grid()`
Display multiple charts in a responsive grid.

```python
from app.components import chart_card, chart_grid

def draw_price():
    st.line_chart(df[["Close"]])

def draw_volume():
    st.bar_chart(df[["Volume"]])

chart_grid({
    "price": {
        "title": "Price",
        "func": draw_price,
        "description": "Historical prices"
    },
    "volume": {
        "title": "Volume",
        "func": draw_volume,
        "description": "Trading volume"
    }
}, columns=2)
```

---

### 3. **FilterPanel** (`app/components/filter_panel.py`)

Styled filter controls and parameter selection.

#### `filter_panel()`
Create a collapsible filter panel in the sidebar.

```python
from app.components import filter_panel
import streamlit as st

with filter_panel("Search & Filter", icon="🔍"):
    period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"])
    volatility = st.slider("Min Volatility", 0.0, 1.0, 0.1)
```

---

#### `filter_row()`
Create a row of filter controls in columns.

```python
from app.components import filter_row

filters = filter_row({
    "period": {
        "label": "Period",
        "type": "select",
        "options": ["1mo", "3mo", "6mo", "1y"],
        "value": "1y"
    },
    "min_vol": {
        "label": "Min Volatility",
        "type": "slider",
        "min": 0.0,
        "max": 1.0,
        "value": 0.1
    },
    "search": {
        "label": "Search Symbol",
        "type": "text",
        "value": ""
    }
}, columns=3)

# Access results
period = filters["period"]
min_vol = filters["min_vol"]
search_term = filters["search"]
```

**Supported filter types:**
- `"select"` - Dropdown selector
- `"multiselect"` - Multiple choice selector
- `"slider"` - Numeric slider
- `"text"` - Text input

---

#### `advanced_filters()`
Create an expandable advanced filter section.

```python
from app.components import advanced_filters

filters = advanced_filters("Advanced Options")
if filters:
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    quality = filters.get("data_quality")
```

---

### 4. **DataTable** (`app/components/data_table.py`)

Styled data display with formatting and summary functions.

#### `data_table()`
Display a formatted DataFrame with optional highlighting.

```python
from app.components import data_table
import pandas as pd

data_table(
    df,
    title="Stock Data",
    description="Last 30 days",
    show_index=False,
    format_rules={
        "Close": lambda x: f"${x:.2f}",
        "Volume": lambda x: f"{x:,.0f}",
        "Return": lambda x: f"{x:.2%}"
    }
)
```

**Parameters:**
- `df` (DataFrame): Data to display
- `title` (str, optional): Table title
- `description` (str, optional): Table subtitle
- `show_index` (bool): Show DataFrame index
- `format_rules` (dict): Column -> format_func mapping
- `use_container_width` (bool): Full width (default: True)

---

#### `summary_stats()`
Display summary statistics.

```python
from app.components import summary_stats

summary_stats(df, title="Market Statistics")
```

---

#### `comparison_table()`
Display a comparison table.

```python
from app.components import comparison_table

comparison_table({
    "Model": ["Random Forest", "XGBoost", "Linear Reg"],
    "R² Score": [0.92, 0.89, 0.78],
    "RMSE": [2.1, 2.5, 3.2],
    "Time (ms)": [145, 230, 50]
}, title="Model Comparison")
```

---

#### `key_value_table()`
Display key-value pairs.

```python
from app.components import key_value_table

key_value_table({
    "Total Return": "15.3%",
    "Annual Return": "12.1%",
    "Volatility": "18.5%",
    "Sharpe Ratio": "0.67"
}, title="Portfolio Metrics")
```

---

### 5. **LoadingStates** (`app/components/loading_states.py`)

Loading animations and state messages.

#### `success_message()`
Display a success message.

```python
from app.components import success_message

success_message("Data loaded successfully!", icon="✅")
```

---

#### `error_message()`
Display an error message with optional details.

```python
from app.components import error_message

error_message(
    "Failed to fetch data",
    icon="❌",
    details="Connection timeout after 30s"
)
```

---

#### `loading_skeleton()`
Display skeleton placeholder.

```python
from app.components import loading_skeleton

loading_skeleton(num_lines=3, title="Loading chart...")
```

---

#### `empty_state()`
Display when no data is available.

```python
from app.components import empty_state

empty_state(
    title="No data available",
    message="Try adjusting your filters",
    icon="🔍"
)
```

---

#### `status_badge()`
Display colored status badge.

```python
from app.components import status_badge

status_badge("Active", status_type="success")  # green
status_badge("Pending", status_type="warning")  # orange
status_badge("Error", status_type="error")      # red
```

---

## 🎨 Styling Integration

All components automatically use the centralized CSS system from `app/styles.py`:

```python
from app.styles import inject_custom_css

# Call once per page
inject_custom_css()
```

**Color Palette Used:**
- Primary: `#1f77b4` (Professional blue)
- Secondary: `#ff7f0e` (Accent orange)
- Success: `#2ca02c` (Green)
- Warning: `#d62728` (Red)
- Info: `#17becf` (Cyan)

**Spacing & Sizing:**
- xs: 4px, sm: 8px, md: 16px, lg: 24px, xl: 32px, 2xl: 48px
- Border radius: 4px, 8px, 12px, 16px

---

## 📚 Usage Examples

### Example 1: Dashboard Page
```python
import streamlit as st
from app.styles import inject_custom_css
from app.components import metric_card_grid, chart_card

st.set_page_config(page_title="Dashboard", layout="wide")
inject_custom_css()

st.title("📊 Dashboard")

# KPI Row
metric_card_grid({
    "revenue": {"title": "Revenue", "value": "$245K", ...},
    "growth": {"title": "Growth", "value": "+12%", ...},
    "active": {"title": "Active Users", "value": "1.2K", ...}
}, columns=3)

# Charts
chart_card(title="Sales Trend", chart_func=lambda: st.line_chart(...))
```

### Example 2: Data Analysis Page
```python
from app.components import filter_row, data_table, summary_stats

# Filters
filters = filter_row({
    "period": {"label": "Period", "type": "select", ...},
    "category": {"label": "Category", "type": "multiselect", ...}
})

# Apply filters and show data
filtered_df = df[df["period"] == filters["period"]]

# Display
data_table(filtered_df, title="Data Overview")
summary_stats(filtered_df, title="Statistics")
```

### Example 3: ML Forecast Page
```python
from app.components import (
    filter_row, loading_spinner, success_message, 
    comparison_table, chart_card
)

# Input
model = st.selectbox("Select Model", ["Random Forest", "XGBoost", ...])

if st.button("Forecast"):
    # Show loading
    with st.spinner("Running forecast..."):
        forecast = run_forecast(model)
    
    # Show success
    success_message("Forecast complete!")
    
    # Show results
    comparison_table(benchmark_results, title="Model Comparison")
    chart_card(title="Forecast", chart_func=lambda: st.line_chart(forecast))
```

---

## ✅ Checklist for Integration

- [x] Created component library (metric_card, chart_card, filter_panel, data_table, loading_states)
- [x] Updated app/main.py to use components
- [x] Updated app/pages/01_bourses.py with styled components
- [x] Updated app/pages/02_crypto.py with styled components
- [ ] Update app/pages/03_portfolio.py with styled components
- [ ] Update app/pages/04_ml_forecast.py with styled components
- [ ] Add component showcase page
- [ ] Performance optimization and testing

---

## 🚀 Performance Tips

1. **Caching**: Use `@st.cache_data` decorator
   ```python
   @st.cache_data(ttl=3600)
   def load_data():
       return fetch_expensive_data()
   ```

2. **Lazy Loading**: Load data on-demand
   ```python
   if st.button("Load Data"):
       df = load_data()
       data_table(df)
   ```

3. **Component Reuse**: Build pages from components
   ```python
   # Avoids code duplication
   metric_card_grid(metrics)
   chart_card(title, func)
   ```

---

**Created:** 2026-04-26  
**Status:** ✅ Complete (Component Library + 2 Pages Integrated)  
**Next:** Update remaining pages (portfolio, ML forecast) + Performance optimization
