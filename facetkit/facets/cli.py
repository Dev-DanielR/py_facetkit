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

    def add_command(self, command_id: str, handler: Callable[..., Any]) -> None:
        doc = handler.__doc__ or ""
        self.commands[command_id] = Command(command_id, handler, dedent(doc).strip())

    def remove_command(self, command_id: str) -> None:
        self.commands.pop(command_id, None)

    def clear(self) -> None:
        self.commands.clear()