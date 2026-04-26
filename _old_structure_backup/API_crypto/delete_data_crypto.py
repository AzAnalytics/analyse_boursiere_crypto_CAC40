from connection_crypto import *
from datetime import datetime, timedelta
# Sélectionner la base de données
db = client[dbname]

# Sélectionner la collection dans laquelle vous souhaitez insérer les données
collection = db[collection_name_crypto]
print(collection)

# Suppression de tous les documents de la collection
result = collection.delete_many({})

print(f"Nombre de documents supprimés: {result.deleted_count}")
