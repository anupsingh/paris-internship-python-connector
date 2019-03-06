from pivot import Connector, AGGREGATION_FIELD
from pivot.authentication import basic_auth

ACTIVEPIVOT_ENDPOINT = "http://localhost:9090/"

connector = Connector(ACTIVEPIVOT_ENDPOINT, basic_auth("admin", "admin"))

mdx_request = ""

with open("example.mdx") as mdx:
    mdx_request = mdx.read()

query1 = connector.mdx_query(mdx_request)
query2 = connector.store_query(
    "RussiaWorldCup2018", fields=["Team1Name", "Team2Name", "Team1Score"]
)
query3 = connector.store_fields("RussiaWorldCup2018")
print(connector.stores())
print(connector.store_fields("RussiaWorldCup2018"))
print(connector.store_references("RussiaWorldCup2018"))
# print(query.dataframe)
