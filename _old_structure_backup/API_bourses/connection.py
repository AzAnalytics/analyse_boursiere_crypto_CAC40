from pymongo import MongoClient
import os

try:
    # Récupération des informations de connexion depuis les variables d'environnement
    user = os.environ.get("MONGO_USER")
    password = os.environ.get("MONGO_PASSWORD")
    host = os.environ.get("MONGO_HOST")
    dbname = os.environ.get("MONGO_DBNAME")
    collection_name = os.environ.get("MONGO_COLLECTION_NAME")
    app_name = os.environ.get("MONGO_APP_NAME")

    # Construction de l'URI de connexion à MongoDB
    uri = f"mongodb+srv://{user}:{password}@{host}/{dbname}?retryWrites=true&w=majority&appName={app_name}&tls=true"

    # Connexion à MongoDB
    client = MongoClient(uri)

    # Sélection de la base de données et de la collection
    db = client[dbname]
    collection = db[collection_name]

    # Liste des symboles
    symboles = {
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
        "Danone S.A.": "BN.PA"
    }

    # Vérification de la connexion
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    # Complétez cette liste avec les symboles réels
except Exception as e:
    print(e)
