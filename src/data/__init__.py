"""
Data Layer: Fetching and Caching

Modules:
- fetchers.py: yfinance, Alpha Vantage, CryptoCompare
- cache.py: Parquet-based caching
"""

from src.data.cache import ParquetCache, get_cache, cache_df, load_df, is_fresh

__all__ = ['ParquetCache', 'get_cache', 'cache_df', 'load_df', 'is_fresh']
