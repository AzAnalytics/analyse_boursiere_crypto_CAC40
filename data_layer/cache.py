"""
Data Caching Layer

Provides lightweight caching using Parquet format.
Eliminates redundant API calls and improves performance 10-100x.
"""

import pandas as pd
import os
from typing import Optional, Tuple
from datetime import datetime, timedelta
import hashlib

from utils.logger import setup_logger

logger = setup_logger(__name__)

# Cache directory
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache_data")

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)


class ParquetCache:
    """
    Lightweight file-based caching using Parquet format.

    Features:
    - 10-100x faster than API calls
    - Self-contained (no Redis/server needed)
    - Automatic TTL-based invalidation
    - Compression support

    Example:
        cache = ParquetCache(ttl_hours=24)

        # Store data
        cache.cache_df("stock_AAPL", df)

        # Load data
        df = cache.load_df("stock_AAPL")

        # Check freshness
        is_fresh = cache.is_fresh("stock_AAPL", max_age=3600)
    """

    def __init__(self, cache_dir: str = CACHE_DIR, ttl_hours: int = 24):
        """
        Initialize cache.

        Args:
            cache_dir: Directory for cache files
            ttl_hours: Time-to-live in hours
        """
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_hours * 3600

        # Ensure directory exists
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"Cache initialized at {cache_dir} (TTL: {ttl_hours}h)")

    def _get_cache_path(self, key: str) -> str:
        """
        Get the cache file path for a key.

        Args:
            key: Cache key

        Returns:
            Full path to cache file
        """
        # Create safe filename from key
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.parquet")

    def _get_metadata_path(self, key: str) -> str:
        """Get metadata file path."""
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.meta")

    def cache_df(
        self,
        key: str,
        df: pd.DataFrame,
        compression: str = "snappy"
    ) -> bool:
        """
        Cache a DataFrame.

        Args:
            key: Cache key (e.g., "stock_AAPL_1y")
            df: DataFrame to cache
            compression: Compression algorithm ("snappy", "gzip", None)

        Returns:
            True if cached successfully
        """
        try:
            path = self._get_cache_path(key)

            # Save DataFrame
            df.to_parquet(path, compression=compression, index=False)

            # Save metadata
            metadata = {
                "key": key,
                "cached_at": datetime.now().isoformat(),
                "rows": len(df),
                "columns": list(df.columns)
            }

            # Write metadata as simple text
            meta_path = self._get_metadata_path(key)
            with open(meta_path, "w") as f:
                f.write(f"{metadata['cached_at']}\n{len(df)}\n{','.join(df.columns)}\n")

            logger.info(f"Cached {key}: {len(df)} rows")
            return True

        except Exception as e:
            logger.error(f"Error caching {key}: {e}")
            return False

    def load_df(self, key: str) -> Optional[pd.DataFrame]:
        """
        Load a cached DataFrame.

        Args:
            key: Cache key

        Returns:
            DataFrame if found and fresh, None otherwise
        """
        try:
            path = self._get_cache_path(key)

            # Check if file exists
            if not os.path.exists(path):
                logger.debug(f"Cache miss for {key}")
                return None

            # Check freshness
            if not self.is_fresh(key):
                logger.debug(f"Cache expired for {key}")
                self.invalidate(key)
                return None

            # Load DataFrame
            df = pd.read_parquet(path)
            logger.info(f"Loaded {key} from cache: {len(df)} rows")
            return df

        except Exception as e:
            logger.error(f"Error loading cache for {key}: {e}")
            return None

    def is_fresh(self, key: str, max_age: Optional[int] = None) -> bool:
        """
        Check if cached data is fresh.

        Args:
            key: Cache key
            max_age: Max age in seconds (uses TTL if None)

        Returns:
            True if data is fresh and not expired
        """
        try:
            path = self._get_cache_path(key)

            if not os.path.exists(path):
                return False

            # Get file modification time
            mtime = os.path.getmtime(path)
            age = datetime.now().timestamp() - mtime

            # Check against TTL
            ttl = max_age or self.ttl_seconds
            is_fresh = age < ttl

            if not is_fresh:
                logger.debug(f"Cache expired for {key}: {age:.0f}s > {ttl}s")

            return is_fresh

        except Exception as e:
            logger.error(f"Error checking freshness for {key}: {e}")
            return False

    def invalidate(self, key: str = None) -> bool:
        """
        Invalidate cache entry or all entries.

        Args:
            key: Cache key to invalidate (None to clear all)

        Returns:
            True if invalidated successfully
        """
        try:
            if key is None:
                # Clear all cache
                for file in os.listdir(self.cache_dir):
                    if file.endswith(".parquet") or file.endswith(".meta"):
                        os.remove(os.path.join(self.cache_dir, file))
                logger.info("Cleared all cache")
            else:
                # Invalidate specific key
                path = self._get_cache_path(key)
                meta_path = self._get_metadata_path(key)

                if os.path.exists(path):
                    os.remove(path)
                if os.path.exists(meta_path):
                    os.remove(meta_path)

                logger.info(f"Invalidated cache for {key}")

            return True

        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return False

    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dict with cache size, file count, etc.
        """
        try:
            total_size = 0
            file_count = 0

            for file in os.listdir(self.cache_dir):
                if file.endswith(".parquet"):
                    file_count += 1
                    path = os.path.join(self.cache_dir, file)
                    total_size += os.path.getsize(path)

            return {
                "cache_dir": self.cache_dir,
                "file_count": file_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "ttl_seconds": self.ttl_seconds
            }

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}


# Global cache instance
_cache = None


def get_cache(ttl_hours: int = 24) -> ParquetCache:
    """Get or create global cache instance."""
    global _cache
    if _cache is None:
        _cache = ParquetCache(ttl_hours=ttl_hours)
    return _cache


def cache_df(key: str, df: pd.DataFrame) -> bool:
    """Cache a DataFrame using global cache."""
    return get_cache().cache_df(key, df)


def load_df(key: str) -> Optional[pd.DataFrame]:
    """Load a cached DataFrame."""
    return get_cache().load_df(key)


def is_fresh(key: str, max_age: int = 3600) -> bool:
    """Check if cache is fresh (default 1 hour)."""
    return get_cache().is_fresh(key, max_age)


def invalidate(key: str = None) -> bool:
    """Invalidate cache."""
    return get_cache().invalidate(key)


def get_stats() -> dict:
    """Get cache statistics."""
    return get_cache().get_cache_stats()
