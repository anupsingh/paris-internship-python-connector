import pandas as pd

from pivot import Connector, AGGREGATION_FIELD
from pivot.authentication import basic_auth

ACTIVEPIVOT_ENDPOINT = "http://localhost:9090/"

connector = Connector(ACTIVEPIVOT_ENDPOINT, basic_auth("admin", "admin"))

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

query_1 = connector.mdx_query(mdx)
query_2 = connector.store_query(
    "RussiaWorldCup2018", fields=["Team1Name", "Team2Name", "Team1Score", "Team2Score"]
)

df_1 = query_1.dataframe[["Team1Name", "Team2Name", "Team1Score", "Team2Score"]]
df_2 = query_2.dataframe[["Team1Name", "Team2Name", "Team1Score", "Team2Score"]]


def get_df(df, name):
    df_1 = df.loc[
        (df["Team1Name"] == name)
        & (df["Team1Score"] != AGGREGATION_FIELD)
        & (df["Team2Score"] != AGGREGATION_FIELD)
    ]
    df_2 = df.loc[
        (df["Team2Name"] == name)
        & (df["Team1Score"] != AGGREGATION_FIELD)
        & (df["Team2Score"] != AGGREGATION_FIELD)
    ].rename(
        columns={
            "Team1Score": "Team2Score",
            "Team2Score": "Team1Score",
            "Team1Name": "Team2Name",
            "Team2Name": "Team1Name",
        }
    )
    return pd.concat([df_1, df_2], sort=False).sort_values(by=["Team1Name", "Team2Name"])


def get_df_2(df, name):
    df_1 = df.loc[(df["Team1Name"] == name)]
    df_2 = df.loc[(df["Team2Name"] == name)].rename(
        columns={
            "Team1Score": "Team2Score",
            "Team2Score": "Team1Score",
            "Team1Name": "Team2Name",
            "Team2Name": "Team1Name",
        }
    )
    return pd.concat([df_1, df_2], sort=False).sort_values(by=["Team1Name", "Team2Name"])


df_france = get_df(df_1, "France")
df_france_2 = get_df_2(df_2, "France")

print(df_france.values == df_france_2.values)

df_peru = get_df(df_1, "Peru")
df_peru_2 = get_df_2(df_2, "Peru")

print(df_peru.values == df_peru_2.values)

