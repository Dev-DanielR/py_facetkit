#===============================================================================
# DEPENDENCIES

import glom

from typing import Dict, Any
from facetkit.exceptions import (
    DependentComponentsError,
    DuplicateComponentError,
    DuplicateFacetError,
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

    def mount_facet(self, name: str, facet: Facet, *, overwrite: bool = True) -> None:
        if name in self.facets:
            if not overwrite: raise DuplicateFacetError(name)
            self._unmount_facet(name, check_dependents=False)
        self.facets[name] = facet

    def unmount_facet(self, name: str) -> None:
        self._unmount_facet(name, check_dependents=True)

    def add_component(self, name: str, comp: Component, *, overwrite: bool = True) -> None:
        """Register a component and attach it to this container."""

        if name in self.components and not overwrite:
            raise DuplicateComponentError(name)
        self._validate_attach_requirements(name, comp)
        if name in self.components: self._detach_component(name, check_dependents=False)
        comp.attach(self)
        self.components[name] = comp

    def remove_component(self, name: str) -> None:
        """Remove a component and detach it from this container."""

        self._detach_component(name, check_dependents=True)

    # Internal API =============================================================

    def _required_components(self, comp: Component) -> tuple[str, ...]:
        return getattr(type(comp), "required_components", ())

    def _required_facets(self, comp: Component) -> tuple[str, ...]:
        return getattr(type(comp), "required_facets", ())

    def _validate_attach_requirements(self, name: str, comp: Component) -> None:
        missing_components = tuple(
            req for req in self._required_components(comp)
            if req not in self.components
        )
        if missing_components:
            raise MissingComponentDependencyError(name, missing_components)

        missing_facets = tuple(
            req for req in self._required_facets(comp)
            if req not in self.facets
        )
        if missing_facets:
            raise MissingFacetDependencyError(name, missing_facets)

    def _validate_detach_requirements(self, name: str) -> None:
        dependents = tuple(
            comp_name for comp_name, comp in self.components.items()
            if comp_name != name and name in self._required_components(comp)
        )
        if dependents:
            raise DependentComponentsError(name, dependents)

    def _validate_facet_unmount_requirements(self, name: str) -> None:
        dependents = tuple(
            comp_name for comp_name, comp in self.components.items()
            if name in self._required_facets(comp)
        )
        if dependents:
            raise FacetInUseError(name, dependents)

    def _detach_component(self, name: str, *, check_dependents: bool) -> None:
        if check_dependents: self._validate_detach_requirements(name)
        comp = self.components.pop(name, None)
        if comp: comp.detach(self)

    def _unmount_facet(self, name: str, *, check_dependents: bool) -> None:
        if check_dependents: self._validate_facet_unmount_requirements(name)
        facet = self.facets.pop(name, None)
        if facet: facet.clear()