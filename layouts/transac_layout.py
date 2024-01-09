from dash import dcc, html
from dash.dependencies import Input, Output
from dash import callback
import sys
sys.path.append("../")
from requests import transac

def generate_transac():
    return html.Div(className="container", children=[
        html.H1('Volumes', className="page_title"),
        dcc.Dropdown(id='transac_dropdown', className="dropdown",
            options=[
                {'label': 'Par type de local', 'value': 'tbtol'},
                {'label': 'Par département', 'value': 'tbd'},
                {'label': 'Par niveaux de prix', 'value': 'tbrop'},
                {'label': 'Par type de mutation', 'value': 'tbnom'}
            ],
            value='tbtol'),  
        dcc.Loading(
            dcc.Graph(id='transac_graph', className="graph", figure=transac('tbtol')),
            parent_className="graph",
            type="dot",
            style={'width': '100%', 'margin': '20px auto'},
            color = '#dcdcdc',
            id='map_loading',  # Add an ID to the Loading component
        )])

@callback(
    Output('transac_graph', 'figure'),
    [Input('transac_dropdown', 'value')]
)
def update_graph(selected_value):
    return transac(selected_value)
