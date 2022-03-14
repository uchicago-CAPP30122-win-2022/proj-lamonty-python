from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from pages import cross_section, detail_view 
from backend import datasets


app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.SANDSTONE])
server = app.server

load_figure_template('sandstone')
app.layout = html.Div([
    dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Cross-Section", href="/cross_section")),
        dbc.NavItem(dbc.NavLink("Deep Dive", href="/detail_view")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="FEMA Aid & Demographics",
    brand_href="#",
    color="primary",
    dark=True, 
    ),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/' or pathname == '/cross_section': # ZM: replace '/' gate with splash page?
        return cross_section.layout
    elif pathname == '/detail_view':
        return detail_view.layout # ZM: update name once's AR's view is in 
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)