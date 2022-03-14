# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from helper import parse_restyle
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
import json
import helper.parse_restyle

START_INDEX = 7 #ZM: Update index 
START_YEAR = 2010
END_YEAR = 2019
df = pd.read_csv('dummy_data.csv')
marks_dict = {}
for i in range(START_YEAR, END_YEAR + 1):
    marks_dict[i] = str(i)

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
    dcc.RangeSlider(START_YEAR, END_YEAR, 1, value=[2010, 2012], id='year-slider',
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
            id='pc-fig'
        )
    ]),
     html.Div([
            dcc.Markdown("""
                **Restyle Data**
                Print out for testing purposes. 
            """),
            html.Pre(id='restyle-data-pc')
        ]),
    dcc.Store(id='query-data'),
    dcc.Store(id='intermediate-value')
])

@callback(
    Output('query-data', 'data'),
    Input('state-dd', 'value'),
    Input('year-slider', 'value')
)
def query_api(states, years): #ZM: placeholder callback, update with actual API
    if not isinstance(states, list):
        states = [states]
    if not isinstance(years, list):
        years = [years]
    # ZM: actual API should be called below instead of referencing df read in by
    # pandas.
    query_df = df[df['state'].isin(states) & 
        (df['year'] >= years[0]) &
        (df['year'] <= years[1])]
    
    return query_df.to_json(date_format='iso', orient='split')

@callback(
    Output('pc-fig', 'figure'),
    Output('intermediate-value', 'data'),
    Input('query-data','data'),
    Input('disaster-dd', 'value'),
)
def update_pc_and_data(query_df_json, disasters):
    query_df = pd.read_json(query_df_json, orient='split')
    if not isinstance(disasters, list):
        disasters = [disasters]

    filtered_df = query_df[query_df['disaster_type'].isin(disasters)]
    
    pc_fig = px.parallel_coordinates(filtered_df, color="aid",
                              dimensions=filtered_df.columns[START_INDEX:11]) #ZM: update indexes once we have full data

    return pc_fig, filtered_df.to_json(date_format='iso', orient='split')


@callback(
    Output('scatter-fig', 'figure'),
    Input('pc-fig', 'restyleData'),
    Input('intermediate-value', 'data'),
    Input('xaxis-dd', 'value')
)
def pc_highlight_scatter(restyleData, filtered_df_json, xaxis):
    filtered_df = pd.read_json(filtered_df_json, orient='split')
    scatter_fig = px.scatter(filtered_df, x=xaxis, y="aid",
        size="population", color="disaster_type", hover_name="county_id",
        size_max=60)
    #ZM: only handles dim_range of length one and doesn't support multiple axes
    # some stateful way to track range selection history?
    if restyleData and None not in restyleData[0].values():
        print('restyleData', list(restyleData[0].values()))
        dim_index, dim_range = parse_restyle.parse_restyle(restyleData)
        col_index = START_INDEX + dim_index
        #print('col_index', col_index)
        #print('dim_range',dim_range)

        selected_points = filtered_df[(filtered_df[filtered_df.columns[col_index]]>=dim_range[0]) &
            (filtered_df[filtered_df.columns[col_index]]<=dim_range[1])].index.values
        #print('selected_points', selected_points)
        scatter_fig.update_traces(selectedpoints = selected_points,
            unselected = {'marker': { 'opacity': 0.15 }})

    scatter_fig.update_layout()
    return scatter_fig
