from pivot import Connector, AGGREGATION_FIELD

ACTIVEPIVOT_ENDPOINT = "http://localhost:9090/"

connector = Connector(ACTIVEPIVOT_ENDPOINT, "admin", "admin")

query_1 = connector.mdx_query("""
SELECT
  NON EMPTY [Measures].[Total scores] ON COLUMNS,
  NON EMPTY [Games].[Games].[Team1Name].Members ON ROWS
  FROM [NanoPivotCube]
  CELL PROPERTIES VALUE, FORMATTED_VALUE, BACK_COLOR, FORE_COLOR, FONT_FLAGS
""")
total_scores_1 = query_1.dataframe[[
    "Team1Name", "Total scores"]].groupby("Team1Name").sum()

query_2 = connector.mdx_query("""
SELECT
  NON EMPTY [Measures].[Total scores] ON COLUMNS,
  NON EMPTY [Games].[Games].[Team2Name].Members ON ROWS
  FROM [NanoPivotCube]
  CELL PROPERTIES VALUE, FORMATTED_VALUE, BACK_COLOR, FORE_COLOR, FONT_FLAGS
""")
total_scores_2 = query_2.dataframe[[
    "Team1Name", "Total scores"]].groupby("Team1Name").sum()


print(total_scores_1 == total_scores_2)
