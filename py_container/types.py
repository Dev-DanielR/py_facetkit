#===============================================================================
# DEPENDENCIES

from collections import namedtuple
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from py_container.container import Container

#===============================================================================
# DEFINITIONS

# Container --------------------------------------------------------------------

class Facet(Protocol):
    name: str
    def clear(self) -> None: ...

class Component(Protocol):
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
