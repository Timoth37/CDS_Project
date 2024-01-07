from pymongo import MongoClient
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json

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
                    "mean_surface_liveable": {"$avg": "$Surface reelle bati"},
                    "number_transac" : {"$sum" : 1}}}
    ]

    result = list(collection.aggregate(pipeline))
    result = result[0]
    return result if result else None

def transac(arg):
    type = 'linear'
    yaxis = "Transaction Number"

    if arg == 'tbtol':
        pipeline = [
                    {"$group": {"_id": "$Type local", "count": {"$sum": 1}}}
                ]

        xaxis = "Type de local"
        title = "Nombre de transactions en fonction du type de local"

    if arg == 'tbd':
        pipeline = [
                    {"$group": {"_id": "$Code departement", "count": {"$sum": 1}}}
                ]
        xaxis = "Département"
        title = "Nombre de transactions en fonction du département"

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
        xaxis = "Price Range"
        title = "Nombre de transactions en fonction du prix"

    if arg == 'tbnom':
        pipeline = [
                    {"$group": {"_id": "$Nature mutation", "count": {"$sum": 1}}}
                ]
        xaxis = "Nature de la mutation"  
        title = "Nombre de transactions en fonction de la nature de la mutation"
        type = 'log'
  


    result = list(collection.aggregate(pipeline))
    df_result = pd.DataFrame(result)
    df_result = df_result.sort_values(by='count', ascending=False)

    # Définir les couleurs de l'échelle
    color_scale = [[0, '#63318b'], [1, '#dcb2ff']]  # Exemple de l'échelle, du vert au rouge

    # Créer le graphique avec Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_result['_id'],
        y=df_result['count'],
        marker=dict(color=df_result['count'], colorscale=color_scale, line=dict(color='rgba(0,0,0,0)', width=0)),
        hoverinfo='y+text',
        name='Valeur foncière moyenne'
    ))

    # Mise en page du graphique
    fig.update_layout(
        title=title,
        xaxis=dict(title=xaxis, showgrid= False),
        yaxis=dict(title=yaxis, showgrid=False, type=type),
        paper_bgcolor='#1d232c',
        plot_bgcolor='#1d232c',
        font=dict(color='#83868b')
    )

    return fig

def prices(arg, price_per_sqm):
    if price_per_sqm:
        column = "prixmcarre bati"
        yaxis = "Prix m² moyen"
    else:
        column = "Valeur fonciere"
        yaxis = "Valeur foncière moyenne"

    if arg == 'pbtol':
        pipeline = [
            {"$match": {column: {"$exists": True, "$ne": float('NaN')}}},
            {"$group": {"_id": "$Type local", "average_value": {"$avg": "$"+column}}}
        ]
        title = yaxis + " en fonction du type de local"
        xaxis = "Type de local"

    if arg == 'pbd':
        pipeline = [
            {"$match": {column: {"$exists": True, "$ne": float('NaN')}}},
            {"$group": {"_id": "$Code departement", "average_value": {"$avg": "$"+column}}}
        ]
        title = yaxis + " en fonction du département"
        xaxis = "Département"

    if arg == 'pbnom':
        pipeline = [
            {"$match": {column: {"$exists": True, "$ne": float('NaN')}}},
            {"$group": {"_id": "$Nature mutation", "average_value": {"$avg": "$"+column}}}
        ]
        title = yaxis + " en fonction de la nature de la mutation"
        xaxis = "Nature de la mutation"

    if arg == 'pbtos':
        pipeline = [
            {"$match": {column: {"$exists": True, "$ne": float('NaN')},
                        "Type de voie": {"$in": ['RUE', 'BD', 'AV', 'RTE', 'CHE']}}},
            {"$group": {"_id": "$Type de voie", "average_value": {"$avg": "$"+column}}}
        ]
        title = yaxis + " en fonction du type de voie"
        xaxis = "Type de voie"

    result = list(collection.aggregate(pipeline))
    df_result = pd.DataFrame(result)
    df_result = df_result.sort_values(by='average_value', ascending=False)

    # Définir les couleurs de l'échelle
    color_scale = [[0, '#63318b'], [1, '#dcb2ff']]  # Exemple de l'échelle, du vert au rouge

    # Créer le graphique avec Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_result['_id'],
        y=df_result['average_value'],
        marker=dict(color=df_result['average_value'], colorscale=color_scale, line=dict(color='rgba(0,0,0,0)', width=0)),
        hoverinfo='y+text',
        name='Valeur foncière moyenne'
    ))

    # Mise en page du graphique
    fig.update_layout(
        title=title,
        xaxis=dict(title=xaxis, showgrid= False),
        yaxis=dict(title=yaxis, showgrid=False),
        paper_bgcolor='#1d232c',
        plot_bgcolor='#1d232c',
        font=dict(color='#83868b')
    )



    return fig

def maps(arg):

    geo = json.load(open('C:/Users/galla/Desktop/A5/CDS/Project/assets/depart.geojson'))


    if arg == 'price':
        pipeline = [
            {"$match": {"Valeur fonciere": {"$exists": True, "$ne": float('NaN')}}},
            {"$group": {"_id": "$Code departement", "average_value": {"$avg": "$Valeur fonciere"}}}
        ]

    if arg == 'smprice':
        pipeline = [
            {"$match": {"prixmcarre bati": {"$exists": True, "$ne": float('NaN')}}},
            {"$group": {"_id": "$Code departement", "average_value": {"$avg": "$prixmcarre bati"}}}
        ]

    result = list(collection.aggregate(pipeline))
    df_result = pd.DataFrame(result)
    fig = px.choropleth(df_result,
                    geojson=geo,
                    title ="Valeur foncière moyenne",
                    locations='_id',
                    featureidkey='properties.code',
                    color='average_value',
                    color_continuous_scale="magma",
                    range_color=(0, 600000),
                    scope="europe",
                    labels={'average_value': 'Valeur fonciere moyenne'})
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        paper_bgcolor='#1d232c',
        plot_bgcolor='#1d232c',
        geo=dict(bgcolor='#1d232c'), 
        margin=dict(
            l=0,  # Marge à gauche
            r=0,  # Marge à droite
            t=0,  # Marge en haut
            b=0   # Marge en bas
        ),
        font=dict(color='#83868b')
    )

    return fig