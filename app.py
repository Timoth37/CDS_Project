import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd


import sys
sys.path.append("layouts")
# Import les layout
from overview_layout import generate_overview

# Import les requests
from requests import global_infos
from requests import type_loc_graph

# Mise en page du dashboard
app = dash.Dash(__name__)

app.layout = html.Div(className="body", children=[
    # Menu vertical
    html.Div(className="menu", children=[
        html.H3('Real Estate in France 2022', className="menu_title"),
        dcc.Link('Overview', className="menu_button", href='/overview'),
        dcc.Link('Classic', className="menu_button", href='/classic'),
        dcc.Link('Map', className="menu_button", href='/map'),
        dcc.Link('Test', className="menu_button", href='/test1'),
        dcc.Link('Test', className="menu_button", href='/test2'),
        dcc.Link('About', className="menu_button", href='/about'),
    ]),

    # Contenu principal
    html.Div(className="page", children=[
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content', className="page_content")
    ])
])

# Callback pour mettre à jour le contenu en fonction de l'URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        globalInfos = global_infos()
        return html.Div(className="main", children=[generate_overview(round(globalInfos['mean_value'], 2), round(globalInfos['max_value']), round(globalInfos['mean_surface_terrain']), round(globalInfos['mean_surface_bati']))])
    
    if pathname == '/overview':
        globalInfos = global_infos()
        return html.Div(className="main", children=[generate_overview(round(globalInfos['mean_value'], 2), round(globalInfos['max_value']), round(globalInfos['mean_surface_terrain']), round(globalInfos['mean_surface_bati']))])

    if pathname == '/classic':
        typeLocGraph = type_loc_graph()
        return html.Div(className="main", children=typeLocGraph)
    else:
        return '404 Page Not Found'

if __name__ == '__main__':
    app.run_server(debug=True)
