#===============================================================================
# DEPENDENCIES

import glom

from typing import Dict, Any
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

    def mount_facet(self, name: str, facet: Facet) -> None:
        if name in self.facets: self.unmount_facet(name)
        self.facets[name] = facet

    def unmount_facet(self, name: str) -> None:
        facet = self.facets.pop(name, None)
        if facet: facet.clear()

    def add_component(self, name: str, comp: Component) -> None:
        """Register a component and attach it to this container."""

        if name in self.components: self.remove_component(name)
        comp.attach(self)
        self.components[name] = comp

    def remove_component(self, name: str) -> None:
        """Remove a component and detach it from this container."""

        comp = self.components.pop(name, None)
        if comp: comp.detach(self)