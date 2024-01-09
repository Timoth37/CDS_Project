from pymongo import MongoClient
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly import colors
import json

mongo_uri = "mongodb://localhost:27017"
database_name = "CDS"
collection_name = "VF"

client = MongoClient(mongo_uri)
db = client[database_name]
collection = db[collection_name]

#listCommunes = json.load(open('C:/Users/galla/Desktop/A5/CDS/Project/assets/json/france.json', encoding='utf-8'))


def generate_discrete_color_sequence(num_colors):
    grad_scale = [[0, colors.unconvert_from_RGB_255((99, 49, 139))], [1, colors.unconvert_from_RGB_255((151,116,180))]]
    tuples = [colors.find_intermediate_color(grad_scale[0][1], grad_scale[1][1], i/(num_colors-1)) for i in range(num_colors)]
    return [colors.label_rgb(j) for j in [colors.convert_to_RGB_255(i) for i in tuples]]

def get_commune_name(communecode):
    result = db['COMMUNES'].find_one({"codgeo": communecode})
    return result['libgeo']

def get_commune_list(departCode):
    test = list(db['COMMUNES'].find({"dep": departCode}))
    return [{"name" : element["libgeo"], "code" : element["codgeo"]} for element in sorted(test, key=lambda obj : obj['libgeo'])]

