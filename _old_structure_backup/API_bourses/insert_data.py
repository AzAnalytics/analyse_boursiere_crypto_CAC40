import yfinance as yf
from connection import *
import pandas as pd
# Sélectionner la base de données

db = client[dbname]

# Sélectionner la collection dans laquelle vous souhaitez insérer les données
collection = db[collection_name]
print(collection)


for symbole in symboles.values():
    action = yf.Ticker(symbole)
    try:
        historique = action.history(period="max")
        if not historique.empty:
            if 'Dividends' in historique.columns and 'Stock Splits' in historique.columns:
                historique = historique.drop(columns=['Dividends', 'Stock Splits'])
            historique = historique.reset_index()
            if pd.api.types.is_datetime64_any_dtype(historique['Date']):
                historique['Date'] = historique['Date'].dt.strftime('%d/%m/%Y')
                # Ici, insérez les données dans MongoDB ou autre traitement
            historique["Symbole"] = symbole
        # Convertir le DataFrame en liste de dictionnaires
        records = historique.to_dict('records')
        # Insérer les données dans MongoDB
        collection.insert_many(records)
    except Exception as e:
        print(f"Erreur avec le symbole {symbole}: {e}")
