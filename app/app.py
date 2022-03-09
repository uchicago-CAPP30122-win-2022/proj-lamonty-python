# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
import plotly.express as px
from helper.gen_table import generate_table
import pandas as pd

app = Dash(__name__)

colors = {
    'background': '#ecf0f1',
    'text': '#af7ac5  '
}

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

df = pd.read_csv('dummy_data.csv')
counties = df['county_id'].unique()

fig_bar = px.bar(df, x="dc_id", y="aid", color='dem_rep', barmode="group")

fig_bar.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

fig_scatter = px.scatter(df, x="pcnt_white", y="aid",
                size="population", color="county_id", hover_name="county_id",
                size_max=60)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='(la)Monty Python Dash Template',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Dash: A web application framework for your data.',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    html.Div(children=[
        html.Label('Dropdown'),
        dcc.Dropdown(counties, counties[0], multi = True)
    ]),

    html.Div(children=[
        dcc.Graph(
        id='bar-graph',
        figure=fig_bar
        ),
        dcc.Graph(
            id='scatter-graph',
            figure=fig_scatter
        )
    ]),


    html.H3(children='A table of dummy data',
        style={
        'textAlign': 'center',
        'color': colors['text']
        }
    ),
    generate_table(df)
])

if __name__ == '__main__':
    app.run_server(debug=True)