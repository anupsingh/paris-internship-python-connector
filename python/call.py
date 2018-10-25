from pivot import Connector

ACTIVEPIVOT_ENDPOINT = "http://localhost:9090/"

connector = Connector(ACTIVEPIVOT_ENDPOINT, "admin", "admin")

with open('example.mdx') as mdx:
    t = mdx.read().strip()
    print(connector.mdx(t))

