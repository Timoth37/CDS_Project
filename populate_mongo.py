import pandas as pd
from pymongo import MongoClient

# Configuration de la base de données MongoDB
mongo_uri = "mongodb+srv://timotheegallais:timotheegallais@securewebdev.ckf4mwz.mongodb.net/?retryWrites=true&w=majority"
database_name = "CDS"
collection_name = "VF"

# Chemin vers le fichier CSV
csv_file_path = "C:/Users/galla/Downloads/valeursfoncieres-2022.txt"

# Fonction pour le traitement des données
def preprocess_data(df):
    # Garder seulement les colonnes spécifiées
    columns_to_keep = ['Date mutation', 'Nature mutation', 'Valeur fonciere', 'Type de voie',
                        'Code postal', 'Commune', 'Code departement', 'Code commune',
                        'Nombre de lots', 'Type local', 'Surface reelle bati',
                        'Nombre pieces principales', 'Surface terrain']
    df = df[columns_to_keep]

    # Convertir la colonne 'Date mutation' en datetime
    df['Date mutation'] = pd.to_datetime(df['Date mutation'], format="%d/%m/%Y", errors='coerce')

    # Adapter le type des colonnes et remplacer les virgules par des points dans 'Valeur fonciere'
    df['Valeur fonciere'] = df['Valeur fonciere'].str.replace(",", ".").astype(float)

    # Supprimer les doublons de propriétés
    df = df[df['Type local'] != 'Dépendance']
    df = df.drop_duplicates(subset=['Date mutation', 'Nature mutation', 'Valeur fonciere', 'Commune', 'Code postal'], keep='first').reset_index(drop=True)

    # Traitement sur la colonne Code Commune
    df['Code departement'] = df['Code departement'].apply(lambda x: str(x).zfill(2))
    df['Code commune'] = df['Code commune'].apply(lambda x: str(x).zfill(3))
    df['Code commune total'] = df['Code departement'] + df['Code commune']

    # Créer deux nouvelles colonnes
    df['prixmcarre bati'] = df['Valeur fonciere'] / df['Surface reelle bati']
    df['prixmcarre terr'] = df['Valeur fonciere'] / df['Surface terrain']

    return df

# Fonction pour charger les données depuis le CSV vers MongoDB
def csv_to_mongodb(csv_file_path, mongo_uri, database_name, collection_name):
    # Charger le CSV dans un DataFrame pandas
    df = pd.read_csv(csv_file_path, sep='|')

    # Appliquer le prétraitement des données
    df = preprocess_data(df)

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


def clear_mongo_collection(mongo_uri, database_name, collection_name):
    # Connexion à la base de données MongoDB
    client = MongoClient(mongo_uri)

    # Accès à la collection spécifiée
    db = client[database_name]
    collection = db[collection_name]

    try:
        # Supprimer tous les documents de la collection
        result = collection.delete_many({})
        print(f"La collection '{collection_name}' a été vidée. {result.deleted_count} documents supprimés.")
    except Exception as e:
        print(f"Erreur lors de la suppression des documents de la collection '{collection_name}': {e}")
    finally:
        # Fermer la connexion MongoDB
        client.close()


#clear_mongo_collection(mongo_uri, database_name, collection_name)