def global_infos():
    pipeline = [
        {"$match": {"Valeur fonciere": {"$exists": True, "$ne": float('NaN')}, 
                    "Surface terrain": {"$exists": True, "$ne": float('NaN')}, 
                    "Surface reelle bati": {"$exists": True, "$ne": float('NaN')},
                    "prixmcarre terr": {"$exists": True, "$ne": float('NaN')}},
                    },
        {"$group": {"_id": None, 
                    "mean_value": {"$avg": "$Valeur fonciere"}, 
                    "max_value": {"$max": "$Valeur fonciere"},
                    "mean_surface_field": {"$avg": "$Surface terrain"},
                    "mean_surface_liveable": {"$avg": "$Surface reelle bati"},
                    "number_transac" : {"$sum" : 1}}}
    ]
    result = list(collection.aggregate(pipeline))
    mainStat = result[0]
    pipeline = [
        {"$group": {"_id": "$Type local", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    result = list(collection.aggregate(pipeline))
    mainStat['main_local'] = result[0]['_id']

    pipeline = [
        {"$project": {
            "month": {"$month": "$Date mutation"}
        }},
        {"$group": {
            "_id": "$month",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    result = list(collection.aggregate(pipeline))
    mainStat['main_month'] = result[0]['_id']

    pipeline = [
        {"$match": {
            "Nombre pieces principales": {"$exists": True, "$nin": [float('nan'), 0]}
        }},
        {"$group": {
            "_id": None,
            "mean_rooms": {"$avg": "$Nombre pieces principales"}
        }}
    ]
    result = list(collection.aggregate(pipeline))
    mainStat['mean_rooms'] = result[0]['mean_rooms']
    return mainStat

def full_search(type, rooms, depart, commune, price, surface):
    pipeline = []

    if type:
        pipeline.append({"$match": {"Type local": type}})

    if rooms:
        pipeline.append({"$match": {"Nombre pieces principales": rooms}})

    if commune:
        pipeline.append({"$match": {"Code commune total": commune}})

    if depart:
        pipeline.append({"$match": {"Code departement": depart}})

    # Filtrer par price
    price_filter = {}
    if price[0] is not None:
        price_filter["$gte"] = price[0]
    if price[1] is not None:
        price_filter["$lte"] = price[1]
    if price_filter:
        pipeline.append({"$match": {"Valeur fonciere": price_filter}})

    # Filtrer par surface
    surface_filter = {}
    if surface[0] is not None:
        surface_filter["$gte"] = surface[0]
    if surface[1] is not None:
        surface_filter["$lte"] = surface[1]
    if surface_filter:
        pipeline.append({"$match": {"prixmcarre bati": surface_filter}})

    pipeline.append({"$sample": {"size": 50}})
    pipeline.append({"$project": {
        "Département": "$Code departement",
        "Code Commune" : "$Code commune total",
        "Type" : "$Type local",
        "Pièces" : "$Nombre pieces principales",
        "Valeur": "$Valeur fonciere",
        "Surface bati": "$Surface reelle bati",
        "_id": 0
    }})
    
    result = list(collection.aggregate(pipeline))
    data = pd.DataFrame(result)
    if not data.empty:
        data['Nom Commune'] = data['Code Commune'].apply(get_commune_name)
        data = data.drop('Code Commune', axis=1)
    return data 

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
        return bar_chart("Nombre de transactions en fonction du département", pipeline, "_id", "count", "Code département", "Transactions", "linear")

    if arg == 'tbrop':
        pipeline = [
            {
                "$project": {
                    "_id": 0,
                    "categorie_prix": {
                        "$switch": {
                            "branches": [
                                {"case": {"$lte": ["$Valeur fonciere", 10000]}, "then": "0-10 000€"},
                                {"case": {"$lte": ["$Valeur fonciere", 50000]}, "then": "10 001-50 000€"},
                                {"case": {"$lte": ["$Valeur fonciere", 100000]}, "then": "50 001-100 000€"},
                                {"case": {"$lte": ["$Valeur fonciere", 200000]}, "then": "100 001-200 000€"},
                                {"case": {"$lte": ["$Valeur fonciere", 500000]}, "then": "200 001-500 000€"},
                                {"case": {"$lte": ["$Valeur fonciere", 1000000]}, "then": "500 001-1 000 000€"},
                                {"case": {"$gt": ["$Valeur fonciere", 1000000]}, "then": ">1 000 000€"}
                            ],
                            "default": "Unknown"
                        }
                    }
                }
            },
            {"$group": {"_id": "$categorie_prix", "count": {"$sum": 1}}}
        ]
        return pie_chart("Nombre de transactions en fonction du prix", pipeline, "_id", "count", "Prix", "Transactions")

    if arg == 'tbnom':
        pipeline = [
                    {"$group": {"_id": "$Nature mutation", "count": {"$sum": 1}}}
                ]
        return bar_chart("Nombre de transactions en fonction de la nature de la mutation", pipeline, "_id", "count", "Nature mutation", "Transactions", "log")

def prices(arg, price_per_sqm):
    if price_per_sqm:
        yaxis = "prixmcarre bati"
        ylabel = "Prix m² moyen"
        lowerThan = 20000
    else:
        yaxis = "Valeur fonciere"
        ylabel = "Valeur foncière moyenne"
        lowerThan = 20000000


    if arg == 'pbtol':
        pipeline = [
            {"$match": {yaxis: {"$exists": True, "$nin": [float('NaN'), float('Infinity')], "$lte" : lowerThan}}},
            {"$group": {"_id": "$Type local", "average_value": {"$avg": "$"+yaxis}}}
        ]
        return bar_chart(ylabel + " en fonction du type de local", pipeline, "_id", "average_value", "Local Type",ylabel, "linear")

    if arg == 'pbd':
        pipeline = [
            {"$match": {yaxis: {"$exists": True, "$nin": [float('NaN'), float('Infinity')], "$lte" : lowerThan}}},
            {"$group": {"_id": "$Code departement", "average_value": {"$avg": "$"+yaxis}}}
        ]
        return bar_chart(ylabel + " en fonction du département", pipeline, "_id", "average_value", "Department",ylabel, "linear")


    if arg == 'pbnom':
        pipeline = [
            {"$match": {yaxis: {"$exists": True, "$nin": [float('NaN'), float('Infinity')], "$lte" : lowerThan}}},
            {"$group": {"_id": "$Nature mutation", "average_value": {"$avg": "$"+yaxis}}}
        ]
        return bar_chart(ylabel + " en fonction de la nature de la mutation", pipeline, "_id", "average_value", "Nature de la mutation",ylabel, "linear")


    if arg == 'pbtos':
        pipeline = [
            {"$match": {yaxis: {"$exists": True, "$nin": [float('NaN'), float('Infinity')], "$lte" : lowerThan},
                        "Type de voie": {"$in": ['RUE', 'BD', 'AV', 'RTE', 'CHE']}}},
            {"$group": {"_id": "$Type de voie", "average_value": {"$avg": "$"+yaxis}}}
        ]
        return bar_chart(ylabel + " en fonction du type de voie", pipeline, "_id", "average_value", "Type de voie",ylabel, "linear")

    if arg== 'pbnor':
        pipeline = [
            {"$match": {yaxis: {"$exists": True, "$nin": [float('NaN'), float('Infinity')], "$lte" : lowerThan},
             "Nombre pieces principales" : {"$gt" : 0, "$lt" : 7}}},
            {"$group": {"_id": "$Nombre pieces principales", "average_value": {"$avg": "$"+yaxis}}}
        ]
        return bar_chart(ylabel + " en fonction du nombre de pièces", pipeline, "_id", "average_value", "Nombre de pièces",ylabel, "linear")


    result = list(collection.aggregate(pipeline))
    df_result = pd.DataFrame(result)
    df_result = df_result.sort_values(by='average_value', ascending=False)    

def maps(arg, depart):
    filtre = {"depart_id": depart}
    projection = {"type": 1, "features": 1, "_id": 0}
    geo =  db['GEO'].find_one(filtre, projection)

    if arg == 'price':
        if depart=="00" :
            pipeline = [
                {"$match": {"Valeur fonciere": {"$exists": True, "$ne": float('NaN'), "$lte" : 20000000}}},
                {"$group": {"_id": "$Code departement", "average_value": {"$avg": "$Valeur fonciere"}}}
            ]
            title = "Valeur foncière par département"
            label = "Valeur foncière"
        else:
            pipeline = [
                {"$match": {"Valeur fonciere": {"$exists": True, "$ne": float('NaN'), "$lte" : 20000000}, "Code departement": depart}},
                {"$group": {"_id": "$Code commune total", "average_value": {"$avg": "$Valeur fonciere"}}}
            ]  
            title = "Valeur foncière par commune dans le "+depart
            label = "Valeur foncière"

    if arg == 'smprice':
        if depart=="00" :
            pipeline = [
                {"$match": {"prixmcarre bati": {"$exists": True, "$nin": [float('NaN'), float('Infinity')],"$lte" : 20000}}},
                {"$group": {"_id": "$Code departement", "average_value": {"$avg": "$prixmcarre bati"}}}
            ]
            title = "Prix du m² par département"
            label = "Prix au m²"
        else:
            pipeline = [
                {"$match": {"prixmcarre bati": {"$exists": True, "$nin": [float('NaN'), float('Infinity')],"$lte" : 20000}, "Code departement": depart}},
                {"$group": {"_id": "$Code commune total", "average_value": {"$avg": "$prixmcarre bati"}}}
            ]  
            title = "Prix m² habitable par commune dans le "+depart
            label = "Prix au m²"

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

def correlation(arg):
    if arg == 'price':
        pop = pd.DataFrame(json.load(open('C:/Users/galla/Desktop/A5/CDS/Project/datas/json/pop.json', encoding='utf-8')))
        pipeline = [
            {"$match": {"prixmcarre bati": {"$exists": True, "$nin": [float('NaN'), float('Infinity')], "$lte" : 20000}}},
            {"$group": {"_id": "$Code departement", "Prix m² habitable": {"$avg": "$prixmcarre bati"}}}
        ]
        result = list(collection.aggregate(pipeline))
        price = pd.DataFrame(result)
        merged_df = pd.merge(price, pop, left_on='_id', right_on="Code departement", how='inner')
        merged_df = merged_df.sort_values(by='Population', ascending=False)    
        return scatter_plot("Prix du m² en fonction de la démographie, par département",merged_df, 'Code departement', 'Prix m² habitable', 'Population')

    if arg == 'surface':
            pop = pd.DataFrame(json.load(open('C:/Users/galla/Desktop/A5/CDS/Project/datas/json/pop.json', encoding='utf-8')))
            pipeline = [
                {"$match": {"Surface reelle bati": {"$exists": True, "$nin": [float('NaN'), float('Infinity')], "$lte" : 20000}}},
                {"$group": {"_id": "$Code departement", "Surface habitable": {"$avg": "$Surface reelle bati"}}}
            ]
            result = list(collection.aggregate(pipeline))
            price = pd.DataFrame(result)
            merged_df = pd.merge(price, pop, left_on='_id', right_on="Code departement", how='inner')
            merged_df = merged_df.sort_values(by='Population', ascending=False) 
            return scatter_3d_plot("Surface habitable en fonction de la démographie, par département",merged_df, 'Code departement', 'Surface habitable', 'Population')


def bar_chart(title, pipeline, xAxis, yAxis, xLabel, yLabel, type):
    color_scale = [[0, '#63318b'], [1, '#e4c3ff']] 
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

def scatter_plot(title, data, xaxis, yaxis, size):       
    color_scale = [[0, '#63318b'], [1, '#e4c3ff']] 
    fig = px.scatter(data, x=xaxis, y=yaxis,
                title = title,
                color=data[yaxis],
                color_continuous_scale=color_scale,
                size=size
            )

    fig.update_layout(
        paper_bgcolor='#1d232c',
        plot_bgcolor='#1d232c',
        font=dict(color='#83868b'),
        yaxis=dict(showgrid=False),
        xaxis=dict(showgrid=False)
    )
    fig.update_traces(marker_line_color="rgba(0,0,0,0)")
    return fig
    
def scatter_3d_plot(title, data, xaxis, yaxis, size):
    color_scale = [[0, '#63318b'], [1, '#e4c3ff']] 
    fig = px.scatter_3d(data, x=xaxis, y=yaxis, z=size,
                title = title,
                color=data[yaxis],
                color_continuous_scale=color_scale,
                size=size
            )

    fig.update_layout(
        paper_bgcolor='#1d232c',
        plot_bgcolor='#1d232c',
        font=dict(color='#83868b'),
        yaxis=dict(showgrid=False),
        xaxis=dict(showgrid=False)
    )
    fig.update_traces(marker_line_color="rgba(0,0,0,0)")
    return fig