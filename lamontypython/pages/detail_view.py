"""
(la)Monty Python
Aditya Retnanto
March 2022

Module to display hurricane view with choropleth and regression info
"""
import pandas as pd
import plotly.express as px
from dash import html, dcc, Input, Output, callback, dash_table
from backend import datasets
from utils import utils
from models.hurricane_regs import DisasterRegs

counties, winner, hurricane_path, hurricane_scope, hurricanes = utils.detail_view_init()

layout = html.Div(children=[
    html.P("Note, it might take some time to display data"),
    html.Div(children=[
        html.Label('Hurricane'),
        dcc.Dropdown(hurricanes, hurricanes[1], multi = False, id='hurricane')
    ]),
html.Br(),
 html.Div([
    dcc.Graph(id='hurricane_map', style={"display": "none"})
  ]),
  html.Br(),
  html.P("Dependent variable in specified regression is dollar value requested from FEMA by county"),
  html.Div([
    dash_table.DataTable(
      id='reg_table',
      data=[]
    )
  ]),
  html.Br(),
  html.Div([
    dash_table.DataTable(
      id='var_table',
      data=[]
    )
  ])
])

@callback(
    Output("hurricane_map", "figure"),
    Output("hurricane_map", "style"),
    Output("reg_table", "data"),
    Output("reg_table", "column"),
    Output("var_table", "data"),
    Output("var_table", "column"),
    Input('hurricane', 'value')
)
def display_hurricane(hurricane):
    """
    Calls API on Hurricane info and updates figures.
    :param hurricane: User selected hurricane
    """
    hurricane_df = hurricane_path.loc[(hurricane_path['NAME'] == hurricane)]
    regression = DisasterRegs(hurricane_scope[hurricane]["states_fips"], hurricane_scope[hurricane]["year"])
    api_data = regression.pull_data()
    reg_output,_,var_table = regression.pooled_ols(api_data)
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
    fig.add_scattermapbox(
      lat = hurricane_df['LAT'],
      lon = hurricane_df['LON'],
      mode = 'markers+text',
      marker_size= hurricane_df['STORM_SPEED'],
      marker_color='rgb(255, 222, 113)',
      showlegend = False
)
    return fig, {"display": "flex"}, reg_output.to_dict('records'), reg_output.columns, var_table.to_dict('records'), var_table.columns
