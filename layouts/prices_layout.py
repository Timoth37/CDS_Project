from dash import dcc, html
from dash.dependencies import Input, Output
from dash import callback
import sys
sys.path.append("../")
from requests import prices

def generate_prices():
    return html.Div(className="container", children=[
        html.H1('Prices Statistics', className="page_title"),
        html.Div(className="choices_container", children=[dcc.Dropdown(id='prices_dropdown', className="dropdown",
            options=[
                {'label': 'By type of local', 'value': 'pbtol'},
                {'label': 'By department', 'value': 'pbd'},
                {'label': 'By nature of mutation', 'value': 'pbnom'},
                {'label': 'By type of street', 'value': 'pbtos'}
            ],
            value='pbtol'),
            dcc.RadioItems(
                id='price_per_sqm_checkbox',
                className="checkbox",
                options = [
                    {'label': 'Full Price', 'value': 'fp'},
                    {'label': 'Square Meter Price', 'value': 'smp'}
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
