from dash import dcc, html
from dash.dependencies import Input, Output
from dash import callback
import sys
sys.path.append("../")
from requests import prices

def generate_prices():
    return html.Div(className="container", children=[
        html.H1('Prix', className="page_title"),
        html.Div(className="choices_container", children=[dcc.Dropdown(id='prices_dropdown', className="dropdown",
            options=[
                {'label': 'Par type de local', 'value': 'pbtol'},
                {'label': 'Par département', 'value': 'pbd'},
                {'label': 'Par nature de mutation', 'value': 'pbnom'},
                {'label': 'Par type de voie', 'value': 'pbtos'},
                {'label': 'Par nombre de pièces', 'value' : 'pbnor'}
            ],
            value='pbtol'),
            dcc.RadioItems(
                id='price_per_sqm_checkbox',
                className="checkbox",
                options = [
                    {'label': 'Valeur foncière', 'value': 'fp'},
                    {'label': 'Prix au m²', 'value': 'smp'}
                ],
                value='fp',
                inline=True)
            ]),
            dcc.Loading(
                dcc.Graph(id='prices_graph', className="graph", figure=prices('pbtol', False)),
                parent_className="graph",
                type="dot",
                style={'width': '100%', 'margin': '20px auto'},
                color = '#dcdcdc',
                id='map_loading',  # Add an ID to the Loading component
            )])

@callback(
    Output('prices_graph', 'figure'),
    [Input('prices_dropdown', 'value'),
     Input('price_per_sqm_checkbox', 'value')]
)
def update_graph(selected_value, price_per_sqm):
    return prices(selected_value, price_per_sqm=='smp')
