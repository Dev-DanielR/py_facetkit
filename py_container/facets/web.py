#===============================================================================
# DEPENDENCIES

from typing import Any, Callable, Dict, Optional, Sequence, Union
from py_container.types import Facet, ErrorHandlerDescriptor, MiddlewareDescriptor, RouteDescriptor

#===============================================================================
# DEFINITIONS

class WebFacet(Facet):

    def __init__(self):
        self.name           = "web"
        self.routes         : Dict[str, RouteDescriptor]        = {}
        self.middleware     : Dict[str, MiddlewareDescriptor]    = {}
        self.error_handlers : Dict[str, ErrorHandlerDescriptor] = {}

    def add_route(
        self,
        name: str,
        path: str,
        handler: Callable[..., Any],
        methods: Sequence[str] = ("GET",),
    ) -> None:
        self.routes[name] = RouteDescriptor(path, tuple(methods), handler, name)

    def remove_route(self, name: str) -> None:
        self.routes.pop(name, None)

    def add_middleware(self, name: str, handler: Callable[..., Any], priority: int = 0) -> None:
        self.middleware[name] = MiddlewareDescriptor(name, handler, priority)

    def remove_middleware(self, name: str) -> None:
        self.middleware.pop(name, None)

    def add_error_handler(self, code: Union[int, str], handler: Callable[..., Any]) -> None:
        self.error_handlers[str(code)] = ErrorHandlerDescriptor(code, handler)

    def remove_error_handler(self, code: Union[int, str]) -> None:
        self.error_handlers.pop(str(code), None)

    def clear(self) -> None:
        self.routes.clear()
        self.middleware.clear()
        self.error_handlers.clear()