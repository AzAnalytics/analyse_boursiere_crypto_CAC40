import yfinance as yf
from datetime import datetime, timedelta
from connection_crypto import *

# Sélectionner la base de données
db = client[dbname]
print(db)

# Sélectionner la collection dans laquelle vous souhaitez insérer les données
collection = db[collection_name_crypto]
print(collection)

# Calculer la date de la veille
today = datetime.now()
hier = today - timedelta(days=1)

date_format_yfinance = hier.strftime('%Y-%m-%d')  # Format pour yfinance
date_format_db = hier.strftime('%d/%m/%Y')  # Format pour la base de données

for symbole, ticker in symboles.items():
    action = yf.Ticker(ticker)
    print(f"Récupération des données pour {symbole} ({ticker}) à partir de {date_format_yfinance}")
    try:
        historique = action.history(start=date_format_yfinance, end=(today + timedelta(days=1)).strftime('%Y-%m-%d'))
        print(f"Données reçues pour {symbole} : {historique}")
        
        if historique.empty:
            print(f"Aucune donnée trouvée pour {symbole} ({ticker}) à la date {date_format_db}.")
            continue
        
        dernier = historique.iloc[-1]
        document = {
            'Date': date_format_db,  # Utilisez le format de date pour la base de données
            'Open': dernier['Open'],
            'High': dernier['High'],
            'Low': dernier['Low'],
            'Close': dernier['Close'],
            'Volume': dernier['Volume'],
            'Symbole': ticker
        }
        collection.insert_one(document)
        print(f"Inséré : {document}")
    except Exception as e:
        print(f"Erreur lors de la récupération des données pour {symbole} ({ticker}) : {e}")
