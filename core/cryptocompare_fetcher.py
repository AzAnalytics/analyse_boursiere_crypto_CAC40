"""
CryptoCompare Data Fetcher

API for detailed cryptocurrency data and real-time prices.
Free tier available at: https://www.cryptocompare.com/api
"""

import pandas as pd
import requests
from typing import Optional, Dict, List
from datetime import datetime, timedelta

from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

# CryptoCompare API configuration
CC_BASE_URL = "https://min-api.cryptocompare.com/data"
CC_TIMEOUT = 10


class CryptoCompareFetcher:
    """
    Fetch cryptocurrency data from CryptoCompare API.

    Features:
    - Real-time price data for 5000+ cryptocurrencies
    - Historical daily/hourly data
    - Market data and trading pairs
    - Portfolio tracking support

    Example:
        fetcher = CryptoCompareFetcher(api_key="YOUR_KEY")
        df = fetcher.fetch_historical("BTC", "USD", days=365)
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CryptoCompare fetcher.

        Args:
            api_key: CryptoCompare API key (optional for free tier)
        """
        self.api_key = api_key or settings.get("CRYPTOCOMPARE_KEY")
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"authorization": f"Apikey {self.api_key}"})

    def _fetch_json(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """
        Fetch JSON from CryptoCompare API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response or None if error
        """
        try:
            url = f"{CC_BASE_URL}/{endpoint}"
            response = self.session.get(
                url,
                params=params,
                timeout=CC_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()

            # Check for errors
            if "Response" in data and data["Response"] == "Error":
                logger.error(f"CryptoCompare Error: {data.get('Message', 'Unknown error')}")
                return None

            return data

        except requests.RequestException as e:
            logger.error(f"Request error fetching from CryptoCompare: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing CryptoCompare response: {e}")
            return None

    def fetch_realtime(
        self,
        symbols: List[str],
        vs_currency: str = "USD"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch real-time price data.

        Args:
            symbols: List of crypto symbols (e.g., ["BTC", "ETH", "XRP"])
            vs_currency: Target currency (default: USD)

        Returns:
            DataFrame with real-time prices or None if error
        """
        logger.info(f"Fetching real-time data for {len(symbols)} cryptos from CryptoCompare...")

        try:
            data = self._fetch_json("pricemultifull", {
                "fsyms": ",".join(symbols),
                "tsyms": vs_currency,
                "extraParams": "analyse_boursiere_crypto"
            })

            if not data or "RAW" not in data:
                return None

            records = []
            raw_data = data["RAW"]

            for symbol in symbols:
                if symbol in raw_data:
                    price_data = raw_data[symbol][vs_currency]
                    records.append({
                        "Symbole": symbol,
                        "Price": float(price_data.get("PRICE", 0)),
                        "High24h": float(price_data.get("HIGH24HOUR", 0)),
                        "Low24h": float(price_data.get("LOW24HOUR", 0)),
                        "Open24h": float(price_data.get("OPEN24HOUR", 0)),
                        "Volume24h": float(price_data.get("VOLUME24HOUR", 0)),
                        "MarketCap": float(price_data.get("MKTCAP", 0)),
                        "Change24h": float(price_data.get("CHANGE24HOUR", 0)),
                        "ChangePercent24h": float(price_data.get("CHANGEPCT24HOUR", 0)),
                        "Timestamp": datetime.fromtimestamp(price_data.get("LASTUPDATE", 0)),
                        "Currency": vs_currency,
                        "Source": "CryptoCompare"
                    })

            df = pd.DataFrame(records)
            logger.info(f"✓ Fetched real-time data for {len(df)} cryptos")
            return df

        except Exception as e:
            logger.error(f"Error fetching real-time crypto data: {e}")
            return None

    def fetch_historical(
        self,
        symbol: str,
        vs_currency: str = "USD",
        days: int = 365
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical daily cryptocurrency data.

        Args:
            symbol: Crypto symbol (e.g., "BTC", "ETH")
            vs_currency: Target currency (default: USD)
            days: Number of days of history (max 2000)

        Returns:
            DataFrame with historical OHLCV data
        """
        logger.info(f"Fetching {days} days of {symbol}/{vs_currency} from CryptoCompare...")

        try:
            # Limit to max 2000 days per request
            limit = min(days, 2000)

            data = self._fetch_json("histoday", {
                "fsym": symbol,
                "tsym": vs_currency,
                "limit": limit,
                "extraParams": "analyse_boursiere_crypto"
            })

            if not data or "Data" not in data:
                return None

            records = []
            for candle in data["Data"]:
                records.append({
                    "Date": datetime.fromtimestamp(candle["time"]),
                    "Open": float(candle.get("open", 0)),
                    "High": float(candle.get("high", 0)),
                    "Low": float(candle.get("low", 0)),
                    "Close": float(candle.get("close", 0)),
                    "Volume": float(candle.get("volumefrom", 0)),
                    "VolumeQuote": float(candle.get("volumeto", 0)),
                    "Symbole": symbol,
                    "Currency": vs_currency,
                    "Source": "CryptoCompare"
                })

            df = pd.DataFrame(records)
            df = df.sort_values("Date")

            logger.info(f"✓ Fetched {len(df)} days of historical data for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None

    def fetch_hourly(
        self,
        symbol: str,
        vs_currency: str = "USD",
        hours: int = 168
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical hourly cryptocurrency data.

        Args:
            symbol: Crypto symbol
            vs_currency: Target currency
            hours: Number of hours (max 2000)

        Returns:
            DataFrame with hourly OHLCV data
        """
        logger.info(f"Fetching {hours} hours of {symbol}/{vs_currency} from CryptoCompare...")

        try:
            limit = min(hours, 2000)

            data = self._fetch_json("histohour", {
                "fsym": symbol,
                "tsym": vs_currency,
                "limit": limit,
                "extraParams": "analyse_boursiere_crypto"
            })

            if not data or "Data" not in data:
                return None

            records = []
            for candle in data["Data"]:
                records.append({
                    "DateTime": datetime.fromtimestamp(candle["time"]),
                    "Open": float(candle.get("open", 0)),
                    "High": float(candle.get("high", 0)),
                    "Low": float(candle.get("low", 0)),
                    "Close": float(candle.get("close", 0)),
                    "Volume": float(candle.get("volumefrom", 0)),
                    "VolumeQuote": float(candle.get("volumeto", 0)),
                    "Symbole": symbol,
                    "Currency": vs_currency,
                    "Source": "CryptoCompare"
                })

            df = pd.DataFrame(records)
            df = df.sort_values("DateTime")

            logger.info(f"✓ Fetched {len(df)} hours of data for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching hourly data for {symbol}: {e}")
            return None

    def fetch_minute(
        self,
        symbol: str,
        vs_currency: str = "USD",
        minutes: int = 60
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical minute cryptocurrency data.

        Args:
            symbol: Crypto symbol
            vs_currency: Target currency
            minutes: Number of minutes (max 2000)

        Returns:
            DataFrame with minute-level OHLCV data
        """
        logger.info(f"Fetching {minutes} minutes of {symbol}/{vs_currency} from CryptoCompare...")

        try:
            limit = min(minutes, 2000)

            data = self._fetch_json("histominute", {
                "fsym": symbol,
                "tsym": vs_currency,
                "limit": limit,
                "extraParams": "analyse_boursiere_crypto"
            })

            if not data or "Data" not in data:
                return None

            records = []
            for candle in data["Data"]:
                records.append({
                    "Time": datetime.fromtimestamp(candle["time"]),
                    "Open": float(candle.get("open", 0)),
                    "High": float(candle.get("high", 0)),
                    "Low": float(candle.get("low", 0)),
                    "Close": float(candle.get("close", 0)),
                    "Volume": float(candle.get("volumefrom", 0)),
                    "VolumeQuote": float(candle.get("volumeto", 0)),
                    "Symbole": symbol,
                    "Currency": vs_currency,
                    "Source": "CryptoCompare"
                })

            df = pd.DataFrame(records)
            df = df.sort_values("Time")

            logger.info(f"✓ Fetched {len(df)} minutes of data for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching minute data for {symbol}: {e}")
            return None

    def close(self):
        """Close the session."""
        self.session.close()
