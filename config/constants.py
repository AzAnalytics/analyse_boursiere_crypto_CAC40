"""
Constantes du projet : symboles, tickers, etc.
"""

# ===== CAC 40 STOCKS =====
CAC40_STOCKS = {
    "LVMH Moët Hennessy - Louis Vuitton, Société Européenne": "MC.PA",
    "Hermès International Société": "RMS.PA",
    "L'Oréal S.A.": "OR.PA",
    "Christian Dior SE": "CDI.PA",
    "TotalEnergies SE": "TTE.PA",
    "Airbus SE": "AIR.PA",
    "Schneider Electric S.E.": "SU.PA",
    "Sanofi": "SAN.PA",
    "L'Air Liquide S.A.": "AI.PA",
    "EssilorLuxottica Société anonyme": "EL.PA",
    "Safran SA": "SAF.PA",
    "AXA SA": "CS.PA",
    "Vinci SA": "DG.PA",
    "BNP Paribas SA": "BNP.PA",
    "Dassault Systèmes SE": "DSY.PA",
    "Kering SA": "KER.PA",
    "Danone S.A.": "BN.PA",
}

# CAC 40 Index
CAC40_INDEX = "^FCHI"

# ===== CRYPTOCURRENCIES =====
CRYPTOCURRENCIES = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Tether": "USDT-USD",
    "Binance Coin": "BNB-USD",
    "Solana": "SOL-USD",
    "Lido Staked ETH": "STETH-USD",
    "Ripple": "XRP-USD",
    "USD Coin": "USDC-USD",
    "Cardano": "ADA-USD",
    "Dogecoin": "DOGE-USD",
    "Avalanche": "AVAX-USD",
    "Shiba Inu": "SHIB-USD",
}

# ===== DATA COLUMNS =====
OHLCV_COLUMNS = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
DATE_COLUMN = "Date"
SYMBOL_COLUMN = "Symbole"

# ===== ASSET TYPES =====
ASSET_TYPE_STOCK = "stock"
ASSET_TYPE_CRYPTO = "crypto"
ASSET_TYPE_INDEX = "index"

ASSET_TYPES = {
    "stock": ASSET_TYPE_STOCK,
    "crypto": ASSET_TYPE_CRYPTO,
    "index": ASSET_TYPE_INDEX,
}

# ===== COLUMNS TO DROP FROM YFINANCE =====
COLUMNS_TO_DROP = ["Dividends", "Stock Splits"]
