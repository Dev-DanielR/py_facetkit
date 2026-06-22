#===============================================================================
# DEPENDENCIES

from typing import Any, Callable, Dict, Optional
from facetkit.types import Facet, KeybindingDescriptor, ScreenDescriptor

#===============================================================================
# DEFINITIONS

class TuiFacet(Facet):

    def __init__(self):
        self.name           = "tui"
        self.screens        : Dict[str, ScreenDescriptor]     = {}
        self.keybindings    : Dict[str, KeybindingDescriptor]  = {}
        self.current_screen : Optional[str]                     = None

    def add_screen(self, screen_id: str, factory: Callable[..., Any], title: str = "") -> None:
        self.screens[screen_id] = ScreenDescriptor(screen_id, factory, title)

    def remove_screen(self, screen_id: str) -> None:
        self.screens.pop(screen_id, None)
        if self.current_screen == screen_id: self.current_screen = None

    def add_keybinding(
        self,
        binding_id: str,
        key: str,
        handler: Callable[..., Any],
        screen_id: Optional[str] = None,
        priority: int = 0,
    ) -> None:
        self.keybindings[binding_id] = KeybindingDescriptor(binding_id, key, handler, screen_id, priority)

    def remove_keybinding(self, binding_id: str) -> None:
        self.keybindings.pop(binding_id, None)

    def clear(self) -> None:
        self.screens.clear()
        self.keybindings.clear()
        self.current_screen = None