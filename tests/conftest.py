import pytest

from py_container import Container


@pytest.fixture
def config():
    return {"app": {"name": "test-app", "debug": True}, "port": 8080}


@pytest.fixture
def container(config):
    return Container(config)


@pytest.fixture
def composed_app(container):
    from py_container import CliFacet, ServiceFacet

    container.mount_facet("cli", CliFacet())
    container.mount_facet("service", ServiceFacet())
    return container