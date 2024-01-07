from pymongo import MongoClient
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly import colors
import json

mongo_uri = "mongodb+srv://timotheegallais:timotheegallais@securewebdev.ckf4mwz.mongodb.net/?retryWrites=true&w=majority"
database_name = "CDS"
collection_name = "VF"

client = MongoClient(mongo_uri)
db = client[database_name]
collection = db[collection_name]

def generate_discrete_color_sequence(num_colors):
    grad_scale = [[0, colors.unconvert_from_RGB_255((99, 49, 139))], [1, colors.unconvert_from_RGB_255((151,116,180))]]
    tuples = [colors.find_intermediate_color(grad_scale[0][1], grad_scale[1][1], i/(num_colors-1)) for i in range(num_colors)]
    return [colors.label_rgb(j) for j in [colors.convert_to_RGB_255(i) for i in tuples]]

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

    if arg == 'tbtol':
        pipeline = [
                    {"$group": {"_id": "$Type local", "count": {"$sum": 1}}}
                ]
        return pie_chart("Nombre de transactions en fonction du type de local", pipeline, "_id", "count", "Type Local", "Transactions")
        
    if arg == 'tbd':
        pipeline = [
                    {"$group": {"_id": "$Code departement", "count": {"$sum": 1}}}
                ]
        return bar_chart("Nombre de transactions en fonction du département", pipeline, "_id", "count", "Department Code", "Transactions", "linear")

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
        return pie_chart("Nombre de transactions en fonction du prix", pipeline, "_id", "count", "Price Category", "Transactions")

    if arg == 'tbnom':
        pipeline = [
                    {"$group": {"_id": "$Nature mutation", "count": {"$sum": 1}}}
                ]
        return bar_chart("Nombre de transactions en fonction de la nature de la mutation", pipeline, "_id", "count", "Mutation Nature", "Transactions", "log")

def prices(arg, price_per_sqm):
    if price_per_sqm:
        yaxis = "prixmcarre bati"
        ylabel = "Prix m² moyen"
    else:
        yaxis = "Valeur fonciere"
        ylabel = "Valeur foncière moyenne"

    if arg == 'pbtol':
        pipeline = [
            {"$match": {yaxis: {"$exists": True, "$nin": [float('NaN'), float('Infinity')]}}},
            {"$group": {"_id": "$Type local", "average_value": {"$avg": "$"+yaxis}}}
        ]
        return bar_chart(ylabel + " en fonction du type de local", pipeline, "_id", "average_value", "Local Type",ylabel, "linear")

    if arg == 'pbd':
        pipeline = [
            {"$match": {yaxis: {"$exists": True, "$nin": [float('NaN'), float('Infinity')]}}},
            {"$group": {"_id": "$Code departement", "average_value": {"$avg": "$"+yaxis}}}
        ]
        return bar_chart(ylabel + " en fonction du département", pipeline, "_id", "average_value", "Department",ylabel, "linear")


    if arg == 'pbnom':
        pipeline = [
            {"$match": {yaxis: {"$exists": True, "$nin": [float('NaN'), float('Infinity')]}}},
            {"$group": {"_id": "$Nature mutation", "average_value": {"$avg": "$"+yaxis}}}
        ]
        return bar_chart(ylabel + " en fonction de la nature de la mutation", pipeline, "_id", "average_value", "Nature de la mutation",ylabel, "linear")


    if arg == 'pbtos':
        pipeline = [
            {"$match": {yaxis: {"$exists": True, "$nin": [float('NaN'), float('Infinity')]},
                        "Type de voie": {"$in": ['RUE', 'BD', 'AV', 'RTE', 'CHE']}}},
            {"$group": {"_id": "$Type de voie", "average_value": {"$avg": "$"+yaxis}}}
        ]
        return bar_chart(ylabel + " en fonction du type de voie", pipeline, "_id", "average_value", "Type de voie",ylabel, "linear")


    result = list(collection.aggregate(pipeline))
    df_result = pd.DataFrame(result)
    df_result = df_result.sort_values(by='average_value', ascending=False)    

