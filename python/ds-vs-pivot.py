from pivot import Connector
from datetime import datetime

# ACTIVEPIVOT_ENDPOINT = "http://localhost:9090"
ACTIVEPIVOT_ENDPOINT = "https://activepivot-ranch.activeviam.com:5700/"
USER = 'admin'
PASSWD = 'admin'

connector = Connector(ACTIVEPIVOT_ENDPOINT, USER, PASSWD)

# with open('example.mdx') as mdx:
#     mdx_request = mdx.read()

# stores = connector.stores()
# print(f"stores: {stores}")
# fields = connector.store_fields('Risk')
# print(f'fields: {fields}')
# refs = connector.store_references('Risk')
# print(f'refs {refs}')
# print(connector.store_fields('Trade'))


# query_ds = connector.store_query('Risk', fields = ['AsOfDate', 'RiskToTrade/CounterParty', 'RiskToTrade/Desk'])
# Result by a datastore query
current_date = datetime.now()
target_date = f"{current_date.year}-{current_date.month}-{current_date.day}"

query_ds = connector.store_query('Risk', fields = ['AsOfDate', 'pnl', 'vega'])
# print(f"ds query = {query_ds.dataframe.describe()}")
aggr_ds_query = query_ds.dataframe.groupby('AsOfDate').sum()
print(f"ds aggregation =\n{aggr_ds_query}")
print(f"ds aggregation =\n{aggr_ds_query.loc[target_date]}")
filtered = aggr_ds_query.loc[target_date, :]
print(f'ds for {target_date} = {filtered}')

# Result by a Mdx query
mdx_query = connector.mdx_query('SELECT NON EMPTY {[Measures].[pnl.SUM],[Measures].[vega.SUM]} ON COLUMNS, NON EMPTY [Time].[HistoricalDates].[AsOfDate].Members ON ROWS FROM [EquityDerivativesCube]')
print(f'mdx query : {mdx_query.dataframe}')