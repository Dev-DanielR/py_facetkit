# Components

A **Component** is an active plugin that connects to one or several [facets](facet.md) in `on_bind` and cleans up in `on_unbind`. This keeps feature setup and teardown in one place instead of scattered across your application.

## Types and exceptions

**Protocol**

```python
class MyComponent:
    def on_bind(self, container): ...
    def on_unbind(self, container): ...
```

Optional class attributes — see [Declared dependencies](#declared-dependencies).

**Exceptions**

| Exception | When | Attributes |
|-----------|------|------------|
| `DuplicateComponentError` | `bind_component(overwrite=False)` | `.component_id` |
| `MissingComponentDependencyError` | `bind_component` — required component absent | `.component_id`, `.missing` |
| `MissingFacetDependencyError` | `bind_component` — required facet not bound | `.component_id`, `.missing` |
| `ComponentInUseError` | `unbind_component` — another component depends on it | `.component_id`, `.dependents` |

`FacetInUseError` (raised on `unbind_facet`) is documented in [Facets](facet.md).

## Lifecycle

Components are bound and unbound through the container:

```python
from facetkit import Container, CliFacet, ServiceFacet

class StatusComponent:
    required_facets = ("cli", "service")

    def on_bind(self, container):
        container.facets["cli"].add_command("status", self.show_status)
        container.facets["service"].add_provider("status", {"healthy": True})

    def on_unbind(self, container):
        container.facets["cli"].remove_command("status")
        container.facets["service"].remove_provider("status")

    def show_status(self):
        """Show application status."""
        return "ok"

app = Container({"app": {"name": "demo"}})
app.bind_facet("cli", CliFacet())
app.bind_facet("service", ServiceFacet())
app.bind_component("status", StatusComponent())
app.unbind_component("status")
```

**`bind_component(component_id, comp, *, overwrite=True)`** — validates declared dependencies, calls `on_bind(container)`, then stores the instance. When `overwrite=True` (the default), if a component has already been bound with the same id it is unbound without a dependent check before replacing it with the new component. Pass `overwrite=False` to raise `DuplicateComponentError` instead:

```python
app.bind_component("logger", Logger(), overwrite=False)
```

If validation fails, `on_bind` is not called.

**`unbind_component(component_id)`** — calls `on_unbind(container)`, then removes the instance. Raises `ComponentInUseError` if any other bound component lists `component_id` in `required_components`.

Inside `on_bind` / `on_unbind`, components typically:

- Register or unregister entries on `container.facets[...]`
- Read shared state from `container.config`
- Reach peer plugins via `container.components["component_id"]`

See [examples/composed_app.py](examples/composed_app.py) for a full walkthrough with peer dependencies and CLI dispatch.

```bash
python docs/examples/composed_app.py
```

## Declared dependencies

Components can declare what must already be present before they bind. Both attributes are optional class-level tuples:

```python
class ApiComponent:
    required_components = ("logger", "database") # peer components
    required_facets = ("cli", "web")             # bound facet ids

    def on_bind(self, container):
        logger = container.components["logger"]
        container.facets["cli"].add_command("api-status", self.status)
        container.facets["web"].add_route("api-status", "/status", self.status)

    def on_unbind(self, container):
        container.facets["cli"].remove_command("api-status")
        container.facets["web"].remove_route("api-status")
```

The container enforces these at lifecycle boundaries:

| Action | Validation |
|--------|------------|
| `bind_component` | Every component_id in `required_components` must already be bound; every facet_id in `required_facets` must already be bound. `on_bind` is not called if anything is missing. |
| `unbind_component` | Blocked if any other bound component lists this component_id in `required_components`. |
| `unbind_facet` | Blocked if any bound component lists this facet_id in `required_facets`. |
| Replace component | Allowed — dependent checks are skipped so the slot stays filled. |

Register dependencies before dependents:

```python
app.bind_component("logger", LoggerComponent())
app.bind_component("database", DatabaseComponent())
app.bind_component("api", ApiComponent()) # OK

app.bind_component("api", ApiComponent()) # raises MissingComponentDependencyError
```

Tear down in reverse:

```python
app.unbind_component("api")    # OK
app.unbind_component("logger") # OK once api is gone

app.unbind_facet("cli")       # raises FacetInUseError while a component still requires it
```