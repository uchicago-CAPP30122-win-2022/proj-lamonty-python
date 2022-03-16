import pandas as pd
import json

def detail_view_init():
  with open('data/geojson-counties-fips.json', 'r') as f:
    counties = json.load(f)
  winner = pd.read_csv("data/county_president_winner.csv", dtype={"county_fips": str})
  hurricane_path = pd.read_csv("data/hurricane_path.csv")
  with open('data/hurricane_scope.json', 'r') as f:
    hurricane_scope = json.load(f)
  hurricanes = hurricane_path['NAME'].unique()
  return counties, winner, hurricane_path, hurricane_scope, hurricanes



def get_election_year(year):
  return year - year%4