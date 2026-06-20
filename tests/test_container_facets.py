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

    def test_mount_facet(self, container):
        cli = CliFacet()
        container.mount_facet("cli", cli)

        assert container.facets["cli"] is cli
        assert container.get("facets.cli.commands") == {}

    def test_unmount_facet_clears_registry(self, container):
        cli = CliFacet()
        cli.add_command("ping", lambda: None)
        container.mount_facet("cli", cli)

        container.unmount_facet("cli")

        assert "cli" not in container.facets
        assert cli.commands == {}

    def test_remount_replaces_facet(self, container):
        first = CliFacet()
        second = CliFacet()
        first.add_command("old", lambda: None)

        container.mount_facet("cli", first)
        container.mount_facet("cli", second)

        assert container.facets["cli"] is second
        assert first.commands == {}

    def test_blocks_duplicate_facet_when_overwrite_disabled(self, container):
        first = CliFacet()
        second = CliFacet()
        first.add_command("old", lambda: None)

        container.mount_facet("cli", first)

        with pytest.raises(DuplicateFacetError) as exc:
            container.mount_facet("cli", second, overwrite=False)

        assert exc.value.name == "cli"
        assert container.facets["cli"] is first
        assert "old" in first.commands

    def test_compose_multiple_facets(self, container):
        container.mount_facet("cli", CliFacet())
        container.mount_facet("service", ServiceFacet())
        container.mount_facet("tui", TuiFacet())
        container.mount_facet("gui", GuiFacet())
        container.mount_facet("web", WebFacet())

        assert set(container.facets) == {"cli", "service", "tui", "gui", "web"}
        assert container.get("facets.cli.name") == "cli"
        assert container.get("facets.service.name") == "service"
        assert container.get("facets.tui.name") == "tui"
        assert container.get("facets.gui.name") == "gui"
        assert container.get("facets.web.name") == "web"


class TestComposableComponents:
    def test_component_registers_into_multiple_facets(self, container):
        class MultiFacetComponent:
            def attach(self, ctx):
                def status():
                    """Show status."""
                    return "ok"

                ctx.facets["cli"].add_command("status", status)
                ctx.facets["service"].add_provider("status", {"healthy": True})

            def detach(self, ctx):
                ctx.facets["cli"].remove_command("status")
                ctx.facets["service"].remove_provider("status")

        container.mount_facet("cli", CliFacet())
        container.mount_facet("service", ServiceFacet())
        container.add_component("status", MultiFacetComponent())

        assert "status" in container.get("facets.cli.commands")
        assert "status" in container.get("facets.service.providers")

        container.remove_component("status")

        assert "status" not in container.get("facets.cli.commands")
        assert "status" not in container.get("facets.service.providers")

    def test_attach_without_required_facet_raises(self, container):
        class NeedsCli:
            required_facets = ("cli",)

            def attach(self, ctx):
                ctx.facets["cli"].add_command("ping", lambda: None)

            def detach(self, ctx):
                pass

        with pytest.raises(MissingFacetDependencyError) as exc:
            container.add_component("needs-cli", NeedsCli())

        assert exc.value.component == "needs-cli"
        assert exc.value.missing == ("cli",)

    def test_attach_succeeds_when_required_facets_present(self, container):
        class NeedsCli:
            required_facets = ("cli",)

            def attach(self, ctx):
                ctx.facets["cli"].add_command("ping", lambda: None)

            def detach(self, ctx):
                ctx.facets["cli"].remove_command("ping")

        container.mount_facet("cli", CliFacet())
        container.add_component("needs-cli", NeedsCli())

        assert "ping" in container.get("facets.cli.commands")

    def test_attach_does_not_run_when_facet_requirements_unmet(self, container):
        class NeedsCli:
            required_facets = ("cli",)
            attached = False

            def attach(self, ctx):
                self.attached = True

            def detach(self, ctx):
                pass

        comp = NeedsCli()
        with pytest.raises(MissingFacetDependencyError):
            container.add_component("needs-cli", comp)

        assert comp.attached is False

    def test_unmount_fails_when_components_depend_on_facet(self, container):
        class NeedsCli:
            required_facets = ("cli",)

            def attach(self, ctx):
                ctx.facets["cli"].add_command("ping", lambda: None)

            def detach(self, ctx):
                ctx.facets["cli"].remove_command("ping")

        container.mount_facet("cli", CliFacet())
        container.add_component("needs-cli", NeedsCli())

        with pytest.raises(FacetInUseError) as exc:
            container.unmount_facet("cli")

        assert exc.value.facet == "cli"
        assert exc.value.dependents == ("needs-cli",)
        assert "cli" in container.facets

    def test_unmount_succeeds_after_dependent_components_removed(self, container):
        class NeedsCli:
            required_facets = ("cli",)

            def attach(self, ctx):
                ctx.facets["cli"].add_command("ping", lambda: None)

            def detach(self, ctx):
                ctx.facets["cli"].remove_command("ping")

        container.mount_facet("cli", CliFacet())
        container.add_component("needs-cli", NeedsCli())

        container.remove_component("needs-cli")
        container.unmount_facet("cli")

        assert "cli" not in container.facets

    def test_remount_facet_skips_dependent_check(self, container):
        class NeedsCli:
            required_facets = ("cli",)

            def attach(self, ctx):
                ctx.facets["cli"].add_command("ping", lambda: None)

            def detach(self, ctx):
                ctx.facets["cli"].remove_command("ping")

        container.mount_facet("cli", CliFacet())
        container.add_component("needs-cli", NeedsCli())

        replacement = CliFacet()
        container.mount_facet("cli", replacement)

        assert container.facets["cli"] is replacement
        assert "needs-cli" in container.components