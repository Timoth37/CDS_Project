import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import sys

sys.path.append("layouts")
# Import les layout
from transac_layout import generate_transac
from search_layout import generate_search
from prices_layout import generate_prices
from maps_layout import generate_maps
from overview_layout import generate_overview

# Mise en page du dashboard
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div(className="body", children=[
    # Menu vertical
    html.Div(className="menu", children=[
        dcc.Link( className="home_button", children=[html.H2('Immobilier en France 2022', className="menu_title")], href='/'),
        dcc.Link('Recherche', className="menu_button", href='/search'),
        dcc.Link('Volumes', className="menu_button", href='/transac'),
        dcc.Link('Prix', className="menu_button", href='/prices'),
        dcc.Link('Cartes', className="menu_button", href='/maps'),
        dcc.Link('Corrélation', className="menu_button", href='/correlation'),
        dcc.Link('A propos', className="menu_button", href='/about'),
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
        return generate_overview()
    
    if pathname == '/search':
        return generate_search()

    if pathname == '/transac':
        return generate_transac()
    
    if pathname =="/prices":
        return generate_prices()
    
    if pathname=='/maps':
        return generate_maps()

    else:
        return '404 Page Not Found'

if __name__ == '__main__':
    app.run_server(debug=True)
