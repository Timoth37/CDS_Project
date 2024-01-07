from dash import dcc, html
from dash.dependencies import Input, Output
from dash import callback
import sys
sys.path.append("../")
from requests import maps

def generate_maps():
    return html.Div(className="container", children=[
        html.H1('Maps Statistics', className="page_title"),
        dcc.Dropdown(id='classic_dropdown', className="dropdown",
            options=[
                {'label': 'Price', 'value': 'price'},
                {'label': 'Meter Square Price', 'value': 'msprice'}
            ],
            value='price'),  
        dcc.Graph(id='classic_graph', className="graph", figure=maps('price'))])

@callback(
    Output('maps_graph', 'figure'),
    [Input('maps_dropdown', 'value')]
)
def update_graph(selected_value):
    return maps(selected_value)
