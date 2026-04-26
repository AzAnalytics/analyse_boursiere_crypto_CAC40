"""
Alpha Vantage Data Fetcher

Alternative API source for stock and cryptocurrency data.
Free tier: 5 requests/minute, 100 requests/day
Requires API key from: https://www.alphavantage.co/
"""

import pandas as pd
import requests
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import time

from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Alpha Vantage API configuration
AV_BASE_URL = "https://www.alphavantage.co/query"
AV_TIMEOUT = 10


class AlphaVantageFetcher:
    """
    Fetch stock and cryptocurrency data from Alpha Vantage API.

    Features:
    - Stock daily/intraday/weekly/monthly data
    - Forex data
    - Cryptocurrency data
    - Rate limiting (5 requests/minute, 100/day)

    Example:
        fetcher = AlphaVantageFetcher(api_key="YOUR_KEY")
        df = fetcher.fetch_stock("AAPL", interval="daily")
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Alpha Vantage fetcher.

        Args:
            api_key: Alpha Vantage API key (gets from settings if not provided)
        """
        self.api_key = api_key or settings.get("ALPHA_VANTAGE_KEY")
        if not self.api_key:
            logger.warning("No Alpha Vantage API key configured")

        self.last_request_time = 0
        self.request_count = 0
        self.session = requests.Session()

    def _rate_limit(self):
        """Respect Alpha Vantage rate limits (5 requests/minute)."""
        elapsed = time.time() - self.last_request_time
        if elapsed < 12:  # 12 seconds = 5 requests/minute
            time.sleep(12 - elapsed)
        self.last_request_time = time.time()

    def _fetch_json(self, params: Dict) -> Optional[Dict]:
        """
        Fetch JSON from Alpha Vantage API.

        Args:
            params: Query parameters

        Returns:
            JSON response or None if error
        """
        try:
            self._rate_limit()

            params["apikey"] = self.api_key

            response = self.session.get(
                AV_BASE_URL,
                params=params,
                timeout=AV_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if "Error Message" in data:
                logger.error(f"Alpha Vantage Error: {data['Error Message']}")
                return None

            if "Note" in data:
                logger.warning(f"Alpha Vantage Rate Limit: {data['Note']}")
                return None

            return data

        except requests.RequestException as e:
            logger.error(f"Request error fetching from Alpha Vantage: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing Alpha Vantage response: {e}")
            return None

    def fetch_stock(
        self,
        symbol: str,
        interval: str = "daily"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch stock data.

        Args:
            symbol: Stock symbol (e.g., "AAPL", "MSFT")
            interval: "daily", "weekly", or "monthly"

        Returns:
            DataFrame with OHLCV data or None if error
        """
        logger.info(f"Fetching {symbol} ({interval}) from Alpha Vantage...")

        # Map interval to function
        function_map = {
            "daily": "TIME_SERIES_DAILY",
            "weekly": "TIME_SERIES_WEEKLY",
            "monthly": "TIME_SERIES_MONTHLY"
        }

        function = function_map.get(interval, "TIME_SERIES_DAILY")

        try:
            data = self._fetch_json({
                "function": function,
                "symbol": symbol,
                "outputsize": "full"  # Get full history
            })

            if not data:
                return None

            # Find the time series key (varies by function)
            ts_key = None
            for key in data.keys():
                if "Time Series" in key or "Time Series (5min)" in key:
                    ts_key = key
                    break

            if not ts_key:
                logger.error(f"No time series data found for {symbol}")
                return None

            # Parse time series data
            ts_data = data[ts_key]
            records = []

            for date_str, ohlc in ts_data.items():
                records.append({
                    "Date": date_str,
                    "Open": float(ohlc.get("1. open", 0)),
                    "High": float(ohlc.get("2. high", 0)),
                    "Low": float(ohlc.get("3. low", 0)),
                    "Close": float(ohlc.get("4. close", 0)),
                    "Volume": int(ohlc.get("5. volume", 0)),
                    "Symbole": symbol,
                    "Source": "Alpha Vantage"
                })

            df = pd.DataFrame(records)
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")

            logger.info(f"✓ Fetched {len(df)} records for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return None

    def fetch_intraday(
        self,
        symbol: str,
        interval: str = "5min"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch intraday stock data.

        Args:
            symbol: Stock symbol
            interval: "1min", "5min", "15min", "30min", "60min"

        Returns:
            DataFrame with intraday OHLCV data
        """
        logger.info(f"Fetching {symbol} (intraday, {interval}) from Alpha Vantage...")

        try:
            data = self._fetch_json({
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": interval,
                "outputsize": "full"
            })

            if not data:
                return None

            # Find time series key
            ts_key = None
            for key in data.keys():
                if "Time Series" in key:
                    ts_key = key
                    break

            if not ts_key:
                logger.error(f"No intraday data found for {symbol}")
                return None

            ts_data = data[ts_key]
            records = []

            for time_str, ohlc in ts_data.items():
                records.append({
                    "DateTime": time_str,
                    "Open": float(ohlc.get("1. open", 0)),
                    "High": float(ohlc.get("2. high", 0)),
                    "Low": float(ohlc.get("3. low", 0)),
                    "Close": float(ohlc.get("4. close", 0)),
                    "Volume": int(ohlc.get("5. volume", 0)),
                    "Symbole": symbol,
                    "Source": "Alpha Vantage",
                    "Interval": interval
                })

            df = pd.DataFrame(records)
            df["DateTime"] = pd.to_datetime(df["DateTime"])
            df = df.sort_values("DateTime")

            logger.info(f"✓ Fetched {len(df)} intraday records for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching intraday data for {symbol}: {e}")
            return None

    def fetch_forex(
        self,
        from_currency: str,
        to_currency: str,
        interval: str = "daily"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch forex data.

        Args:
            from_currency: Currency code (e.g., "EUR")
            to_currency: Currency code (e.g., "USD")
            interval: "daily", "weekly", "monthly"

        Returns:
            DataFrame with forex OHLCV data
        """
        logger.info(f"Fetching {from_currency}/{to_currency} ({interval}) from Alpha Vantage...")

        function_map = {
            "daily": "FX_DAILY",
            "weekly": "FX_WEEKLY",
            "monthly": "FX_MONTHLY"
        }

        function = function_map.get(interval, "FX_DAILY")

        try:
            data = self._fetch_json({
                "function": function,
                "from_symbol": from_currency,
                "to_symbol": to_currency,
                "outputsize": "full"
            })

            if not data:
                return None

            ts_key = None
            for key in data.keys():
                if "Time Series" in key:
                    ts_key = key
                    break

            if not ts_key:
                logger.error(f"No forex data found for {from_currency}/{to_currency}")
                return None

            ts_data = data[ts_key]
            records = []

            for date_str, ohlc in ts_data.items():
                records.append({
                    "Date": date_str,
                    "Open": float(ohlc.get("1. open", 0)),
                    "High": float(ohlc.get("2. high", 0)),
                    "Low": float(ohlc.get("3. low", 0)),
                    "Close": float(ohlc.get("4. close", 0)),
                    "Symbole": f"{from_currency}/{to_currency}",
                    "Source": "Alpha Vantage"
                })

            df = pd.DataFrame(records)
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")

            logger.info(f"✓ Fetched {len(df)} forex records for {from_currency}/{to_currency}")
            return df

        except Exception as e:
            logger.error(f"Error fetching forex data: {e}")
            return None

    def fetch_crypto(
        self,
        symbol: str,
        market: str = "USD"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch cryptocurrency daily data.

        Args:
            symbol: Crypto symbol (e.g., "BTC", "ETH")
            market: Market currency (e.g., "USD")

        Returns:
            DataFrame with crypto OHLCV data
        """
        logger.info(f"Fetching {symbol}/{market} from Alpha Vantage...")

        try:
            data = self._fetch_json({
                "function": "CURRENCY_DAILY",
                "from_currency": symbol,
                "to_currency": market,
                "outputsize": "full"
            })

            if not data:
                return None

            ts_key = None
            for key in data.keys():
                if "Time Series" in key:
                    ts_key = key
                    break

            if not ts_key:
                logger.error(f"No crypto data found for {symbol}")
                return None

            ts_data = data[ts_key]
            records = []

            for date_str, ohlc in ts_data.items():
                records.append({
                    "Date": date_str,
                    "Open": float(ohlc.get("1. open", 0)),
                    "High": float(ohlc.get("2. high", 0)),
                    "Low": float(ohlc.get("3. low", 0)),
                    "Close": float(ohlc.get("4. close", 0)),
                    "Symbole": symbol,
                    "Market": market,
                    "Source": "Alpha Vantage"
                })

            df = pd.DataFrame(records)
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")

            logger.info(f"✓ Fetched {len(df)} crypto records for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching crypto data for {symbol}: {e}")
            return None

    def close(self):
        """Close the session."""
        self.session.close()
