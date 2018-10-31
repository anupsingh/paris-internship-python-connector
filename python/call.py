from pivot import Connector

ACTIVEPIVOT_ENDPOINT = "http://localhost:9090/"

connector = Connector(ACTIVEPIVOT_ENDPOINT, "admin", "admin")

df1 = None

with open('example.mdx') as mdx:
    query = connector.mdx(mdx.read())
    df1 = query.to_data_frame()

