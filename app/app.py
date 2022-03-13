from dash import Dash, dcc, html, Input, Output, callback
from pages import cross_section, detail_view #ZM: Update detail_view once AR's view is in


app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    print(pathname)
    if pathname == '/' or pathname == '/cross_section': # ZM: replace '/' gate with splash page?
        return cross_section.layout
    elif pathname == '/detail_view':
        return detail_view.layout # ZM: update name once's AR's view is in 
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)