import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output, callback
from backend import datasets
from utils import utils

counties, winner, hurricane_path, hurricane_scope, hurricanes = utils.detail_view_init()

layout = html.Div(children=[
    html.Div(children=[
        html.Label('Hurricane'),
        dcc.Dropdown(hurricanes, hurricanes[0], multi = False, id='hurricane')
    ]),

 html.Div([
    dcc.Graph(id='hurricane_map')
  ])
])

@callback(
    Output("hurricane_map", "figure"),
    Input('hurricane', 'value')
)
def display_hurricane(hurricane):
  hurricane_df = hurricane_path.loc[(hurricane_path['NAME'] == hurricane)]
  api_data = datasets.get_data(hurricane_scope[hurricane]["states_fips"], hurricane_scope[hurricane]["year"])
  year_occur = hurricane_scope[hurricane]["year"][0]
  election = winner.loc[winner['year'] == utils.get_election_year(year_occur)]
  merged_df= pd.merge(election, api_data, how="left", on = 'county_fips')
  fig = px.choropleth_mapbox(merged_df, geojson=counties, 
    locations='county_fips',
    hover_name = 'county_name',
    color = 'party',
    mapbox_style="open-street-map",
    zoom=3, 
    center = {"lat": 37.0902, "lon": -95.7129},
    color_discrete_sequence=px.colors.qualitative.Set1,
    opacity=0.3,
  )
  fig.add_scattermapbox(lat = hurricane_df['LAT'],
    lon = hurricane_df['LON'],
    mode = 'markers+text',
    marker_size= hurricane_df['STORM_SPEED'],
    marker_color='rgb(255, 222, 113)',
    showlegend = False
)
  return fig


