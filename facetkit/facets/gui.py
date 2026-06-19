#===============================================================================
# DEPENDENCIES

from typing import Any, Callable, Dict, Optional
from facetkit.types import Facet, LayoutDescriptor, MenuDescriptor, ToolbarDescriptor, WidgetDescriptor

#===============================================================================
# DEFINITIONS

class GuiFacet(Facet):

    def __init__(self):
        self.name     = "gui"
        self.widgets  : Dict[str, WidgetDescriptor]   = {}
        self.menus    : Dict[str, MenuDescriptor]     = {}
        self.toolbars : Dict[str, ToolbarDescriptor]  = {}
        self.layouts  : Dict[str, LayoutDescriptor]   = {}

    def add_widget(
        self,
        widget_id: str,
        factory: Callable[..., Any],
        parent: Optional[str] = None,
        layout_hints: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.widgets[widget_id] = WidgetDescriptor(widget_id, factory, parent, layout_hints or {})

    def remove_widget(self, widget_id: str) -> None:
        self.widgets.pop(widget_id, None)

    def add_menu(self, menu_id: str, factory: Callable[..., Any], parent: Optional[str] = None) -> None:
        self.menus[menu_id] = MenuDescriptor(menu_id, factory, parent)

    def remove_menu(self, menu_id: str) -> None:
        self.menus.pop(menu_id, None)

    def add_toolbar(self, toolbar_id: str, factory: Callable[..., Any], parent: Optional[str] = None) -> None:
        self.toolbars[toolbar_id] = ToolbarDescriptor(toolbar_id, factory, parent)

    def remove_toolbar(self, toolbar_id: str) -> None:
        self.toolbars.pop(toolbar_id, None)

    def add_layout(self, layout_id: str, factory: Callable[..., Any], hints: Optional[Dict[str, Any]] = None) -> None:
        self.layouts[layout_id] = LayoutDescriptor(layout_id, factory, hints or {})

    def remove_layout(self, layout_id: str) -> None:
        self.layouts.pop(layout_id, None)

    def clear(self) -> None:
        self.widgets.clear()
        self.menus.clear()
        self.toolbars.clear()
        self.layouts.clear()