#===============================================================================
# DEPENDENCIES

import glom

from typing import Dict, Any
from facetkit.exceptions import (
    DuplicateComponentError,
    DuplicateFacetError,
    ComponentInUseError,
    FacetInUseError,
    MissingComponentDependencyError,
    MissingFacetDependencyError,
)
from facetkit.types import Component, Facet

#===============================================================================
# DEFINITIONS

_UNSET = object()

class Container:

    def __init__(self, config: Dict[str, Any]):
        self.config     : Dict[str, Any]       = config
        self.facets     : Dict[str, Facet]     = {}
        self.components : Dict[str, Component] = {}

    # Public API ===============================================================

    def get(self, path: str, default: Any = _UNSET) -> Any:
        """Retrieve from container using glom.

        Raises glom errors when *default* is omitted. Pass *default* to
        return that value instead when the path cannot be resolved.
        """

        if not path: return self
        try:
            return glom.glom(self.__dict__, path)
        except (glom.PathAccessError, glom.GlomError):
            if default is _UNSET: raise
            return default
        except Exception:
            if default is _UNSET: raise
            return default

    def bind_facet(self, facet_id: str, facet: Facet, *, overwrite: bool = True) -> None:
        if facet_id in self.facets:
            if not overwrite: raise DuplicateFacetError(facet_id)
            self._unbind_facet(facet_id, check_dependents=False)
        self.facets[facet_id] = facet

    def unbind_facet(self, facet_id: str) -> None:
        self._unbind_facet(facet_id, check_dependents=True)

    def bind_component(self, component_id: str, comp: Component, *, overwrite: bool = True) -> None:
        """Bind a component and invoke its on_bind hook."""

        if component_id in self.components and not overwrite:
            raise DuplicateComponentError(component_id)
        self._validate_bind_requirements(component_id, comp)
        if component_id in self.components:
            self._unbind_component(component_id, check_dependents=False)
        comp.on_bind(self)
        self.components[component_id] = comp

    def unbind_component(self, component_id: str) -> None:
        """Unbind a component and invoke its on_unbind hook."""

        self._unbind_component(component_id, check_dependents=True)

    # Internal API =============================================================

    def _required_facets(self, comp: Component) -> tuple[str, ...]:
        return getattr(type(comp), "required_facets", ())

    def _validate_facet_unbind_requirements(self, facet_id: str) -> None:
        dependents = tuple(
            comp_id for comp_id, comp in self.components.items()
            if facet_id in self._required_facets(comp)
        )
        if dependents:
            raise FacetInUseError(facet_id, dependents)

    def _unbind_facet(self, facet_id: str, *, check_dependents: bool) -> None:
        if check_dependents: self._validate_facet_unbind_requirements(facet_id)
        facet = self.facets.pop(facet_id, None)
        if facet: facet.clear()

    def _required_components(self, comp: Component) -> tuple[str, ...]:
        return getattr(type(comp), "required_components", ())

    def _validate_bind_requirements(self, component_id: str, comp: Component) -> None:
        missing_components = tuple(
            req for req in self._required_components(comp)
            if req not in self.components
        )
        if missing_components:
            raise MissingComponentDependencyError(component_id, missing_components)

        missing_facets = tuple(
            req for req in self._required_facets(comp)
            if req not in self.facets
        )
        if missing_facets:
            raise MissingFacetDependencyError(component_id, missing_facets)

    def _validate_unbind_requirements(self, component_id: str) -> None:
        dependents = tuple(
            other_id for other_id, comp in self.components.items()
            if other_id != component_id and component_id in self._required_components(comp)
        )
        if dependents:
            raise ComponentInUseError(component_id, dependents)

    def _unbind_component(self, component_id: str, *, check_dependents: bool) -> None:
        if check_dependents: self._validate_unbind_requirements(component_id)
        comp = self.components.pop(component_id, None)
        if comp: comp.on_unbind(self)
