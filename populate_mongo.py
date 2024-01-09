import pandas as pd
import json
from pymongo import MongoClient

# Configuration de la base de données MongoDB
mongo_uri = "mongodb://localhost:27017"
database_name = "CDS"


def populate_VF(file_path, mongo_uri, database_name, collection_name):
    df = pd.read_csv(file_path, sep='|')
    df = preprocess_data(df)

    client = MongoClient(mongo_uri)
    db = client[database_name]
    collection = db[collection_name]

    data = df.to_dict(orient='records')

    collection.insert_many(data)

    client.close()

#populate_VF("C:/Users/galla/Downloads/valeursfoncieres-2021.txt", mongo_uri, database_name, 'VF')

def populate_DEPART(file_path, mongo_uri, database_name, collection_name):

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        client = MongoClient(mongo_uri)
        db = client[database_name]
        collection = db[collection_name]
        
        collection.insert_many(data)
        
        client.close()
#populate_DEPART("C:/Users/galla/Desktop/A5/CDS/Project/datas/json/france.json", mongo_uri, database_name, 'COMMUNES')


def populate_GEO(departList, mongo_uri, database_name, collection_name):
    client = MongoClient(mongo_uri)
    db = client[database_name]
    collection = db[collection_name]
    
    for i, j in departList.items():
        with open('C:/Users/galla/Desktop/A5/CDS/Project/datas/geojson/'+i+'.geojson', 'r') as file:
            data=json.load(file)
            data['depart_id'] = i
            collection.insert_one(data)


departList = {
        "00" : "France",
        "01": "Ain",
        "02": "Aisne",
        "03": "Allier",
        "04": "Alpes-de-Haute-Provence",
        "05": "Hautes-Alpes",
        "06": "Alpes-Maritimes",
        "07": "Ardèche",
        "08": "Ardennes",
        "09": "Ariège",
        "10": "Aube",
        "11": "Aude",
        "12": "Aveyron",
        "13": "Bouches-du-Rhône",
        "14": "Calvados",
        "15": "Cantal",
        "16": "Charente",
        "17": "Charente-Maritime",
        "18": "Cher",
        "19": "Corrèze",
        "21": "Côte-d'Or",
        "22": "Côtes-d'Armor",
        "23": "Creuse",
        "24": "Dordogne",
        "25": "Doubs",
        "26": "Drôme",
        "27": "Eure",
        "28": "Eure-et-Loir",
        "29": "Finistère",
        "2A": "Corse-du-Sud",
        "2B": "Haute-Corse",
        "30": "Gard",
        "31": "Haute-Garonne",
        "32": "Gers",
        "33": "Gironde",
        "34": "Hérault",
        "35": "Ille-et-Vilaine",
        "36": "Indre",
        "37": "Indre-et-Loire",
        "38": "Isère",
        "39": "Jura",
        "40": "Landes",
        "41": "Loir-et-Cher",
        "42": "Loire",
        "43": "Haute-Loire",
        "44": "Loire-Atlantique",
        "45": "Loiret",
        "46": "Lot",
        "47": "Lot-et-Garonne",
        "48": "Lozère",
        "49": "Maine-et-Loire",
        "50": "Manche",
        "51": "Marne",
        "52": "Haute-Marne",
        "53": "Mayenne",
        "54": "Meurthe-et-Moselle",
        "55": "Meuse",
        "56": "Morbihan",
        "57": "Moselle",
        "58": "Nièvre",
        "59": "Nord",
        "60": "Oise",
        "61": "Orne",
        "62": "Pas-de-Calais",
        "63": "Puy-de-Dôme",
        "64": "Pyrénées-Atlantiques",
        "65": "Hautes-Pyrénées",
        "66": "Pyrénées-Orientales",
        "67": "Bas-Rhin",
        "68": "Haut-Rhin",
        "69": "Rhône",
        "70": "Haute-Saône",
        "71": "Saône-et-Loire",
        "72": "Sarthe",
        "73": "Savoie",
        "74": "Haute-Savoie",
        "75": "Paris",
        "76": "Seine-Maritime",
        "77": "Seine-et-Marne",
        "78": "Yvelines",
        "79": "Deux-Sèvres",
        "80": "Somme",
        "81": "Tarn",
        "82": "Tarn-et-Garonne",
        "83": "Var",
        "84": "Vaucluse",
        "85": "Vendée",
        "86": "Vienne",
        "87": "Haute-Vienne",
        "88": "Vosges",
        "89": "Yonne",
        "90": "Territoire de Belfort",
        "91": "Essonne",
        "92": "Hauts-de-Seine",
        "93": "Seine-Saint-Denis",
        "94": "Val-de-Marne",
        "95": "Val-d'Oise",
        "971": "Guadeloupe",
        "972": "Martinique",
        "973": "Guyane",
        "974": "La Réunion",
        "976": "Mayotte"
    }

#populate_GEO(departList, mongo_uri, database_name, 'GEO')


def preprocess_data(df):
    # Garder seulement les colonnes spécifiées
    columns_to_keep = ['Date mutation', 'Nature mutation', 'Valeur fonciere', 'Type de voie',
                        'Code postal', 'Commune', 'Code departement', 'Code commune',
                        'Nombre de lots', 'Type local', 'Surface reelle bati',
                        'Nombre pieces principales', 'Surface terrain']
    df = df[columns_to_keep]

    # Convertir la colonne 'Date mutation' en datetime et Valeur fonciere en float et Type Local en string
    df['Date mutation'] = pd.to_datetime(df['Date mutation'], format="%d/%m/%Y", errors='coerce')
    df['Valeur fonciere'] = df['Valeur fonciere'].apply(lambda x: str(x).replace(',','.'))
    df['Valeur fonciere']=df['Valeur fonciere'].astype(float)
    
    df['Type local'] = df['Type local'].astype(str)

    # Supprimer les doublons de propriétés
    df = df[df['Type local'] != str('nan')]
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