from pivot import Connector

ACTIVEPIVOT_ENDPOINT = "http://localhost:9090/"

connector = Connector(ACTIVEPIVOT_ENDPOINT, "admin", "admin")

df = None

with open('example.mdx') as mdx:
    df = connector.mdx(mdx.read())

