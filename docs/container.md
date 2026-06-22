# Container

The **Container** is the application root. It holds shared configuration, a map of [bound facets](facet.md), and a registry of [bound components](component.md).

```
Container
├── config          → shared application settings
├── components      → named plugins (on_bind / on_unbind lifecycle)
└── facets          → passive registries, keyed by facet id
```

Create one at startup and pass it through your app:

```python
from facetkit import Container

app = Container({"app": {"name": "demo"}, "port": 8080})
```

## Config

The constructor takes a plain dict. Components and application code read it through `container.config` or `container.get("config....")`.

```python
app.config["port"]           # 8080
app.get("config.app.name")   # "demo"
```

## Lifecycle

The container exposes lifecycle methods for [facets](facet.md) (`bind_facet`, `unbind_facet`) and [components](component.md) (`bind_component`, `unbind_component`). Both bind methods accept an `overwrite` flag (default `True`) to control duplicate-id behavior.

## Boot order

Typical startup sequence:

1. Create a `Container` with config
2. `bind_facet` for each surface your app uses
3. `bind_component` for each feature plugin — bind dependencies before dependents

Your framework layer (argparse, FastAPI, Textual, Qt, etc.) then reads the facet registries and dispatches.

## Introspection with `get()`

`Container.get(path)` uses [glom](https://glom.readthedocs.io/) to read nested state:

```python
app.get("")                        # the container itself
app.get("config.app.name")         # config values
app.get("facets")                  # all bound facets
app.get("facets.cli")              # CliFacet instance
app.get("facets.cli.commands")     # command registry
app.get("facets.web.routes.users") # a single route entry
```

Without `default`, resolution errors propagate (missing paths, glom failures, etc.):

```python
app.get("facets.cli.commands") # works when the cli facet is bound
app.get("facets.missing")      # raises glom.PathAccessError
```

Pass `default` for optional lookups — any resolution error returns that value:

```python
app.get("facets.missing", default=None) # None
app.get("facets.missing", default={})   # {}
```

Direct dict access also works when you know a facet is bound:

```python
app.facets["cli"].commands["hello"]
app.components["logger"]
```