def maps(arg, depart):
    geo = json.load(open('C:/Users/galla/Desktop/A5/CDS/Project/assets/geojson/'+depart+'.geojson'))

    if arg == 'price':
        if depart=="00" :
            pipeline = [
                {"$match": {"Valeur fonciere": {"$exists": True, "$ne": float('NaN')}}},
                {"$group": {"_id": "$Code departement", "average_value": {"$avg": "$Valeur fonciere"}}}
            ]
            title = "Valeur foncière par département"
            label = "Price"
        else:
            pipeline = [
                {"$match": {"Valeur fonciere": {"$exists": True, "$ne": float('NaN')}, "Code departement": depart}},
                {"$group": {"_id": "$Code commune total", "average_value": {"$avg": "$Valeur fonciere"}}}
            ]  
            title = "Valeur foncière par commune dans le "+depart
            label = "Price"

    if arg == 'smprice':
        if depart=="00" :
            pipeline = [
                {"$match": {"prixmcarre bati": {"$exists": True, "$nin": [float('NaN'), float('Infinity')]}}},
                {"$group": {"_id": "$Code departement", "average_value": {"$avg": "$prixmcarre bati"}}}
            ]
            title = "Prix du m² par département"
            label = "Square Meter Price"
        else:
            pipeline = [
                {"$match": {"prixmcarre bati": {"$exists": True, "$ne": float('NaN')}, "Code departement": depart}},
                {"$group": {"_id": "$Code commune total", "average_value": {"$avg": "$prixmcarre bati"}}}
            ]  
            title = "Prix m² habitable par commune dans le "+depart
            label = "Square Meter Price"

    if arg == 'surfliveable':
        if depart =="00":
            pipeline = [
                {"$match": {"Surface reelle bati": {"$exists": True, "$nin": [float('NaN'), float('Infinity')]}}},
                {"$group": {"_id": "$Code departement", "average_value": {"$avg": "$Surface reelle bati"}}}
            ]
            title = "Surface de l'habitation par département"
            label = "Surface"
        else:
            pipeline = [
                {"$match": {"Surface reelle bati": {"$exists": True, "$ne": float('NaN')}, "Code departement": depart}},
                {"$group": {"_id": "$Code commune total", "average_value": {"$avg": "$Surface reelle bati"}}}
            ]  
            title = "Surface habitable par commune dans le "+depart
            label = "Surface"

    result = list(collection.aggregate(pipeline))
    df_result = pd.DataFrame(result)
    fig = px.choropleth(df_result,
                    geojson=geo,
                    title = title,
                    locations='_id',
                    featureidkey='properties.code',
                    color='average_value',
                    color_continuous_scale=[[0, '#dcb2ff'], [0.4, '#63318b'], [1, '#161b21']],
                    scope="europe",
                    labels={'average_value': label, "_id" : "Département" })
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        paper_bgcolor='#1d232c',
        plot_bgcolor='#1d232c',
        geo=dict(bgcolor='#1d232c'), 
        margin=dict(
            l=0,  
            r=0,  
            t=50,  
            b=0   
        ),
        font=dict(color='#83868b')
    )

    return fig

def bar_chart(title, pipeline, xAxis, yAxis, xLabel, yLabel, type):
    color_scale = [[0, '#63318b'], [1, '#e4c3ff']]  # Exemple de l'échelle, du vert au rouge
    result = list(collection.aggregate(pipeline))
    data = pd.DataFrame(result)
    data = data.sort_values(by=yAxis, ascending=False)
    fig = px.bar(data, x=data[xAxis], y=data[yAxis],
             title=title,
             labels={xAxis: xLabel, yAxis: yLabel},
             color=data[yAxis],
             color_continuous_scale=color_scale)

    fig.update_layout(
        paper_bgcolor='#1d232c',
        plot_bgcolor='#1d232c',
        font=dict(color='#83868b'),
        yaxis=dict(type=type, showgrid=False)
    )
    fig.update_traces(marker_line_color="rgba(0,0,0,0)")


    return fig

def pie_chart(title, pipeline, xAxis, yAxis, xLabel, yLabel):
    result = list(collection.aggregate(pipeline))
    data = pd.DataFrame(result)
    data = data.sort_values(by='count', ascending=False)
    print()
    fig = px.pie(data, 
                values=yAxis, 
                names=xAxis, 
                title=title,
                color=yAxis,
                color_discrete_sequence=generate_discrete_color_sequence(len(data[xAxis])),
                hole=.3,
                labels={xAxis: xLabel, yAxis: yLabel}
            )
    fig.update_layout(
        paper_bgcolor='#1d232c',
        plot_bgcolor='#1d232c',
        font=dict(color='#83868b')
    )
    return fig