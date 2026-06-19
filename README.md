# py-container

A composable Python container for application state and passive registries.
Provides basic functionality for CLI commands, TUI screens, GUI widgets, web routes and background services.

## Design

- **Container** — shared config, component lifecycle, and a map of mounted facets
- **Facets** — framework-agnostic registries (commands, routes, widgets, tasks, etc)
- **Components** — plugins that register into facets on `attach` and clean up on `detach`

```
Container
├── config
├── components
└── facets
    ├── cli      → commands
    ├── tui      → screens, keybindings
    ├── gui      → widgets, menus, toolbars, layouts
    ├── web      → routes, middleware, error handlers
    └── service  → tasks, providers
```

## Requirements

- Python 3.10+
- [glom](https://github.com/mahmoud/glom) (declared as a dependency)

## Installation

```bash
pip install py-container
```

For local development:

```bash
git clone https://github.com/Dev-DanielR/py_container.git
cd py_container
pip install -e ".[dev]"
```

## Quick start

```python
from py_container import Container, CliFacet, WebFacet

app = Container({"app": {"name": "demo"}})

app.mount_facet("cli", CliFacet())
app.mount_facet("web", WebFacet())

def hello():
    """Say hello."""
    return "Hello!"

cli = app.facets["cli"]
cli.add_command("hello", hello)

web = app.facets["web"]
web.add_route("hello", "/hello", lambda: {"message": "Hello!"}, methods=["GET"])
```

Your application reads the registries and dispatches however you like — argparse, FastAPI, Textual, Qt, etc.

## Components

Components implement `attach(ctx)` and `detach(ctx)`. The container is passed as context:

```python
class StatusComponent:
    def attach(self, ctx):
        ctx.facets["cli"].add_command("status", self.show_status)
        ctx.facets["service"].add_provider("status", {"healthy": True})

    def detach(self, ctx):
        ctx.facets["cli"].remove_command("status")
        ctx.facets["service"].remove_provider("status")

    def show_status(self):
        """Show application status."""
        return "ok"

app.mount_facet("cli", CliFacet())
app.mount_facet("service", ServiceFacet())
app.add_component("status", StatusComponent())
```

Replacing or removing a component calls `detach` on the old instance before the new one attaches.

## Facets

| Facet | Registries | Purpose |
|-------|------------|---------|
| `CliFacet` | `commands` | Named CLI commands. Description is taken from the handler's docstring |
| `TuiFacet` | `screens`, `keybindings`, `current_screen` | Terminal UI descriptors |
| `GuiFacet` | `widgets`, `menus`, `toolbars`, `layouts` | Desktop UI descriptors |
| `WebFacet` | `routes`, `middleware`, `error_handlers` | HTTP/API descriptors |
| `ServiceFacet` | `tasks`, `providers` | Background work and shared providers |

Mount only what you need:

```python
app.mount_facet("cli", CliFacet())
app.mount_facet("web", WebFacet())
# No TUI/GUI facets required
```

Unmounting clears the facet's registries:

```python
app.unmount_facet("cli")
```

### Registry behavior

- **Duplicate keys** — registering the same name again overwrites the previous entry (last wins).
- **Unmount** — `unmount_facet` clears that facet's registries. Attached components are not automatically detached; call `remove_component` first if you need a full teardown.
- **Facet names** — the mount name is arbitrary (`app.mount_facet("cli", CliFacet())`). The library does not enforce that the name matches the facet type.
- **Missing facets** — `app.facets["cli"]` raises `KeyError`; `app.get("facets.cli")` returns `None`.

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

Missing paths return `default` (or `None`):

```python
app.get("facets.missing")              # None
app.get("facets.missing", default={})  # {}
```

`get()` also returns `default` on any internal error while resolving a path, not only missing keys. That keeps introspection safe but can hide bugs — prefer direct attribute access when you want exceptions to surface.

Direct dict access also works when you know a facet is mounted:

```python
app.facets["cli"].commands["hello"]
```

## Public API

```python
from py_container import (
    Container,
    Component,     # protocol
    Facet,         # protocol
    CliFacet,
    TuiFacet,
    GuiFacet,
    WebFacet,
    ServiceFacet,
    Command,
    RouteDescriptor,
    # ... other descriptor types
)
```

## Versioning

This project is pre-1.0 (`0.1.0`). Public APIs may change between minor releases. See [CHANGELOG.md](CHANGELOG.md) for release notes.

## Development

```bash
pip install -e ".[dev]"
pytest
```

Build a wheel locally:

```bash
pip install build
python -m build
```

## License

MIT — see [LICENSE](LICENSE).