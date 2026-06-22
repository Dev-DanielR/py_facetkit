import pytest

from facetkit import (
    Container,
    CliFacet,
    DuplicateFacetError,
    FacetInUseError,
    GuiFacet,
    MissingFacetDependencyError,
    ServiceFacet,
    TuiFacet,
    WebFacet,
)


class TestContainerFacets:
    def test_starts_with_empty_facets(self, container):
        assert container.facets == {}

    def test_bind_facet(self, container):
        cli = CliFacet()
        container.bind_facet("cli", cli)

        assert container.facets["cli"] is cli
        assert container.get("facets.cli.commands") == {}

    def test_unbind_facet_clears_registry(self, container):
        cli = CliFacet()
        cli.add_command("ping", lambda: None)
        container.bind_facet("cli", cli)

        container.unbind_facet("cli")

        assert "cli" not in container.facets
        assert cli.commands == {}

    def test_rebind_replaces_facet(self, container):
        first = CliFacet()
        second = CliFacet()
        first.add_command("old", lambda: None)

        container.bind_facet("cli", first)
        container.bind_facet("cli", second)

        assert container.facets["cli"] is second
        assert first.commands == {}

    def test_blocks_duplicate_facet_when_overwrite_disabled(self, container):
        first = CliFacet()
        second = CliFacet()
        first.add_command("old", lambda: None)

        container.bind_facet("cli", first)

        with pytest.raises(DuplicateFacetError) as exc:
            container.bind_facet("cli", second, overwrite=False)

        assert exc.value.facet_id == "cli"
        assert container.facets["cli"] is first
        assert "old" in first.commands

    def test_compose_multiple_facets(self, container):
        container.bind_facet("cli", CliFacet())
        container.bind_facet("service", ServiceFacet())
        container.bind_facet("tui", TuiFacet())
        container.bind_facet("gui", GuiFacet())
        container.bind_facet("web", WebFacet())

        assert set(container.facets) == {"cli", "service", "tui", "gui", "web"}
        assert container.get("facets.cli.name") == "cli"
        assert container.get("facets.service.name") == "service"
        assert container.get("facets.tui.name") == "tui"
        assert container.get("facets.gui.name") == "gui"
        assert container.get("facets.web.name") == "web"


class TestComposableComponents:
    def test_component_binds_into_multiple_facets(self, container):
        class MultiFacetComponent:
            def on_bind(self, container):
                def status():
                    """Show status."""
                    return "ok"

                container.facets["cli"].add_command("status", status)
                container.facets["service"].add_provider("status", {"healthy": True})

            def on_unbind(self, container):
                container.facets["cli"].remove_command("status")
                container.facets["service"].remove_provider("status")

        container.bind_facet("cli", CliFacet())
        container.bind_facet("service", ServiceFacet())
        container.bind_component("status", MultiFacetComponent())

        assert "status" in container.get("facets.cli.commands")
        assert "status" in container.get("facets.service.providers")

        container.unbind_component("status")

        assert "status" not in container.get("facets.cli.commands")
        assert "status" not in container.get("facets.service.providers")

    def test_on_bind_without_required_facet_raises(self, container):
        class NeedsCli:
            required_facets = ("cli",)

            def on_bind(self, container):
                container.facets["cli"].add_command("ping", lambda: None)

            def on_unbind(self, container):
                pass

        with pytest.raises(MissingFacetDependencyError) as exc:
            container.bind_component("needs-cli", NeedsCli())

        assert exc.value.component_id == "needs-cli"
        assert exc.value.missing == ("cli",)

    def test_on_bind_succeeds_when_required_facets_present(self, container):
        class NeedsCli:
            required_facets = ("cli",)

            def on_bind(self, container):
                container.facets["cli"].add_command("ping", lambda: None)

            def on_unbind(self, container):
                container.facets["cli"].remove_command("ping")

        container.bind_facet("cli", CliFacet())
        container.bind_component("needs-cli", NeedsCli())

        assert "ping" in container.get("facets.cli.commands")

    def test_on_bind_does_not_run_when_facet_requirements_unmet(self, container):
        class NeedsCli:
            required_facets = ("cli",)
            bound = False

            def on_bind(self, container):
                self.bound = True

            def on_unbind(self, container):
                pass

        comp = NeedsCli()
        with pytest.raises(MissingFacetDependencyError):
            container.bind_component("needs-cli", comp)

        assert comp.bound is False

    def test_unbind_fails_when_components_depend_on_facet(self, container):
        class NeedsCli:
            required_facets = ("cli",)

            def on_bind(self, container):
                container.facets["cli"].add_command("ping", lambda: None)

            def on_unbind(self, container):
                container.facets["cli"].remove_command("ping")

        container.bind_facet("cli", CliFacet())
        container.bind_component("needs-cli", NeedsCli())

        with pytest.raises(FacetInUseError) as exc:
            container.unbind_facet("cli")

        assert exc.value.facet_id == "cli"
        assert exc.value.dependents == ("needs-cli",)
        assert "cli" in container.facets

    def test_unbind_succeeds_after_dependent_components_unbound(self, container):
        class NeedsCli:
            required_facets = ("cli",)

            def on_bind(self, container):
                container.facets["cli"].add_command("ping", lambda: None)

            def on_unbind(self, container):
                container.facets["cli"].remove_command("ping")

        container.bind_facet("cli", CliFacet())
        container.bind_component("needs-cli", NeedsCli())

        container.unbind_component("needs-cli")
        container.unbind_facet("cli")

        assert "cli" not in container.facets

    def test_rebind_facet_skips_dependent_check(self, container):
        class NeedsCli:
            required_facets = ("cli",)

            def on_bind(self, container):
                container.facets["cli"].add_command("ping", lambda: None)

            def on_unbind(self, container):
                container.facets["cli"].remove_command("ping")

        container.bind_facet("cli", CliFacet())
        container.bind_component("needs-cli", NeedsCli())

        replacement = CliFacet()
        container.bind_facet("cli", replacement)

        assert container.facets["cli"] is replacement
        assert "needs-cli" in container.components