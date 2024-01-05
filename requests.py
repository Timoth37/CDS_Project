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
                    "mean_surface_terrain": {"$avg": "$Surface terrain"},
                    "mean_surface_bati": {"$avg": "$Surface reelle bati"}}}
    ]

    result = list(collection.aggregate(pipeline))
    return result[0] if result else None

def type_loc_graph():
    pipeline = [
                {"$group": {"_id": "$Type local", "count": {"$sum": 1}}}
            ]

    result = list(collection.aggregate(pipeline))
    df_result = pd.DataFrame(result)


    # Création de la figure pour dcc.Graph
    figure = {
        'data': [
            {'x': df_result['_id'], 'y': df_result['count'], 'type': 'bar', 'name': 'Nombre de demandes', 'marker': {'color': '#666666'}}
        ],
        'layout': {
            'title': "Nombre de transactions en fonction du type de local",
            'xaxis': {'title': 'Type local'},
            'yaxis': {'title': 'Nombre de demandes'},
            'paper_bgcolor': '#000000',
            'plot_bgcolor': '#000000',
        }
    }

    return html.Div(className="graph_container", children=[dcc.Graph(figure=figure)])