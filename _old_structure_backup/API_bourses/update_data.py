import yfinance as yf
from datetime import datetime, timedelta
from connection import *

# Sélectionner la base de données
db = client[dbname]
print(db)

# Sélectionner la collection dans laquelle vous souhaitez insérer les données
collection = db[collection_name]
print(collection)

# Calculer la date de la veille
today = datetime.now()
if today.weekday() == 0:
    hier = today - timedelta(days=3)
else:
    hier = today - timedelta(days=1)

date_format_yfinance = hier.strftime('%Y-%m-%d')  # Format pour yfinance
date_format_db = hier.strftime('%d/%m/%Y')  # Format pour la base de données

for symbole in symboles.values():
    action = yf.Ticker(symbole)
    historique = action.history(start=date_format_yfinance, end=datetime.now().strftime('%Y-%m-%d'))
    if not historique.empty:
        dernier = historique.iloc[-1]
        document = {
            'Date': date_format_db,  # Utilisez le format de date pour la base de données
            'Open': dernier['Open'],
            'High': dernier['High'],
            'Low': dernier['Low'],
            'Close': dernier['Close'],
            'Volume': dernier['Volume'],
            'Symbole': symbole
        }
        collection.insert_one(document)
        print(f"Inséré : {document}")
    else:
        print(f"Aucune donnée trouvée pour {symbole} à la date {date_format_db}.")
