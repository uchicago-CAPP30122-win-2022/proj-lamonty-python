import pandas as pd
def clean_fips(df):
    states = ['AL', 'AR', 'AK','AZ','CA', 'CO', 'CT']
    for state in states:
        df.loc[df['state_po'] == state, ['county_fips']] = '0' + df.loc[df['state_po'] == state, ['county_fips']]
    return df

def hurricane_subset(df):
    maria_data = df.loc[(df['NAME'] == 'MARIA') & (df['SEASON'] == 2017)]
    harvey_data = df.loc[(df['NAME'] == 'HARVEY') & (df['SEASON'] == 2017)]
    irma_data = df.loc[(df['NAME'] == 'IRMA') & (df['SEASON'] == 2017)]
    sandy_data = df.loc[(df['NAME'] == 'SANDY') & (df['SEASON'] == 2012)]
    subset = [maria_data, harvey_data, irma_data, sandy_data]
    subset_df = pd.concat(subset)
    subset_df.to_csv("hurricane_path.csv", index = False)

county = pd.read_csv("countypres_2000-2020.csv", dtype={"county_fips": str})
winning_candidate_idx = county.groupby(['county_fips','year'], sort=False)['candidatevotes'].transform(max) == county['candidatevotes']
winner = county[winning_candidate_idx]
winner = clean_fips(winner)
winner.to_csv("county_president_winner.csv", index = False)

hurricane_data = pd.read_csv("ibtracs.ALL.list.v04r00.csv")
hurricane_subset(hurricane_data)
