# ESA CCI LC Extension Specification

- **Title:** ESA Climate Change Initiative (CCI) Land Cover (LC)
- **Identifier:** <https://raw.githubusercontent.com/stactools-packages/esa-cci-lc/main/extension/schema.json>
- **Field Name Prefix:** esa_cci_lc
- **Scope:** Item, Collection
- **Extension [Maturity Classification](https://github.com/radiantearth/stac-spec/tree/master/extensions/README.md#extension-maturity):** Proposal
- **Owner**: @m-mohr

This document explains the ESA Climate Change Initiative (CCI) Land Cover (LC) Extension to the
[SpatioTemporal Asset Catalog](https://github.com/radiantearth/stac-spec) (STAC) specification.

- Examples:
  - [Item example](../examples/item-conus.json): Shows the basic usage of the extension in a STAC Item
  - [Collection example](../examples/collection.json): Shows the basic usage of the extension in a STAC Collection
- [JSON Schema](schema.json)

## Item Properties and Collection Summaries

| Field Name           | Type    | Description |
| -------------------- | ------- | ----------- |
| esa_cci_lc:version   | string  | **REQUIRED**. The version number of the dataset (one of: `2.1.1` or `2.0.7cds`) |

## Contributing

All contributions are subject to the
[STAC Specification Code of Conduct](https://github.com/radiantearth/stac-spec/blob/master/CODE_OF_CONDUCT.md).
For contributions, please follow the
[STAC specification contributing guide](https://github.com/radiantearth/stac-spec/blob/master/CONTRIBUTING.md) Instructions
for running tests are copied here for convenience.
