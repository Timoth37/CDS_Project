from dash import html
import sys
sys.path.append("../")
from requests import global_infos


def generate_overview():
    global departList
    result = global_infos()
    meanPrice = round(result['mean_value'])
    maxPrice = round(result['max_value'])
    meanField = round(result['mean_surface_field'])
    meanLiveable = round(result['mean_surface_liveable'])

    return html.Div(className="container", children=[
        html.H1(children='Résumé', className="page_title"),
        html.Div(className="bubble_container", children=[
            html.Div(className= "bubble", children=[
                html.H3('Moyenne Valeur Foncière', className="bubble_title"),
                html.P(f"{meanPrice:,}  €".replace(',','  '), className="bubble_text")
            ]),
            html.Div(className="bubble", children=[
                html.H3('Valeur Foncière Maximale', className="bubble_title"),
                html.P(f"{maxPrice:,}  €".replace(',','  '), className="bubble_text")
            ]),
            html.Div(className="bubble", children=[
                html.H3('Moyenne Surface Terrain', className="bubble_title"),
                html.P(f"{meanField:,}  m²".replace(',','  '), className="bubble_text")
            ]),
            html.Div(className="bubble", children=[
                html.H3('Moyenne Surface Réelle Bâtie', className="bubble_title"),
                html.P(f"{meanLiveable:,}  m²".replace(',','  '), className="bubble_text")
            ]),
        ])
    ])