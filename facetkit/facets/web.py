#===============================================================================
# DEPENDENCIES

from typing import Any, Callable, Dict, Optional, Sequence, Union
from facetkit.types import Facet, ErrorHandlerDescriptor, MiddlewareDescriptor, RouteDescriptor

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
        route_id: str,
        path: str,
        handler: Callable[..., Any],
        methods: Sequence[str] = ("GET",),
    ) -> None:
        self.routes[route_id] = RouteDescriptor(route_id, path, tuple(methods), handler)

    def remove_route(self, route_id: str) -> None:
        self.routes.pop(route_id, None)

    def add_middleware(self, middleware_id: str, handler: Callable[..., Any], priority: int = 0) -> None:
        self.middleware[middleware_id] = MiddlewareDescriptor(middleware_id, handler, priority)

    def remove_middleware(self, middleware_id: str) -> None:
        self.middleware.pop(middleware_id, None)

    def add_error_handler(self, error_handler_id: Union[int, str], handler: Callable[..., Any]) -> None:
        self.error_handlers[str(error_handler_id)] = ErrorHandlerDescriptor(error_handler_id, handler)

    def remove_error_handler(self, error_handler_id: Union[int, str]) -> None:
        self.error_handlers.pop(str(error_handler_id), None)

    def clear(self) -> None:
        self.routes.clear()
        self.middleware.clear()
        self.error_handlers.clear()