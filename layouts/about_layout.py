from dash import html


def generate_about():
    return html.Div(className="container", children=[
        html.H1(children='A propos', className="page_title"),
        html.P(className='about', children='''Ce projet a été réalisé dans le cadre du cours \'Cloud Data Structure\' en 5ème année à l\'ESILV.
                Il cloture le module. Le travail consiste en un Dashboard interactif permettant une analyse des données
                relatives aux demandes de valeurs foncières de l'année 2021 en France.\n
               Travail réalisé par TEIXEIRA David, MOUTY Guillaume et GALLAIS Timothée'''),
    ])