# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from helper import parse_restyle
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
import json
import helper.parse_restyle

# ZM: make a callback for getting data from API
# We will need to filter for type separately from year/state, which go into the
# API call.
START_INDEX = 7
df = pd.read_csv('data/dummy_data.csv')
marks_dict = {}
for i in range(2005,2021):
    marks_dict[i] = str(i)


pc_fig = px.parallel_coordinates(df, color="aid",
                              dimensions=df.columns[START_INDEX:11])

layout = html.Div(children=[
    html.Div(className = 'filter-container',
        children=[
            html.Div(className ='filter-div', 
                children = [html.Label('Select a State'),
                    dcc.Dropdown(df['state'].unique(), 
                    df['state'].unique()[0:3], multi = True, id='state-dd')]),
            html.Div(className='filter-div',
                children = [html.Label('Select Disaster Type'),
                    dcc.Dropdown(df['disaster_type'].unique(), 
                    df['disaster_type'].unique()[0], multi = True, id='disaster-dd')]
            ),
            html.Div(className='filter-div',
                    children=[html.Label('Select X Axis Variable'),
                    dcc.Dropdown(df.columns[START_INDEX:11], 
                        df.columns[START_INDEX], id='xaxis-dd')] # ZM: update indexes once we have real data 
            )
        ]
    ),
    html.Br(),
    html.Label('Select Year Range'),
    dcc.RangeSlider(2005, 2020, 1, value=[2010, 2012], id='year-slider',
    marks = marks_dict),
    html.Br(),
    html.Div(children=[
        dcc.Graph(
            id='scatter-fig'
        )
    ]),
    html.Br(),
    html.Label('Select ranges along the parallel coordinates axes to highlight points in the scatter plot.'),
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
    Input('year-slider', 'value'),
    Input('disaster-dd', 'value'),
    Input('xaxis-dd', 'value'),
    Input('pc-fig', 'restyleData')
)
def update_figures(states, years, disasters, xaxis, restyleData):
    print('state', states)
    print('years',years)
    if not isinstance(states, list):
        states = [states]
    if not isinstance(years, list):
        years = [years]
    if not isinstance(disasters, list):
        disasters = [disasters]

    filtered_df = df[df['state'].isin(states) & 
        df['disaster_type'].isin(disasters) & 
        (df['year'] >= years[0]) &
        (df['year'] <= years[1])]

    scatter_fig = px.scatter(filtered_df, x=xaxis, y="aid",
        size="population", color="disaster_type", hover_name="county_id",
        size_max=60)
    
    if restyleData:
        dim_index, dim_range = parse_restyle.parse_restyle(restyleData)
        col_index = START_INDEX + dim_index
        print('col_index', col_index)
        print('dim_range',dim_range)

        selected_points = filtered_df[filtered_df[filtered_df.columns[col_index]]>=dim_range[0]].index.values
        print('selected_points', selected_points)
        scatter_fig.update_traces(selectedpoints = selected_points,
            unselected = {'marker': { 'opacity': 0.3 }})

    pc_fig = px.parallel_coordinates(filtered_df, color="aid",
                              dimensions=df.columns[START_INDEX:11]) #ZM: update indexes once we have full data

    scatter_fig.update_layout()

    return scatter_fig, pc_fig

# ZM: callback to highlight bubbles from parallelcoord selection
#@callback(
#    Output('restyle-data-pc', 'children'),#ZM: update output to bubble chart 
#    Input('pc-fig', 'restyleData'))
#def pc_highlight_scatter(restyleData):
#    if restyleData: # change this to if first key None or not
#        dim_index, dim_range = parse_restyle.parse_restyle(restyleData)
#        print('dim_index', dim_index)
#        print('range', dim_range)
#        #ZM: highlight bubbles here
#
#
#    #for d in restyleData:
#       # print('d', d)
#       # print('key',d.keys())
#       # print('values',d.values())
#    return json.dumps(restyleData, indent=2)
