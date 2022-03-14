import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output
import pandas as pd
from backend import datasets


##MAKE FUNCTION
with open('data/geojson-counties-fips.json', 'r') as f:
  counties = json.load(f)
winner = pd.read_csv("data/county_president_winner.csv", dtype={"county_fips": str})
df = winner.loc[winner['year'] == 2016]
hurricane_path = pd.read_csv("data/hurricane_path.csv")
hurricanes = hurricane_path['NAME'].unique()
hurricane_df = hurricane_path.loc[(hurricane_path ['NAME'] == 'HARVEY')]
data = datasets.get_data(["48"], [2017])
merged_df= pd.merge(df, data, how="left", on = 'county_fips')
print(merged_df.columns)
##########

fig = px.choropleth_mapbox(merged_df, geojson=counties, 
                          locations='county_fips',
                          hover_name = 'county_name',
                          color = 'party',
                          mapbox_style="open-street-map",
                          zoom=3, 
                          center = {"lat": 37.0902, "lon": -95.7129},
                          opacity=0.3,
                          )
#fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.add_scattermapbox(lat = hurricane_df['LAT'],
                      lon = hurricane_df['LON'],
                      mode = 'markers+text',
                      #text = harvey_data['STORM_SPEED'].,
                      marker_size= hurricane_df['STORM_SPEED'],
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