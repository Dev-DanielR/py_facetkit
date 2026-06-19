#===============================================================================
# DEPENDENCIES

from textwrap import dedent

from typing import Any, Callable, Dict
from facetkit.types import Command, Facet

#===============================================================================
# DEFINITIONS

class CliFacet(Facet):

    def __init__(self):
        self.name     = "cli"
        self.commands : Dict[str, Command] = {}

    def add_command(self, name: str, handler: Callable[..., Any]) -> None:
        doc = handler.__doc__ or ""
        self.commands[name] = Command(name, handler, dedent(doc).strip())

    def remove_command(self, name: str) -> None:
        self.commands.pop(name, None)

    def clear(self) -> None:
        self.commands.clear()