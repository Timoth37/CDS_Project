from dash import dcc, html
from dash.dependencies import Input, Output
from dash import callback
import sys
sys.path.append("../")
from requests import correlation

def generate_corr():
    return html.Div(className="container", children=[
            html.H1('Corrélations', className="page_title"),
            dcc.Dropdown(id='corr_dropdown', className="dropdown",
                options=[
                    {'label': 'Prix m² et population', 'value': 'price'},
                    {'label': 'Surface habitable et population', 'value' : 'surface'}
                ],
                value='price'
            ),
            dcc.Loading(
                dcc.Graph(id='corr_graph', className="graph", figure=correlation('price')),
                parent_className="graph",
                type="dot",
                style={'width': '100%', 'margin': '20px auto'},
                color = '#dcdcdc',
                id='map_loading')
            ])

@callback(
    Output('corr_graph', 'figure'),
    Input('corr_dropdown', 'value')
)
def update_graph(selected_value):
    return correlation(selected_value)
