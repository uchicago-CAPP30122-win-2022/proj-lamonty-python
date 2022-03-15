# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from helper import parse_restyle
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
import json
import helper.parse_restyle

START_IV_IDX = 0 #ZM: Update index 
END_IV_IDX = 14
DV_NAME = 'aid_per_capita'
START_YEAR = 2010
END_YEAR = 2019
df = pd.read_csv('data/dummy_data.csv')
marks_dict = {}
for i in range(START_YEAR, END_YEAR + 1):
    marks_dict[i] = str(i)

layout = html.Div(children=[
    html.Div(className = 'filter-container',
        children=[
            html.Div(className ='filter-div', 
                children = [html.Label('Select a State'),
                    dcc.Dropdown(df['state'].unique(), 
                    df['state'].unique()[0:3], multi = True, id='state-dd')]),#ZM: replace with state name from JSON
            html.Div(className='filter-div',
                children = [html.Label('Select Disaster Type'),
                    dcc.Dropdown(df['incident_type'].unique(), 
                    df['disaster_type'].unique()[0], multi = True, id='disaster-dd')]
            ),
            html.Div(className='filter-div',
                    children=[html.Label('Select X Axis Variable'),
                    dcc.Dropdown(df.columns[START_IV_IDX:END_IV_IDX], 
                        df.columns[START_IV_IDX], id='xaxis-dd')] # ZM: update indexes once we have real data 
            )
        ]
    ),
    html.Br(),
    html.Label('Select Year Range'),
    dcc.RangeSlider(START_YEAR, END_YEAR, 1, value=[START_YEAR, START_YEAR + 2], 
        id='year-slider',
        marks = marks_dict
    ),
    html.Br(),
    html.Div(children=[
        dcc.Graph(
            id='scatter-fig'
        )
    ]),
    html.Br(),
    html.Label('Select a range along a parallel coordinates axis to highlight points in the scatter plot.'),
    html.Div(id='pc-container', children=[
        html.Div(className='buffer'),
        html.Div(id='pc-plot',children=[
            dcc.Graph(
            id='pc-fig'
        )
        ]),
        html.Div(className='buffer')
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
    '''
    Load data from FEMA and ACS APIs into app using backend modules and user
    inputs for states and years. Data is used for all visuals on cross-section
    view.

    Inputs:
        states: a list of state names selected from the states dropdown in ui
        years: a list of years selected from the years slider in ui

    Outputs:
        Joined data from FEMA and ACS data sources meeting input filter criteria,
        converted to JSON for in-browser storage.
    '''
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
    '''
    Filter the data returned by API call further based on user inputs for
    specific disaster types.

    Inputs:
        query_df_json: json file from browser memory, originally created by FEMA
            and ACS API call
        disasters: a list of disaster types selected by user from ui dropdown
    
    Outputs:
        pc_fig: a Dash parallel coorinates component
        filtered_df: a filtered version of the original API query, which feeds
        into the parallel coordinates and scatter plot graphs, converted to
            JSON for in-browser storage
    '''
    query_df = pd.read_json(query_df_json, orient='split')
    if not isinstance(disasters, list):
        disasters = [disasters]

    filtered_df = query_df[query_df['disaster_type'].isin(disasters)]
    
    pc_fig = px.parallel_coordinates(filtered_df, color="aid_per_capita",
                              dimensions=filtered_df.columns[START_IV_IDX:END_IV_IDX]) #ZM: update indexes once we have full data

    pc_fig.update_layout(margin = dict(l = 25))

    return pc_fig, filtered_df.to_json(date_format='iso', orient='split')

@callback(
    Output('scatter-fig', 'figure'),
    Input('pc-fig', 'restyleData'),
    Input('intermediate-value', 'data'),
    Input('xaxis-dd', 'value')
)
def modify_scatter(restyleData, filtered_df_json, xaxis):
    '''
    Modify the scatter plot based on user selections for x-axis variable and 
    highlighted data ranges in the parallel coordinates plot. 

    Inputs:
        restyleData: range of user selection from interactive parallel
            coordinates plot
        filtered_df_json: json file from browser memory, created by
            update_pc_and_data callback
        xaxis: the variable selected by user from ui dropdown to display on
            scatterplot x-axis

    Outputs:
        scatter_fig: a Dash scatterplot component
    '''
    filtered_df = pd.read_json(filtered_df_json, orient='split')
    scatter_fig = px.scatter(filtered_df, x=xaxis, y="aid_per_capita",
        size="population", color="disaster_type", hover_name="county_fips",
        size_max=60)
    #ZM: only handles dim_range of length one and doesn't support multiple axes
    # some stateful way to track range selection history?
    if restyleData and None not in restyleData[0].values():
        #print('restyleData', list(restyleData[0].values()))
        dim_index, dim_range = parse_restyle.parse_restyle(restyleData)
        col_index = START_IV_IDX + dim_index
        #print('col_index', col_index)
        #print('dim_range',dim_range)

        selected_points = filtered_df[(filtered_df[filtered_df.columns[col_index]]>=dim_range[0]) &
            (filtered_df[filtered_df.columns[col_index]]<=dim_range[1])].index.values
        #print('selected_points', selected_points)
        scatter_fig.update_traces(selectedpoints = selected_points,
            unselected = {'marker': { 'opacity': 0.15 }})

    scatter_fig.update_layout()
    return scatter_fig
