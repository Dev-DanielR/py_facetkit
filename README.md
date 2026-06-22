# facetkit

A composable Python container for application state and passive registries — CLI commands, TUI screens, GUI widgets, web routes, and background services.

facetkit separates three pieces:

| Piece | Role |
|-------|------|
| [Container](docs/container.md) | Application root — config, facet & component binding |
| [Facet](docs/facet.md) | Passive registry for a surface area (commands, routes, widgets, …) |
| [Component](docs/component.md) | Plugin that connects to one or several facets in on_bind and cleans up in on_unbind  |

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
- [glom](https://github.com/mahmoud/glom)

## Installation

```bash
pip install facetkit
```

For local development:

```bash
git clone https://github.com/Dev-DanielR/py_facetkit.git
cd facetkit
pip install -e ".[dev]"
```

## Quick start

```python
from facetkit import Container, CliFacet, WebFacet

app = Container({"app": {"name": "demo"}})

app.bind_facet("cli", CliFacet())
app.bind_facet("web", WebFacet())

def hello():
    """Say hello."""
    return "Hello!"

app.facets["cli"].add_command("hello", hello)
app.facets["web"].add_route("hello", "/hello", lambda: {"message": "Hello!"}, methods=["GET"])
```

Register directly on facets (as above) or through [components](docs/component.md). Your dispatch layer reads the registries and wires them to argparse, FastAPI, Textual, Qt, or whatever you use.

## Documentation

- [Container](docs/container.md) — config, lifecycle, introspection
- [Facets](docs/facet.md) — facet types, registries, binding
- [Components](docs/component.md) — on_bind/on_unbind, dependencies
- [Examples](docs/examples/composed_app.py) — composed app with logger and status components

## Development

```bash
pip install -e ".[dev]"
pytest
```

See [CHANGELOG.md](CHANGELOG.md) for release notes. Pre-1.0 (`0.4.0`) — public APIs may change between minor releases.

## License

MIT — see [LICENSE](LICENSE).