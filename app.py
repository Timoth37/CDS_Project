import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import math
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

app.layout = html.Div(children=[
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback pour mettre à jour le contenu en fonction de l'URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        globalInfos = global_infos()
        typeLocGraph = type_loc_graph()
        
        return html.Div(className="body", children=[generate_overview(round(globalInfos['mean_value'], 2), 
                                 globalInfos['max_value'], 
                                 round(globalInfos['mean_surface_terrain']), 
                                 round(globalInfos['mean_surface_bati'])), typeLocGraph])
                                  # Importez la mise en page spécifique pour l'aperçu
    else:
        return '404 Page Not Found'

if __name__ == '__main__':
    app.run_server(debug=True)
