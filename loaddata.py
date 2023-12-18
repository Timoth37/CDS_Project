import pandas as pd
from pymongo import MongoClient
# Configuration de la base de données MongoDB
mongo_uri = "mongodb+srv://TDG:TDG@cluster0.cyiptjg.mongodb.net/?retryWrites=true&w=majority"
database_name = "CDS"
collection_name = "ValeurFonciere"

# Chemin vers le fichier CSV
csv_file_path = "C:/Guillaume/Annee5/CloudDataStructure/valeursfoncieres-2022.csv"

# Fonction pour charger les données depuis le CSV vers MongoDB
def csv_to_mongodb(csv_file_path, mongo_uri, database_name, collection_name):
    # Charger le CSV dans un DataFrame pandas
    df = pd.read_csv(csv_file_path, sep=';', on_bad_lines='skip')

    # Connexion à la base de données MongoDB
    client = MongoClient(mongo_uri)

    db = client[database_name]
    collection = db[collection_name]

    # Convertir le DataFrame en une liste de dictionnaires (une par document)
    data = df.to_dict(orient='records')

    # Insérer les données dans la collection MongoDB
    collection.insert_many(data)

    # Fermer la connexion MongoDB
    client.close()

# Appeler la fonction avec les paramètres appropriés
csv_to_mongodb(csv_file_path, mongo_uri, database_name, collection_name)