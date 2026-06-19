#===============================================================================
# DEPENDENCIES

from typing import Any, Callable, Dict, Optional
from py_container.types import Facet, TaskDescriptor

#===============================================================================
# DEFINITIONS

class ServiceFacet(Facet):

    def __init__(self):
        self.name      = "service"
        self.tasks     : Dict[str, TaskDescriptor] = {}
        self.providers : Dict[str, Any]            = {}

    def add_task(self, name: str, factory: Callable[..., Any], interval: Optional[float] = None) -> None:
        self.tasks[name] = TaskDescriptor(name, factory, interval)

    def remove_task(self, name: str) -> None:
        self.tasks.pop(name, None)

    def add_provider(self, name: str, provider: Any) -> None:
        self.providers[name] = provider

    def remove_provider(self, name: str) -> None:
        self.providers.pop(name, None)

    def clear(self) -> None:
        self.tasks.clear()
        self.providers.clear()