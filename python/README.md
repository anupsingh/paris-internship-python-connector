Table of Contents

- [How to define a connector](#how-to-define-a-connector)
- [Authentication](#authentication)
- [Query](#query)
  - [Attributes](#attributes)
  - [Methods](#methods)
  - [Types](#types)
- [Queries](#queries)
  - [Stores](#stores)
  - [Store fields](#store-fields)
  - [MDX query](#mdx-query)
  - [MDX query builder](#mdx-query-builder)
  - [Datastore query](#datastore-query)

## How to define a connector

```py
from pivot import Connector
from pivot.authentication import basic_auth

active_pivot_endpoint = "https://endpoint.my-activepivot.com/"

connector = Connector(active_pivot_endpoint, basic_auth("username", "password"))
```

## Authentication

Supported methods:

- [Basic Authentication](https://www.httpwatch.com/httpgallery/authentication/)

## Query

Every query returns a `Query` object:

### Attributes

| Attribute | Type                    | Description                                        |
| --------- | ----------------------- | -------------------------------------------------- |
| dataframe | panda.dataframe         | dataframe that represents the results of the query |
| types     | Dict[column_name, type] | Object that define the type of each column         |

### Methods

| Method      | Input | Returns | Description                                                                                                                                                  |
| ----------- | ----- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| refresh     | /     | /       | Recompute its dataframe based on its internal query                                                                                                          |
| detect_type | /     | /       | Parse the dataframe and populate empty fields of the attribute `types` with the type that fits the most each column (only supports `int`, `float` and `str`) |
| apply_types | /     | /       | Convert each column to their types defined in the attribute `types`                                                                                          |
### Types

To define a custom type, you just have to write:

```py
class Date:
  hour: int
  min: int
  sec: int

  def __init__(self, date):
    if isinstance(date, Date):
      return date
    self.hour = int(date.split('h')[0])
    min = date.split('h')[1]
    self.min = int(min.split('min')[0])
    self.sec = int(min.split('min')[1])

  def __str__(self):
    return f"{self.hour}h{self.min}min{self.sec}"

query.types = {
  "complex_column": complex,
  "date_column": Date,
}

query.detect_type()

query.apply_type()
```

If a type fails on a data, there is a fallback on the str type.

## Queries

### Stores

Get the list of stores of a cube

```py
connector.stores()

# ['store_1', 'store_2']
```

### Store fields

Get the list of available fields of a specific store with their respective types

```py
connector.store_fields('store_1')

# { 'field_1': <class 'int'>, 'field_2': <class 'str'> }
```

### MDX query

Basic usage:

```py
query = connector.mdx_query(MDX_QUERY_STRING)

print(query.dataframe)
```

If you want to set a few custom types:

```py
query = connector.mdx_query(MDX_QUERY_STRING, { "complex_column": complex })

print(query.dataframe)
```

### MDX query builder

In order to avoid writing MDX queries, you can use the mdx_builder:

```py
query = connector.mdx_builder(CUBE, [FIELD_1, FIELD_2, FIELD_3])

print(query.dataframe)
```

If you want to set a few custom types:

```py
query = connector.mdx_builder(CUBE, [FIELD_1, FIELD_2, FIELD_3], { "complex_column": complex })

print(query.dataframe)
```

### Datastore query

Execute a query directly on the data store.
Must specify the name of the data store and the fields that you want to retrieve.

You can specify:

- the conditions if you want to filter the data
- the timeout of the request
- the epoch
- the branch on which the request will be done
- the limit and the offset for pagination
- the returned types

Basic query:

```py
connector.store_query('store_1', ['field_1', 'field_2'])
```

With limit and offset:
```py
connector.store_query('store_1', ['field_1', 'field_2'], limit=250, offset=500)
# Will omit the 500 first results and then retrieve the 250 following
```

With the branch:
```py
connector.store_query('store_1', ['field_1', 'field_2'], branch='fork_1')
```

With conditions:
```py
connector.store_query('store_1', ['field_1', 'field_2'], conditions={"year" : 2010, "currency" : "EUR"})
```
