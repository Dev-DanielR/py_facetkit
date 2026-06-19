# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-18

### Added

- `Container` with config, component lifecycle, and facet mounting
- Passive facets: `CliFacet`, `TuiFacet`, `GuiFacet`, `WebFacet`, `ServiceFacet`
- `Component` attach/detach protocol for composable plugins
- `Container.get()` introspection via glom paths
- Descriptor types for registry entries (`Command`, `RouteDescriptor`, etc.)
- CLI command descriptions derived from handler docstrings

[0.1.0]: https://github.com/Dev-DanielR/facetkit/releases/tag/v0.1.0