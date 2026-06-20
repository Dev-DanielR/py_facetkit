# Container

The **Container** is the application root. It holds shared configuration, a map of [mounted facets](facet.md), and a registry of [attached components](component.md).

```
Container
├── config          → shared application settings
├── components      → named plugins (attach / detach lifecycle)
└── facets          → passive registries, keyed by mount name
```

Create one at startup and pass it through your app:

```python
from facetkit import Container

app = Container({"app": {"name": "demo"}, "port": 8080})
```

## Config

The constructor takes a plain dict. Components and application code read it through `ctx.config` or `ctx.get("config....")`.

```python
app.config["port"]           # 8080
app.get("config.app.name")   # "demo"
```

## Lifecycle

The container exposes lifecycle methods for [facets](facet.md) (`mount_facet`, `unmount_facet`) and [components](component.md) (`add_component`, `remove_component`). Both mount and add accept an `overwrite` flag (default `True`) to control duplicate-name behavior.

## Boot order

Typical startup sequence:

1. Create a `Container` with config
2. `mount_facet` for each surface your app uses
3. `add_component` for each feature plugin — register dependencies before dependents

Your framework layer (argparse, FastAPI, Textual, Qt, etc.) then reads the facet registries and dispatches.

## Introspection with `get()`

`Container.get(path)` uses [glom](https://glom.readthedocs.io/) to read nested state:

```python
app.get("")                        # the container itself
app.get("config.app.name")         # config values
app.get("facets")                  # all mounted facets
app.get("facets.cli")              # CliFacet instance
app.get("facets.cli.commands")     # command registry
app.get("facets.web.routes.users") # a single route entry
```

Without `default`, resolution errors propagate (missing paths, glom failures, etc.):

```python
app.get("facets.cli.commands") # works when the cli facet is mounted
app.get("facets.missing")      # raises glom.PathAccessError
```

Pass `default` for optional lookups — any resolution error returns that value:

```python
app.get("facets.missing", default=None) # None
app.get("facets.missing", default={})   # {}
```

Direct dict access also works when you know a facet is mounted:

```python
app.facets["cli"].commands["hello"]
app.components["logger"]
```