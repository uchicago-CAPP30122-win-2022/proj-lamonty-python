# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
import json

# ZM: make a callback for getting data from API
# We will need to filter for type separately from year/state, which go into the
# API call.
df = pd.read_csv('dummy_data.csv')


pc_fig = px.parallel_coordinates(df, color="aid",
                              dimensions=df.columns[7:11])

layout = html.Div(children=[
    html.Div(className = 'filter-container',
        children=[
            html.Div(className ='filter-div', 
                children = [html.Label('Select a State'),
                    dcc.Dropdown(df['state'].unique(), 
                    df['state'].unique()[0:3], multi = True, id='state-dd')]),
            html.Div(className='filter-div',
                children = [html.Label('Select a Year'),
                    dcc.Dropdown(df['year'].unique(), 
                    df['year'].unique()[0], multi = True, id='year-dd')]),
            html.Div(className='filter-div',
                children = [html.Label('Select Disaster Type'),
                    dcc.Dropdown(df['disaster_type'].unique(), 
                    df['disaster_type'].unique()[0], multi = True, id='disaster-dd')]
            ),
            html.Div(className='filter-div',
                    children=[html.Label('Select X Axis Variable'),
                    dcc.Dropdown(df.columns[7:11], df.columns[7], id='xaxis-dd')] # ZM: update indexes once we have real data 
            )
        ]
    ),
    html.Br(),
    html.Div(children=[
        dcc.Graph(
            id='scatter-fig'
        )
    ]),
    html.Br(),
    html.Div(children=[
        dcc.Graph(
            id='pc-fig',
            figure=pc_fig
        )
    ]),
     html.Div([
            dcc.Markdown("""
                **Restyle Data**
                Print out for testing purposes. 
            """),
            html.Pre(id='restyle-data-pc')
        ])
])


@callback(
    Output('scatter-fig', 'figure'),
    Output('pc-fig', 'figure'),
    Input('state-dd', 'value'),
    Input('year-dd', 'value'),
    Input('disaster-dd', 'value'),
    Input('xaxis-dd', 'value')
)
def update_scatter(states, years, disasters, xaxis):
    if not isinstance(states, list):
        states = [states]
    if not isinstance(years, list):
        years = [years]
    if not isinstance(disasters, list):
        disasters = [disasters]

    filtered_df = df[df['state'].isin(states) & 
        df['disaster_type'].isin(disasters) & 
        df['year'].isin(years)]

    scatter_fig = px.scatter(filtered_df, x=xaxis, y="aid",
        size="population", color="disaster_type", hover_name="county_id",
        size_max=60)

    pc_fig = px.parallel_coordinates(filtered_df, color="aid",
                              dimensions=df.columns[7:11]) #ZM: update indexes once we have full data

    scatter_fig.update_layout()

    return scatter_fig, pc_fig

# ZM: callback to print out restyle for testing purposes. 
@callback(
    Output('restyle-data-pc', 'children'),
    Input('pc-fig', 'restyleData'))
def pc_highlight_scatter(restyleData):
    #print('restyleData', restyleData)
    #for d in restyleData:
       # print('d', d)
       # print('key',d.keys())
       # print('values',d.values())
    return json.dumps(restyleData, indent=2)
