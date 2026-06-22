import pytest

from facetkit import Container


@pytest.fixture
def config():
    return {"app": {"name": "test-app", "debug": True}, "port": 8080}


@pytest.fixture
def container(config):
    return Container(config)


@pytest.fixture
def composed_app(container):
    from facetkit import CliFacet, ServiceFacet

    container.bind_facet("cli", CliFacet())
    container.bind_facet("service", ServiceFacet())
    return container