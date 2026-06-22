#===============================================================================
# DEPENDENCIES

from typing import Any, Callable, Dict, Optional
from facetkit.types import Facet, TaskDescriptor

#===============================================================================
# DEFINITIONS

class ServiceFacet(Facet):

    def __init__(self):
        self.name      = "service"
        self.tasks     : Dict[str, TaskDescriptor] = {}
        self.providers : Dict[str, Any]            = {}

    def add_task(self, task_id: str, factory: Callable[..., Any], interval: Optional[float] = None) -> None:
        self.tasks[task_id] = TaskDescriptor(task_id, factory, interval)

    def remove_task(self, task_id: str) -> None:
        self.tasks.pop(task_id, None)

    def add_provider(self, provider_id: str, provider: Any) -> None:
        self.providers[provider_id] = provider

    def remove_provider(self, provider_id: str) -> None:
        self.providers.pop(provider_id, None)

    def clear(self) -> None:
        self.tasks.clear()
        self.providers.clear()