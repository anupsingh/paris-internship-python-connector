# How to define a connector

```py
from pivot import Connector
from pivot.authentication import basic_auth

active_pivot_endpoint = "https://endpoint.my-activepivot.com/"

connector = Connector(active_pivot_endpoint, basic_auth("username", "password"))
```

# Authentication

Supported methods:

- [Basic Authentication](https://www.httpwatch.com/httpgallery/authentication/)
