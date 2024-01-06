from pymongo import MongoClient
import pandas as pd
from dash import dcc, html


mongo_uri = "mongodb+srv://timotheegallais:timotheegallais@securewebdev.ckf4mwz.mongodb.net/?retryWrites=true&w=majority"
database_name = "CDS"
collection_name = "VF"

client = MongoClient(mongo_uri)
db = client[database_name]
collection = db[collection_name]

def global_infos():
    pipeline = [
        {"$match": {"Valeur fonciere": {"$exists": True, "$ne": float('NaN')}, 
                    "Surface terrain": {"$exists": True, "$ne": float('NaN')}, 
                    "Surface reelle bati": {"$exists": True, "$ne": float('NaN')},
                    "prixmcarre terr": {"$exists": True, "$ne": float('NaN')}}},
        {"$group": {"_id": None, 
                    "mean_value": {"$avg": "$Valeur fonciere"}, 
                    "max_value": {"$max": "$Valeur fonciere"},
                    "mean_surface_field": {"$avg": "$Surface terrain"},
                    "mean_surface_liveable": {"$avg": "$Surface reelle bati"}}}
    ]

    result = list(collection.aggregate(pipeline))
    result = result[0]
    return result if result else None

def type_loc_graph(arg):
    if arg == 'tbtol':
        pipeline = [
                    {"$group": {"_id": "$Type local", "count": {"$sum": 1}}}
                ]

        result = list(collection.aggregate(pipeline))
        df_result = pd.DataFrame(result)
        df_result = df_result.sort_values(by='count', ascending = False)


        figure = {
            'data': [
                {'x': df_result['_id'], 'y': df_result['count'], 'type': 'bar', 'name': 'Nombre de demandes', 'marker': {'color': '#63318b'}}
            ],
            'layout': {
                'title': "Nombre de transactions en fonction du type de local",
                'xaxis': {'title': 'Type local'},
                'yaxis': {'title': 'Nombre de demandes'},
                'paper_bgcolor': '#1d232c',
                'plot_bgcolor': '#1d232c',
                'font' : {
                    'color' : '#83868b'
                }
            }
        }

    if arg == 'tbd':
        pipeline = [
                    {"$group": {"_id": "$Code departement", "count": {"$sum": 1}}}
                ]

        result = list(collection.aggregate(pipeline))
        df_result = pd.DataFrame(result)


        figure = {
            'data': [
                {'x': df_result['_id'], 'y': df_result['count'], 'type': 'bar', 'name': 'Nombre de demandes', 'marker': {'color': '#63318b'}}
            ],
            'layout': {
                'title': "Nombre de transactions en fonction du département",
                'xaxis': {'title': 'Département'},
                'yaxis': {'title': 'Nombre de demandes'},
                'paper_bgcolor': '#1d232c',
                'plot_bgcolor': '#1d232c',
                'font' : {
                    'color' : '#83868b'
                }
            }
        }

    if arg == 'tbrop':
        pipeline = [
            {
                "$project": {
                    "_id": 0,
                    "categorie_prix": {
                        "$switch": {
                            "branches": [
                                {"case": {"$lte": ["$Valeur fonciere", 10000]}, "then": "0-10000"},
                                {"case": {"$lte": ["$Valeur fonciere", 50000]}, "then": "10001-50000"},
                                {"case": {"$lte": ["$Valeur fonciere", 100000]}, "then": "50001-100000"},
                                {"case": {"$lte": ["$Valeur fonciere", 200000]}, "then": "100001-200000"},
                                {"case": {"$lte": ["$Valeur fonciere", 500000]}, "then": "200001-500000"},
                                {"case": {"$lte": ["$Valeur fonciere", 1000000]}, "then": "500001-1000000"},
                                {"case": {"$gt": ["$Valeur fonciere", 1000000]}, "then": "1000000+"}
                            ],
                            "default": "Unknown"
                        }
                    }
                }
            },
            {"$group": {"_id": "$categorie_prix", "count": {"$sum": 1}}}
        ]

        result = list(collection.aggregate(pipeline))
        df_result = pd.DataFrame(result)

        figure = {
            'data': [
                {'x': df_result['_id'], 'y': df_result['count'], 'type': 'bar', 'name': 'Nombre de transactions', 'marker': {'color': '#63318b'}}
            ],
            'layout': {
                'title': "Nombre de transactions en fonction de la Valeur foncière",
                'xaxis': {'title': 'Catégorie de prix'},
                'yaxis': {'title': 'Nombre de transactions'},
                'paper_bgcolor': '#1d232c',
                'plot_bgcolor': '#1d232c',
                'font' : {
                    'color' : '#83868b'
                }
            }
        }

    if arg == 'tbnom':
        pipeline = [
                    {"$group": {"_id": "$Nature mutation", "count": {"$sum": 1}}}
                ]

        result = list(collection.aggregate(pipeline))
        df_result = pd.DataFrame(result)
        df_result = df_result.sort_values(by='count', ascending = False)


        figure = {
            'data': [
                {'x': df_result['_id'], 'y': df_result['count'], 'type': 'bar', 'name': 'Nombre de demandes', 'marker': {'color': '#63318b'}}
            ],
            'layout': {
                'title': "Nombre de transactions en fonction de la nature de la mutation (log)",
                'xaxis': {'title': 'Nature de la mutation'},
                'yaxis': {'title': 'Nombre de demandes', 'type': 'log'},
                'paper_bgcolor': '#1d232c',
                'plot_bgcolor': '#1d232c',
                'font' : {
                    'color' : '#83868b'
                }
            }
        }     

    return figure