import pandas as pd

from pivot import Connector, AGGREGATION_FIELD

ACTIVEPIVOT_ENDPOINT = "http://localhost:9090/"

connector = Connector(ACTIVEPIVOT_ENDPOINT, "admin", "admin")

mdx = """
WITH
 Member [Measures].[[Scores]].[Team1Score]].[Team1Score]]_for_order] AS [Scores].[Team1Score].CurrentMember.MEMBER_CAPTION 
SELECT
  NON EMPTY Crossjoin(
    Hierarchize(
      DrilldownLevel(
        [Scores].[Team1Score].[ALL].[AllMember]
      )
    ),
    Hierarchize(
      DrilldownLevel(
        [Scores].[Team2Score].[ALL].[AllMember]
      )
    ),
    [Measures].[Total scores]
  ) ON COLUMNS,
  NON EMPTY [Games].[Games].[Team2Name].Members ON ROWS
  FROM [NanoPivotCube]
"""

query = connector.mdx_query(mdx)
df = query.dataframe[['Team1Name', 'Team2Name', 'Team1Score', 'Team2Score']]

def get_df(df, name):
    df_1 = df.loc[(df['Team1Name'] == name) & (df['Team1Score'] != AGGREGATION_FIELD) & (df['Team2Score'] != AGGREGATION_FIELD)]
    df_2 = df.loc[(df['Team2Name'] == name) & (df['Team1Score'] != AGGREGATION_FIELD) & (df['Team2Score'] != AGGREGATION_FIELD)].rename(columns={'Team1Score': 'Team2Score', 'Team2Score': 'Team1Score', 'Team1Name': 'Team2Name', 'Team2Name': 'Team1Name'})
    return pd.concat([df_1, df_2], sort=False)

df_france = get_df(df, 'France')

df_peru = get_df(df, 'Peru')
