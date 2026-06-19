from unittest.mock import MagicMock

import glom
import pytest

import facetkit.container as container_module
from facetkit import Container


class FakeComponent:
    def __init__(self):
        self.attached_to = []
        self.detached_from = []

    def attach(self, ctx):
        self.attached_to.append(ctx)

    def detach(self, ctx):
        self.detached_from.append(ctx)


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


class TestContainerAddComponent:
    def test_registers_component(self, container):
        comp = FakeComponent()
        container.add_component("logger", comp)

        assert container.components["logger"] is comp

    def test_attaches_component_to_container(self, container):
        comp = FakeComponent()
        container.add_component("logger", comp)

        assert container in comp.attached_to

    def test_replacing_component_detaches_old_one(self, container):
        old = FakeComponent()
        new = FakeComponent()

        container.add_component("logger", old)
        container.add_component("logger", new)

        assert container in old.detached_from
        assert container.components["logger"] is new
        assert container in new.attached_to


class TestContainerRemoveComponent:
    def test_removes_component(self, container):
        comp = FakeComponent()
        container.add_component("logger", comp)

        container.remove_component("logger")

        assert "logger" not in container.components

    def test_detaches_component_from_container(self, container):
        comp = FakeComponent()
        container.add_component("logger", comp)

        container.remove_component("logger")

        assert container in comp.detached_from

    def test_removing_missing_component_is_noop(self, container):
        container.remove_component("missing")

        assert container.components == {}

    def test_remove_does_not_call_detach_when_missing(self, container):
        comp = MagicMock()
        container.remove_component("logger")

        comp.detach.assert_not_called()