from dash import Dash, html, dcc
import pandas as pd

colors = {
    'background': '#ecf0f1',
    'text': '#af7ac5'
}

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ],
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    )