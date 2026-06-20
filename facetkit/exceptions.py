#===============================================================================
# DEFINITIONS

class DuplicateFacetError(Exception):
    """Raised when mounting a facet under a name that is already in use."""

    def __init__(self, name: str):
        self.name = name
        super().__init__(f"facet {name!r} is already mounted")

class DuplicateComponentError(Exception):
    """Raised when registering a component under a name that is already in use."""

    def __init__(self, name: str):
        self.name = name
        super().__init__(f"component {name!r} is already registered")

class MissingComponentDependencyError(Exception):
    """Raised when a component's required_components are not registered."""

    def __init__(self, component: str, missing: tuple[str, ...]):
        self.component = component
        self.missing = missing
        names = ", ".join(missing)
        super().__init__(f"component {component!r} requires {names}")

class MissingFacetDependencyError(Exception):
    """Raised when a component's required_facets are not mounted."""

    def __init__(self, component: str, missing: tuple[str, ...]):
        self.component = component
        self.missing = missing
        names = ", ".join(missing)
        super().__init__(f"component {component!r} requires facets {names}")

class DependentComponentsError(Exception):
    """Raised when removing a component that others depend on."""

    def __init__(self, component: str, dependents: tuple[str, ...]):
        self.component = component
        self.dependents = dependents
        names = ", ".join(dependents)
        super().__init__(f"cannot remove {component!r}; required by {names}")

class FacetInUseError(Exception):
    """Raised when unmounting a facet that attached components depend on."""

    def __init__(self, facet: str, dependents: tuple[str, ...]):
        self.facet = facet
        self.dependents = dependents
        names = ", ".join(dependents)
        super().__init__(f"cannot unmount facet {facet!r}; required by {names}")