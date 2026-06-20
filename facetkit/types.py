#===============================================================================
# DEPENDENCIES

from collections import namedtuple
from typing import TYPE_CHECKING, Any, ClassVar, Protocol

if TYPE_CHECKING:
    from facetkit.container import Container

#===============================================================================
# DEFINITIONS

# Container --------------------------------------------------------------------

class Facet(Protocol):
    name: str
    def clear(self) -> None: ...

class Component(Protocol):
    """Composable plugin registered on a Container.

    Optional class attributes:
        required_components: names of components that must already be
            registered before attach runs.
        required_facets: mount names of facets that must already be
            mounted before attach runs.
    """

    required_components: ClassVar[tuple[str, ...]]
    required_facets: ClassVar[tuple[str, ...]]
    def attach(self, ctx: 'Container') -> None: ...
    def detach(self, ctx: 'Container') -> None: ...

# cli Facet --------------------------------------------------------------------

Command = namedtuple('Command', ['name', 'callable', 'description'])

# TUI Facet --------------------------------------------------------------------

ScreenDescriptor     = namedtuple('ScreenDescriptor',     ['name', 'factory', 'title'])
KeybindingDescriptor = namedtuple('KeybindingDescriptor', ['key', 'handler', 'screen', 'priority'])

# GUI Facet --------------------------------------------------------------------

WidgetDescriptor   = namedtuple('WidgetDescriptor',   ['id', 'factory', 'parent', 'layout_hints'])
MenuDescriptor     = namedtuple('MenuDescriptor',     ['id', 'factory', 'parent'])
ToolbarDescriptor  = namedtuple('ToolbarDescriptor',  ['id', 'factory', 'parent'])
LayoutDescriptor   = namedtuple('LayoutDescriptor',   ['id', 'factory', 'hints'])

# Web Facet --------------------------------------------------------------------

RouteDescriptor        = namedtuple('RouteDescriptor',        ['path', 'methods', 'handler', 'name'])
MiddlewareDescriptor   = namedtuple('MiddlewareDescriptor',   ['name', 'handler', 'priority'])
ErrorHandlerDescriptor = namedtuple('ErrorHandlerDescriptor', ['code', 'handler'])

# Service Facet ----------------------------------------------------------------

TaskDescriptor = namedtuple('TaskDescriptor', ['name', 'factory', 'interval'])
