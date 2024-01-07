from dash import dcc, html
from dash.dependencies import Input, Output
from dash import callback
import sys
sys.path.append("../")
from requests import transac

def generate_transac():
    return html.Div(className="container", children=[
        html.H1('Transactions Statistics', className="page_title"),
        dcc.Dropdown(id='classic_dropdown', className="dropdown",
            options=[
                {'label': 'By type of local', 'value': 'tbtol'},
                {'label': 'By department', 'value': 'tbd'},
                {'label': 'By range of price', 'value': 'tbrop'},
                {'label': 'By nature of mutation', 'value': 'tbnom'}
            ],
            value='tbtol'),  
        dcc.Graph(id='classic_graph', className="graph", figure=transac('tbtol'))])

@callback(
    Output('classic_graph', 'figure'),
    [Input('classic_dropdown', 'value')]
)
def update_graph(selected_value):
    return transac(selected_value)
