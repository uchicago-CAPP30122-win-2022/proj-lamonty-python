import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import Dash, html, dcc, Input, Output
import pandas as pd

##MAKE FUNCTION
with open('geojson-counties-fips.json', 'r') as f:
  counties = json.load(f)
winner = pd.read_csv("county_president_winner.csv", dtype={"county_fips": str})
df = winner.loc[winner['year'] == 2016]
hurricane_path = pd.read_csv("hurricane_path.csv")

hurricanes = hurricane_path['NAME'].unique()
harvey_data = hurricane_path .loc[(hurricane_path ['NAME'] == 'HARVEY')]
##########

fig = px.choropleth_mapbox(df, geojson=counties, locations='county_fips',
                           color = 'party',
                           mapbox_style="open-street-map",
                           zoom=3, 
                           center = {"lat": 37.0902, "lon": -95.7129},
                           opacity=0.3,
                          )
#fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.add_scattermapbox(lat = harvey_data['LAT'],
                      lon = harvey_data['LON'],
                      mode = 'markers+text',
                      #text = harvey_data['STORM_SPEED'].,
                      marker_size=harvey_data['STORM_SPEED'],
                      marker_color='rgb(0,102,255)',
                      showlegend = False
)

layout = html.Div(children=[
    html.Div(children=[
        html.Label('Hurricane'),
        dcc.Dropdown(hurricanes, hurricanes, multi = False, id='hurricane')
    ]),

 html.Div([
    dcc.Graph(figure=fig)
  ])
])