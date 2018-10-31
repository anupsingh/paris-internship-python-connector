from pivot import Connector

ACTIVEPIVOT_ENDPOINT = "http://localhost:9090/"

connector = Connector(ACTIVEPIVOT_ENDPOINT, "admin", "admin")

mdx_request = ''

with open('example.mdx') as mdx:
    mdx_request = mdx.read()

query = connector.mdx(mdx_request)
print(query.dataframe)
