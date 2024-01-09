from dash import html, dcc, callback, Input, Output, State
from dash import no_update, dash_table
import sys
sys.path.append("../")
from requests import global_infos
from requests import get_commune_list
from requests import full_search

departList = {
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

def generate_search():
    global departList
    return html.Div(className="container", children=[
        html.H1(children='Recherche', className="page_title"),
        html.Div(className='search_container', children=[
            html.Div(className='filters_container', children=[
                html.Div(className="filters_dropdown", children=[
                    dcc.Dropdown(
                        id="type_dropdown",
                        className="filters_dropdown_item",
                        options=[
                            {'label': 'Appartement', 'value': 'Appartement'},
                            {'label': 'Maison', 'value': 'Maison'},
                            {'label': 'Local commercial', 'value': 'Local industriel. commercial ou assimilé'},
                        ],
                        placeholder="Type"
                                           
                    ),
                    dcc.Dropdown(
                        id="rooms_dropdown",
                        className="filters_dropdown_item",
                        options=[
                            {'label': 'T1', 'value': 1},
                            {'label': 'T2', 'value': 2},
                            {'label': 'T3', 'value': 3},
                            {'label': 'T4', 'value': 4},
                            {'label': 'T5', 'value': 5},
                            {'label': '>T5', 'value': '+'}
                        ],
                        placeholder="Pièces"
                    ),
                    dcc.Dropdown(
                        id="depart_dropdown",
                        className="filters_dropdown_item",
                        options= [{'label' : code + " : " +name, 'value' : code} for code, name in departList.items()],
                        placeholder='Département'
                    ),
                   dcc.Dropdown(
                       id="commune_dropdown",
                        className="filters_dropdown_item",
                        options=[],
                        placeholder='Commune'
                    )
                ]),
                html.Div(className='rangeslider', children=[
                    html.H3('Prix'),
                    dcc.RangeSlider(
                        id='price_slider',
                        min=2,
                        max=6,
                        marks={i: f"{10**i:,}" for i in range(2, 7)},
                        value=[None, None],
                        dots=False,
                        step=0.01,
                        updatemode='drag',
                    ),
                    html.P(id='price_slider_output', children=update_price_slider_output([None,None]))
                ]),
                html.Div(className='rangeslider', children=[
                    html.H3('Surface Habitable'),
                    dcc.RangeSlider(
                        id='surface_slider',
                        min=0,
                        max=3,
                        marks={i: f"{10**i:,}" for i in range(4)},
                        value=[None, None],
                        dots=False,
                        step=0.01,
                        updatemode='drag'         
                    ),
                    html.P(id='surface_slider_output', children=update_surface_slider_output([None,None]))
                ]),
                html.Div(className='button_container', children=[
                    html.Button('Réinitialiser', id='btn_reinit',className='button', n_clicks=0),
                    html.Button('Chercher', id='btn_search', className='button', n_clicks=0),
                ]),
                dcc.Loading(children=[
                            dash_table.DataTable(data = [], 
                            columns=[{"name": i, "id": i} for i in []], 
                            id='datatable',
                            page_size=10,
                            style_header={
                                'backgroundColor': '#63318b',
                                'fontWeight': 'bold',
                                'color' : '#dcdcdc'
                            },
                            style_cell={
                                'textAlign': 'left'
                            },
                            style_data={
                                'color': '#dcdcdc',
                                'backgroundColor': '#1d232c'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': '#1d2229',
                                }
                            ],
                            style_as_list_view=True
                        )
                    ],
                    parent_className="graph",
                    type="dot",
                    style={'width': '100%', 'margin': '20px auto'},
                    color = '#dcdcdc',
                    id='search_loading', 
                )
            ])
        ])
    ])


@callback(
     Output('surface_slider_output', 'children'),
     Input('surface_slider', 'value')
)
def update_surface_slider_output(surface_value):
    if(surface_value != [None, None]):
        return f"{round(10**surface_value[0]):,} - {round(10**surface_value[1]):,} m²"
    else: 
        return f"  -   m²"


@callback(
    Output('price_slider_output', 'children'),
    Input('price_slider', 'value')
)
def update_price_slider_output(price_value):
    if(price_value != [None, None]):
        return f"{round(10**price_value[0]):,} - {round(10**price_value[1]):,} €"
    else: 
        return f"  -   €"

@callback(
    [Output('commune_dropdown', 'options'),
     Output('commune_dropdown', 'disabled')],
    [Input('depart_dropdown', 'value')]
)
def update_commune_dropdown(selected_depart):
    if selected_depart is None:
        return [], True
    else:
        commune_code = selected_depart
        test = [{'label' : commune['name'], 'value' : commune['code']} for commune in get_commune_list(commune_code)]
        return test, False
    
@callback(
    Output('datatable', 'data'),
    Output('datatable', 'columns'),
    Input('btn_search', 'n_clicks'),
    State('type_dropdown', 'value'),
    State('rooms_dropdown', 'value'),
    State('depart_dropdown', 'value'),
    State('commune_dropdown', 'value'),
    State('price_slider', 'value'),
    State('surface_slider', 'value'),
    prevent_initial_call=True
)
def btn_click(n_clicks, type, rooms, depart, commune, price, surface):
    if type==None and rooms==None and depart==None and commune==None and price == [None, None] and surface == [None, None] : 
        return [], [{"name": i, "id": i} for i in []]
    
    datatable = full_search(type, rooms, depart, commune, [10**i if i is not None else None for i in price], [10**j if j is not None else None for j in surface])
    if datatable.empty:
        return [], [{"name": i, "id": i} for i in []]
    return datatable.to_dict('records'), [{"name": i, "id": i} for i in datatable.columns]



@callback(
    [Output('type_dropdown', 'value'),
    Output('rooms_dropdown', 'value'),
    Output('depart_dropdown', 'value'),
    Output('commune_dropdown', 'value'),
    Output('price_slider', 'value'),
    Output('surface_slider', 'value'),
    Output('datatable', 'data', allow_duplicate=True)],
    [Input('btn_reinit', 'n_clicks')],
    prevent_initial_call=True
)
def reinit(n_clicks):
    return None, None, None, None, [None, None], [None,None], []


@callback(
    [Output('btn_search','disabled'),
    Output('btn_reinit', 'disabled')],
    [Input('type_dropdown', 'value'),
    Input('rooms_dropdown', 'value'),
    Input('depart_dropdown', 'value'),
    Input('commune_dropdown', 'value'),
    Input('price_slider', 'value'),
    Input('surface_slider', 'value')]
)
def btn_status(type, rooms, depart, commune, price, surface):
    if type==None and rooms==None and depart==None and commune==None and price == [None, None] and surface == [None, None] : 
        return True, True
    else:
        return False, False
    
