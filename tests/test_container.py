from unittest.mock import MagicMock

import glom
import pytest

import facetkit.container as container_module
from facetkit import (
    Container,
    ComponentInUseError,
    DuplicateComponentError,
    MissingComponentDependencyError,
)


class FakeComponent:
    def __init__(self):
        self.bound_to = []
        self.unbound_from = []

    def on_bind(self, container):
        self.bound_to.append(container)

    def on_unbind(self, container):
        self.unbound_from.append(container)


class TestContainerInit:
    def test_stores_config(self, config):
        container = Container(config)
        assert container.config is config

    def test_starts_with_empty_components(self, config):
        container = Container(config)
        assert container.components == {}

class TestContainerGet:
    def test_empty_path_returns_self(self, container):
        assert container.get("") is container

    def test_retrieves_top_level_attribute(self, container):
        assert container.get("config") is container.config

    def test_retrieves_nested_config_value(self, container):
        assert container.get("config.app.name") == "test-app"

    def test_retrieves_scalar_config_value(self, container):
        assert container.get("config.port") == 8080

    def test_missing_path_returns_default(self, container):
        assert container.get("config.missing", default="fallback") == "fallback"

    def test_missing_path_returns_none_when_default_is_none(self, container):
        assert container.get("config.missing", default=None) is None

    def test_missing_path_raises_without_default(self, container):
        with pytest.raises(glom.PathAccessError):
            container.get("config.missing")

    def test_glom_error_raises_without_default(self, container, monkeypatch):
        def raise_glom_error(*_args, **_kwargs):
            raise glom.GlomError("boom")

        monkeypatch.setattr(container_module.glom, "glom", raise_glom_error)
        with pytest.raises(glom.GlomError):
            container.get("config.app.name")

    def test_unexpected_exception_raises_without_default(self, container, monkeypatch):
        def raise_runtime_error(*_args, **_kwargs):
            raise RuntimeError("unexpected")

        monkeypatch.setattr(container_module.glom, "glom", raise_runtime_error)
        with pytest.raises(RuntimeError):
            container.get("config.app.name")

    def test_glom_error_returns_default(self, container, monkeypatch):
        def raise_glom_error(*_args, **_kwargs):
            raise glom.GlomError("boom")

        monkeypatch.setattr(container_module.glom, "glom", raise_glom_error)
        assert container.get("config.app.name", default="safe") == "safe"

    def test_unexpected_exception_returns_default(self, container, monkeypatch):
        def raise_runtime_error(*_args, **_kwargs):
            raise RuntimeError("unexpected")

        monkeypatch.setattr(container_module.glom, "glom", raise_runtime_error)
        assert container.get("config.app.name", default="safe") == "safe"


class TestContainerBindComponent:
    def test_binds_component(self, container):
        comp = FakeComponent()
        container.bind_component("logger", comp)

        assert container.components["logger"] is comp

    def test_on_bind_called_when_component_bound(self, container):
        comp = FakeComponent()
        container.bind_component("logger", comp)

        assert container in comp.bound_to

    def test_replacing_component_calls_on_unbind_on_old_one(self, container):
        old = FakeComponent()
        new = FakeComponent()

        container.bind_component("logger", old)
        container.bind_component("logger", new)

        assert container in old.unbound_from
        assert container.components["logger"] is new
        assert container in new.bound_to

    def test_blocks_duplicate_component_when_overwrite_disabled(self, container):
        first = FakeComponent()
        second = FakeComponent()

        container.bind_component("logger", first)

        with pytest.raises(DuplicateComponentError) as exc:
            container.bind_component("logger", second, overwrite=False)

        assert exc.value.component_id == "logger"
        assert container.components["logger"] is first
        assert second.bound_to == []
        assert first.unbound_from == []


class TestContainerUnbindComponent:
    def test_unbinds_component(self, container):
        comp = FakeComponent()
        container.bind_component("logger", comp)

        container.unbind_component("logger")

        assert "logger" not in container.components

    def test_on_unbind_called_when_component_unbound(self, container):
        comp = FakeComponent()
        container.bind_component("logger", comp)

        container.unbind_component("logger")

        assert container in comp.unbound_from

    def test_unbinding_missing_component_is_noop(self, container):
        container.unbind_component("missing")

        assert container.components == {}

    def test_unbind_does_not_call_on_unbind_when_missing(self, container):
        comp = MagicMock()
        container.unbind_component("logger")

        comp.on_unbind.assert_not_called()


class TestComponentDependencies:
    def test_on_bind_succeeds_when_required_components_present(self, container):
        class Logger(FakeComponent):
            pass

        class Api(FakeComponent):
            required_components = ("logger",)

        container.bind_component("logger", Logger())
        container.bind_component("api", Api())

        assert "api" in container.components
        assert container in container.components["api"].bound_to

    def test_on_bind_fails_when_required_component_missing(self, container):
        class Api(FakeComponent):
            required_components = ("logger",)

        with pytest.raises(MissingComponentDependencyError) as exc:
            container.bind_component("api", Api())

        assert exc.value.component_id == "api"
        assert exc.value.missing == ("logger",)
        assert "api" not in container.components

    def test_on_bind_does_not_run_when_requirements_unmet(self, container):
        class Api(FakeComponent):
            required_components = ("logger",)

        api = Api()
        with pytest.raises(MissingComponentDependencyError):
            container.bind_component("api", api)

        assert api.bound_to == []

    def test_unbind_fails_when_other_components_depend_on_it(self, container):
        class Logger(FakeComponent):
            pass

        class Api(FakeComponent):
            required_components = ("logger",)

        container.bind_component("logger", Logger())
        container.bind_component("api", Api())

        with pytest.raises(ComponentInUseError) as exc:
            container.unbind_component("logger")

        assert exc.value.component_id == "logger"
        assert exc.value.dependents == ("api",)
        assert "logger" in container.components

    def test_unbind_succeeds_after_dependents_unbound(self, container):
        class Logger(FakeComponent):
            pass

        class Api(FakeComponent):
            required_components = ("logger",)

        container.bind_component("logger", Logger())
        container.bind_component("api", Api())

        container.unbind_component("api")
        container.unbind_component("logger")

        assert container.components == {}

    def test_replacing_component_skips_dependent_check(self, container):
        class Logger(FakeComponent):
            pass

        class Api(FakeComponent):
            required_components = ("logger",)

        container.bind_component("logger", Logger())
        container.bind_component("api", Api())

        replacement = Logger()
        container.bind_component("logger", replacement)

        assert container.components["logger"] is replacement
        assert "api" in container.components