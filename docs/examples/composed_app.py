"""Compose a container with logger and status components.

Demonstrates component dependencies, facet registration, and dispatch
over the CLI command registry.

Run from the project root after installing facetkit:

    python docs/examples/composed_app.py
"""

from facetkit import Container, CliFacet, ServiceFacet


class LoggerComponent:
    def attach(self, ctx):
        ctx.facets["service"].add_provider("logger", self)

    def detach(self, ctx):
        ctx.facets["service"].remove_provider("logger")

    def info(self, msg):
        print(msg)


class StatusComponent:
    required_components = ("logger",)
    required_facets = ("cli", "service")

    def attach(self, ctx):
        self._logger = ctx.components["logger"]
        ctx.facets["cli"].add_command("status", self.show_status)
        ctx.facets["service"].add_provider("status", {"healthy": True})

    def detach(self, ctx):
        ctx.facets["cli"].remove_command("status")
        ctx.facets["service"].remove_provider("status")

    def show_status(self):
        """Show application status."""
        self._logger.info("status check")
        return "ok"


def main():
    app = Container({"app": {"name": "demo"}})
    app.mount_facet("cli", CliFacet())
    app.mount_facet("service", ServiceFacet())
    app.add_component("logger", LoggerComponent())
    app.add_component("status", StatusComponent())

    print("Registered CLI commands:")
    for name, cmd in app.facets["cli"].commands.items():
        print(f"  {name}: {cmd.description}")


if __name__ == "__main__":
    main()