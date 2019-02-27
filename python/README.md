Table of Contents

- [How to define a connector](#how-to-define-a-connector)
- [Authentication](#authentication)
- [Query](#query)
  - [Attributes](#attributes)
  - [Methods](#methods)
  - [Types](#types)
  - [MDX](#mdx)

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

### MDX
