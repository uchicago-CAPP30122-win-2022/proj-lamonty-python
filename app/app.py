# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output
import plotly.express as px
from helper.gen_table import generate_table
import pandas as pd

app = Dash(__name__)

colors = {
    'background': 'white',
    'text': '#af7ac5  '
}

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

df = pd.read_csv('dummy_data.csv')


fig_bar = px.bar(df, x="dc_id", y="aid", color='dem_rep', barmode="group")

fig_bar.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='(la)Monty Python Dash Template',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children=[
        html.Label('Select a State'),
        dcc.Dropdown(df['state'].unique(), 
            df['state'].unique()[0:3], multi = True, id='state-dd'),
        html.Label('Select a Year'),
        dcc.Dropdown(df['year'].unique(), 
            df['year'].unique()[0], multi = True, id='year-dd'),
        html.Label('Select Disaster Type'),
        dcc.Dropdown(df['disaster_type'].unique(), 
            df['disaster_type'].unique()[0], multi = True, id='disaster-dd'),
        html.Label('Select X Axis Variable'),
        dcc.Dropdown(df.columns[7:11], df.columns[7], id='xaxis-dd')
    ]),

    html.Div(children=[
        dcc.Graph(
            id='scatter-fig'
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


@app.callback(
    Output('scatter-fig', 'figure'),
    Input('state-dd', 'value'),
    Input('year-dd', 'value'),
    Input('disaster-dd', 'value'),
    Input('xaxis-dd', 'value')
)
def update_figures(states, years, disasters, xaxis):
    # print('states',states)
    if not isinstance(states, list):
        states = [states]
    if not isinstance(years, list):
        years = [years]
    if not isinstance(disasters, list):
        disasters = [disasters]

    filtered_df = df[df['state'].isin(states) & 
                    df['disaster_type'].isin(disasters) & 
                    df['year'].isin(years)]

    fig = px.scatter(filtered_df, x=xaxis, y="aid",
                size="population", color="disaster_type", hover_name="county_id",
                size_max=60)

    fig.update_layout()

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)