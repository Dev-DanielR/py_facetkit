# Facets

A **Facet** is a passive registry for an application surface — CLI commands, web routes, GUI widgets, background tasks, and so on. Facets collect descriptors; your dispatch layer reads them and runs the app. Bind only what you need on the [Container](container.md).

## Types and exceptions

**Protocol**

- `Facet` — `name: str`, `clear()`

**Implementations**

| Facet | Registries | Purpose |
|-------|------------|---------|
| `CliFacet` | `commands` | Named CLI commands. Description is taken from the handler's docstring |
| `TuiFacet` | `screens`, `keybindings`, `current_screen` | Terminal UI descriptors |
| `GuiFacet` | `widgets`, `menus`, `toolbars`, `layouts` | Desktop UI descriptors |
| `WebFacet` | `routes`, `middleware`, `error_handlers` | HTTP/API descriptors |
| `ServiceFacet` | `tasks`, `providers` | Background work and shared providers |

**Descriptor types** — `Command`, `ScreenDescriptor`, `KeybindingDescriptor`, `WidgetDescriptor`, `MenuDescriptor`, `ToolbarDescriptor`, `LayoutDescriptor`, `RouteDescriptor`, `MiddlewareDescriptor`, `ErrorHandlerDescriptor`, `TaskDescriptor`

**Exceptions**

| Exception | When | Attributes |
|-----------|------|------------|
| `DuplicateFacetError` | `bind_facet(overwrite=False)` | `.facet_id` |
| `FacetInUseError` | `unbind_facet` while a component requires the facet id | `.facet_id`, `.dependents` |

## Lifecycle

Facets are bound and unbound through the container:

```python
from facetkit import Container, CliFacet, WebFacet

app = Container({})
app.bind_facet("cli", CliFacet())
app.unbind_facet("cli")
```

**`bind_facet(facet_id, facet, *, overwrite=True)`** — stores the facet under `facet_id`. When `overwrite=True` (the default), an existing binding of the same id is cleared and replaced without a dependent check. Pass `overwrite=False` to raise `DuplicateFacetError` instead:

```python
app.bind_facet("cli", CliFacet(), overwrite=False)
```

**`unbind_facet(facet_id)`** — pops the facet and calls `clear()` on it. Raises `FacetInUseError` if any bound [component](component.md) lists `facet_id` in `required_facets`. Unbind those components first.

Replacing a facet reuses the facet id — dependent checks are skipped on replacement so the slot stays available.

## Registering entries

Populate registries directly or through [components](component.md) during `on_bind`:

```python
def hello():
    """Say hello."""
    return "Hello!"

app.facets["cli"].add_command("hello", hello)
app.facets["web"].add_route("hello", "/hello", lambda: {"message": "Hello!"}, methods=["GET"])
```

Each facet exposes typed `add_*` / `remove_*` helpers over plain dict registries. Your application dispatches however you like — argparse, FastAPI, Textual, Qt, etc.

## Facet ids

The facet id is arbitrary. The library does not require `"cli"` for a `CliFacet`, though consistent naming helps components declare `required_facets`:

```python
app.bind_facet("cli", CliFacet())      # conventional
app.bind_facet("commands", CliFacet()) # also valid
```