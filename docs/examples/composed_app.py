"""Compose a container with logger and status components.

Demonstrates component dependencies, facet registration, and dispatch
over the CLI command registry.

Run from the project root after installing facetkit:

    python docs/examples/composed_app.py
"""

from facetkit import Container, CliFacet, ServiceFacet


class LoggerComponent:
    def on_bind(self, container):
        container.facets["service"].add_provider("logger", self)

    def on_unbind(self, container):
        container.facets["service"].remove_provider("logger")

    def info(self, msg):
        print(msg)


class StatusComponent:
    required_components = ("logger",)
    required_facets = ("cli", "service")

    def on_bind(self, container):
        self._logger = container.components["logger"]
        container.facets["cli"].add_command("status", self.show_status)
        container.facets["service"].add_provider("status", {"healthy": True})

    def on_unbind(self, container):
        container.facets["cli"].remove_command("status")
        container.facets["service"].remove_provider("status")

    def show_status(self):
        """Show application status."""
        self._logger.info("status check")
        return "ok"


def main():
    app = Container({"app": {"name": "demo"}})
    app.bind_facet("cli", CliFacet())
    app.bind_facet("service", ServiceFacet())
    app.bind_component("logger", LoggerComponent())
    app.bind_component("status", StatusComponent())

    print("Registered CLI commands:")
    for command_id, cmd in app.facets["cli"].commands.items():
        print(f"  {command_id}: {cmd.description}")


if __name__ == "__main__":
    main()