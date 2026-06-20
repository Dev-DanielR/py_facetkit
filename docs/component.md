# Components

A **Component** is an active plugin that registers into [facets](facet.md) on attach and cleans up on detach. This keeps feature setup and teardown in one place instead of scattered across your application.

## Types and exceptions

**Protocol**

```python
class MyComponent:
    def attach(self, ctx): ...
    def detach(self, ctx): ...
```

Optional class attributes — see [Declared dependencies](#declared-dependencies).

**Exceptions**

| Exception | When | Attributes |
|-----------|------|------------|
| `DuplicateComponentError` | `add_component(overwrite=False)` | `.name` |
| `MissingComponentDependencyError` | `add_component` — required component absent | `.component`, `.missing` |
| `MissingFacetDependencyError` | `add_component` — required facet not mounted | `.component`, `.missing` |
| `DependentComponentsError` | `remove_component` — another component depends on it | `.component`, `.dependents` |

`FacetInUseError` (raised on `unmount_facet`) is documented in [Facets](facet.md).

## Lifecycle

Components are registered and removed through the container:

```python
from facetkit import Container, CliFacet, ServiceFacet

class StatusComponent:
    required_facets = ("cli", "service")

    def attach(self, ctx):
        ctx.facets["cli"].add_command("status", self.show_status)
        ctx.facets["service"].add_provider("status", {"healthy": True})

    def detach(self, ctx):
        ctx.facets["cli"].remove_command("status")
        ctx.facets["service"].remove_provider("status")

    def show_status(self):
        """Show application status."""
        return "ok"

app = Container({"app": {"name": "demo"}})
app.mount_facet("cli", CliFacet())
app.mount_facet("service", ServiceFacet())
app.add_component("status", StatusComponent())
app.remove_component("status")
```

**`add_component(name, comp, *, overwrite=True)`** — validates declared dependencies, calls `attach(ctx)`, then stores the instance. The [container](container.md) is passed as `ctx`. When `overwrite=True` (the default), an existing registration of the same name is detached and replaced without a dependent check. Pass `overwrite=False` to raise `DuplicateComponentError` instead:

```python
app.add_component("logger", Logger(), overwrite=False)
```

If validation fails, `attach` is not called.

**`remove_component(name)`** — calls `detach(ctx)`, then removes the instance. Raises `DependentComponentsError` if any other attached component lists `name` in `required_components`.

Inside `attach` / `detach`, components typically:

- Register or unregister entries on `ctx.facets[...]`
- Read shared state from `ctx.config`
- Reach peer plugins via `ctx.components["name"]`

See [examples/composed_app.py](examples/composed_app.py) for a full walkthrough with peer dependencies and CLI dispatch.

```bash
python docs/examples/composed_app.py
```

## Declared dependencies

Components can declare what must already be present before they attach. Both attributes are optional class-level tuples:

```python
class ApiComponent:
    required_components = ("logger", "database") # peer components
    required_facets = ("cli", "web")             # mounted facet names

    def attach(self, ctx):
        logger = ctx.components["logger"]
        ctx.facets["cli"].add_command("api-status", self.status)
        ctx.facets["web"].add_route("api-status", "/status", self.status)

    def detach(self, ctx):
        ctx.facets["cli"].remove_command("api-status")
        ctx.facets["web"].remove_route("api-status")
```

The container enforces these at lifecycle boundaries:

| Action | Validation |
|--------|------------|
| `add_component` | Every name in `required_components` must already be registered; every name in `required_facets` must already be mounted. `attach` is not called if anything is missing. |
| `remove_component` | Blocked if any other attached component lists this name in `required_components`. |
| `unmount_facet` | Blocked if any attached component lists this mount name in `required_facets`. |
| Replace same name | Allowed — dependent checks are skipped so the slot stays filled. |

Register dependencies before dependents:

```python
app.add_component("logger", LoggerComponent())
app.add_component("database", DatabaseComponent())
app.add_component("api", ApiComponent()) # OK

app.add_component("api", ApiComponent()) # raises MissingComponentDependencyError
```

Tear down in reverse:

```python
app.remove_component("api")    # OK
app.remove_component("logger") # OK once api is gone

app.unmount_facet("cli")       # raises FacetInUseError while a component still requires it
```