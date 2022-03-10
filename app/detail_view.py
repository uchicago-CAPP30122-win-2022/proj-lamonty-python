import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import Dash, html, dcc, Input, Output
import pandas as pd
app = Dash(__name__)

colors = {
    'background': '#ecf0f1',
    'text': '#af7ac5  '
}
with open('geojson-counties-fips.json', 'r') as f:
  counties = json.load(f)
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                   dtype={"fips": str})
hurricane_path = pd.read_csv("hurricane_path.csv")
hurricanes = hurricane_path['NAME'].unique()

harvey_data = hurricane_path .loc[(hurricane_path ['NAME'] == 'HARVEY')]
fig = px.choropleth_mapbox(df, geojson=counties, locations='fips',
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

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='(la)Monty Python Dash Template',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    
    html.Div(children=[
        html.Label('Hurricane'),
        dcc.Dropdown(hurricanes, hurricanes, multi = False, id='hurricane')
    ]),

 html.Div([
    dcc.Graph(figure=fig)
  ])
])

if __name__ == '__main__':
    app.run_server(debug=True)