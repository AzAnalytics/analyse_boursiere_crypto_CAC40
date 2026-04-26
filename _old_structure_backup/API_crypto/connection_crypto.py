from pymongo import MongoClient
import os

try:

    user = os.environ.get("MONGO_USER")
    password = os.environ.get("MONGO_PASSWORD")
    host = os.environ.get("MONGO_HOST")
    dbname = os.environ.get("MONGO_DBNAME")
    collection_name_crypto = os.environ.get("MONGO_COLLECTION_NAME_CRYPTO")
    app_name = os.environ.get("MONGO_APP_NAME")
    uri = f"mongodb+srv://{user}:{password}@{host}/{dbname}?retryWrites=true&w=majority&appName={app_name}&tls=true"

    print(uri)
    client = MongoClient(uri)
    symboles = {
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
        "Shiba Inu": "SHIB-USD"
    }
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    # Complétez cette liste avec les symboles réels
except Exception as e:
    print(e)
