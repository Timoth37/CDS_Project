from dash import dcc, html
from dash.dependencies import Input, Output
from dash import callback, callback_context, no_update
import sys
sys.path.append("../")
from requests import maps

currentDropdown = 'price'
currentDepart = '75'

def generate_maps():
    return html.Div(className="container", children=[
        html.H1('L\'immobilier en carte', className="page_title"),
        dcc.Dropdown(id='maps_dropdown', className="dropdown",
            options=[
                {'label': 'Valeur foncière', 'value': 'price'},
                {'label': 'Prix au m²', 'value': 'smprice'},
                {'label': 'Surface habitable', 'value': 'surfliveable'},
            ],
            value='price'),
        html.Div(className="map_container", children=[
            dcc.Loading(
                dcc.Graph(id='france_map', figure=maps(currentDropdown, '00')),
                parent_className="map_graph",
                type="dot",
                style={'width': '100%', 'margin': '20px auto'},
                color = '#dcdcdc',
                id='map_loading',  # Add an ID to the Loading component
            ),
            dcc.Loading(
                dcc.Graph(id='depart_map', figure=maps(currentDropdown, currentDepart)),
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
    global currentDepart
    global currentDropdown
    ctx = callback_context
    if ctx.triggered_id == 'maps_dropdown':
        currentDropdown = selected_value
        main_map = maps(currentDropdown, '00')
        detailed_map = maps(currentDropdown, currentDepart)
        return main_map, detailed_map
    elif ctx.triggered_id == 'france_map':
        currentDepart = click_data['points'][0]['location']
        detailed_map = maps(currentDropdown, currentDepart)
        return no_update, detailed_map
    else:
        return no_update, no_update
