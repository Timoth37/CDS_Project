from dash import dcc, html
from dash.dependencies import Input, Output
from dash import callback
import sys
sys.path.append("../")
from requests import maps


def generate_maps():
    return html.Div(className="container", children=[
        html.H1('Maps Statistics', className="page_title"),
        dcc.Dropdown(id='maps_dropdown', className="dropdown",
            options=[
                {'label': 'Price', 'value': 'price'},
                {'label': 'Meter Square Price', 'value': 'smprice'},
                {'label': 'Liveable Surface', 'value': 'surfliveable'},
            ],
            value='price'),
        html.Div(className="map_container", children=[
            dcc.Graph(id='france_map', className="map_graph", figure=maps('price', '00')),
            dcc.Loading(
                dcc.Graph(id='depart_map', figure=maps('price', '75')),
                parent_className="map_graph",
                type="dot",
                style={'width': '100%', 'margin': '20px auto'},
                color = '#dcdcdc',
                id='depart_map_loading',  # Add an ID to the Loading component
            )])
        ])

@callback(
    [Output('france_map', 'figure'),
     Output('depart_map', 'figure')],
    [Input('maps_dropdown', 'value'),
     Input('france_map', 'clickData')]
)
def update_graph(selected_value, click_data):
    main_map = maps(selected_value, "00")
    detailed_map = maps(selected_value, "75")
    
    if click_data:
        department_code = click_data['points'][0]['location']
        detailed_map = maps(selected_value, department_code)

    return main_map, detailed_map
