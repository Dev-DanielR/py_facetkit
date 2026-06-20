# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-06-20

### Added

- `overwrite` parameter on `mount_facet` and `add_component` (default `True`; pass `False` to block duplicate keys)
- `DuplicateFacetError` and `DuplicateComponentError` for blocked duplicate registration
- `Component.required_components` class attribute for declarative peer dependencies
- `Component.required_facets` class attribute for declarative facet mount dependencies
- `MissingComponentDependencyError` raised on attach when required components are absent
- `MissingFacetDependencyError` raised on attach when required facets are not mounted
- `DependentComponentsError` raised on remove when other components still depend on it
- `FacetInUseError` raised on unmount when attached components still depend on the facet
- Added '/docs' folder, with explanations for container, facet and component.
- Added '/docs/examples' folder, with an example of a composable app.

[0.3.0]: https://github.com/Dev-DanielR/py_facetkit/releases/tag/v0.3.0

## [0.2.0] - 2026-06-19

### Added

- `Container.get()` now does a strict check if a default value is omitted

[0.2.0]: https://github.com/Dev-DanielR/py_facetkit/releases/tag/v0.2.0

## [0.1.0] - 2026-06-18

### Added

- `Container` with config, component lifecycle, and facet mounting
- Passive facets: `CliFacet`, `TuiFacet`, `GuiFacet`, `WebFacet`, `ServiceFacet`
- `Component` attach/detach protocol for composable plugins
- `Container.get()` introspection via glom paths
- Descriptor types for registry entries (`Command`, `RouteDescriptor`, etc.)
- CLI command descriptions derived from handler docstrings

[0.1.0]: https://github.com/Dev-DanielR/py_facetkit/releases/tag/v0.1.0
