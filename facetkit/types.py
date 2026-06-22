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
    """Composable plugin that connects to a Container.

    Optional class attributes:
        required_components: ids of components that must already be bound before on_bind runs.
        required_facets: ids of facets that must already be bound before on_bind runs.
    """

    required_components: ClassVar[tuple[str, ...]]
    required_facets: ClassVar[tuple[str, ...]]
    def on_bind(self, container: 'Container') -> None: ...
    def on_unbind(self, container: 'Container') -> None: ...

# cli Facet --------------------------------------------------------------------

Command = namedtuple('Command', ['id', 'callable', 'description'])

# TUI Facet --------------------------------------------------------------------

ScreenDescriptor     = namedtuple('ScreenDescriptor',     ['id', 'factory', 'title'])
KeybindingDescriptor = namedtuple('KeybindingDescriptor', ['id', 'key', 'handler', 'screen_id', 'priority'])

# GUI Facet --------------------------------------------------------------------

WidgetDescriptor   = namedtuple('WidgetDescriptor',   ['id', 'factory', 'parent_id', 'layout_hints'])
MenuDescriptor     = namedtuple('MenuDescriptor',     ['id', 'factory', 'parent_id'])
ToolbarDescriptor  = namedtuple('ToolbarDescriptor',  ['id', 'factory', 'parent_id'])
LayoutDescriptor   = namedtuple('LayoutDescriptor',   ['id', 'factory', 'hints'])

# Web Facet --------------------------------------------------------------------

RouteDescriptor        = namedtuple('RouteDescriptor',        ['id', 'path', 'methods', 'handler'])
MiddlewareDescriptor   = namedtuple('MiddlewareDescriptor',   ['id', 'handler', 'priority'])
ErrorHandlerDescriptor = namedtuple('ErrorHandlerDescriptor', ['id', 'handler'])

# Service Facet ----------------------------------------------------------------

TaskDescriptor = namedtuple('TaskDescriptor', ['id', 'factory', 'interval'])
