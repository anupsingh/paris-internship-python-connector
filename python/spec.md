## Connect to ActivePivot

```py
from pivot import Connector

ACTIVEPIVOT_ENDPOINT = "http://localhost:9090/"

connector = Connector(ACTIVEPIVOT_ENDPOINT, "admin", "admin")
```

## Data frame from a MDX query

```python
query1 = connecter.mdx_query("SELECT ... FROM [Cube]")
df1 = query1.to_data_frame()
best_teams = df1.loc[df['Total'] > 10, 'TeamName1']
```

## Get fields from datasotre

```python
fields = connector.store_fields(store='RussiaWorldCup2018')
```

## Data frame from a Datatore query

```python
query2 = connector.store_query(store='RussiaWorldCup2018', fields = ['Team1Name', 'Team2Name'])
df2 = query2.to_data_frame()
```

## Refresh the result

Shall it refresh internally or produce a new object, allowing the user to compare the two results together

```python
from pivot import refreshed
query1Updated = refreshed(query1) # Copy
query1.refresh() # In place
```

## Server-side simulation within a branch

```python
query3 = query1.simulate_on_branch('simulation1')
query3.add()
query3.update_where(...)
query3.delete_where(...)
query3.to_data_frame()

query3.delete_simulation()
```

Would it be possible to update the Panda DataFrame and save it back on the server
