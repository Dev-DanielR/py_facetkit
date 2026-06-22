#===============================================================================
# DEFINITIONS

class DuplicateFacetError(Exception):
    """Raised when binding a facet under a facet_id that is already in use."""

    def __init__(self, facet_id: str):
        self.facet_id = facet_id
        super().__init__(f"facet {facet_id!r} is already bound")

class DuplicateComponentError(Exception):
    """Raised when binding a component under a component_id that is already in use."""

    def __init__(self, component_id: str):
        self.component_id = component_id
        super().__init__(f"component {component_id!r} is already bound")

class MissingComponentDependencyError(Exception):
    """Raised when a component's required_components are not bound."""

    def __init__(self, component_id: str, missing: tuple[str, ...]):
        self.component_id = component_id
        self.missing = missing
        missing_ids = ", ".join(missing)
        super().__init__(f"component {component_id!r} requires {missing_ids}")

class MissingFacetDependencyError(Exception):
    """Raised when a component's required_facets are not bound."""

    def __init__(self, component_id: str, missing: tuple[str, ...]):
        self.component_id = component_id
        self.missing = missing
        missing_ids = ", ".join(missing)
        super().__init__(f"component {component_id!r} requires facets {missing_ids}")

class ComponentInUseError(Exception):
    """Raised when unbinding a component that others depend on."""

    def __init__(self, component_id: str, dependents: tuple[str, ...]):
        self.component_id = component_id
        self.dependents = dependents
        dependent_ids = ", ".join(dependents)
        super().__init__(f"cannot unbind {component_id!r}; required by {dependent_ids}")

class FacetInUseError(Exception):
    """Raised when unbinding a facet that bound components depend on."""

    def __init__(self, facet_id: str, dependents: tuple[str, ...]):
        self.facet_id = facet_id
        self.dependents = dependents
        dependent_ids = ", ".join(dependents)
        super().__init__(f"cannot unbind facet {facet_id!r}; required by {dependent_ids}")