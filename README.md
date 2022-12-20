# stactools-esa-cci-lc

[![PyPI](https://img.shields.io/pypi/v/stactools-esa-cci-lc)](https://pypi.org/project/stactools-esa-cci-lc/)

- Name: esa-cci-lc
- Package: `stactools.esa_cci_lc`
- [stactools-esa-cci-lc on PyPI](https://pypi.org/project/stactools-esa-cci-lc/)
- Owner: @m-mohr
- Dataset homepage:
  - <https://cds.climate.copernicus.eu/cdsapp#!/dataset/satellite-land-cover>
- STAC extensions used:
  - [classification](https://github.com/stac-extensions/classification/)
  - [datacube](https://github.com/stac-extensions/datacube/)
  - [grid](https://github.com/stac-extensions/grid/)
  - [item-assets](https://github.com/stac-extensions/item-assets)
  - [processing](https://github.com/stac-extensions/processing/)
  - [projection](https://github.com/stac-extensions/projection/)
  - [raster](https://github.com/stac-extensions/raster/)
  - [scientific](https://github.com/stac-extensions/scientific)
- Extra fields:
  - `esa_cci_lc:version`: Land cover product version.
- [Browse the example in human-readable form](https://radiantearth.github.io/stac-browser/#/external/raw.githubusercontent.com/stactools-packages/esa-cci-lc/main/examples/catalog.json)

## Background

A stactools package for ESA's Climate Change Initiative (CCI) Land Cover (LC)
product. The ESA CCI LC dataset provides global maps describing the land surface classes,
which have been defined using the United Nations Food and Agriculture
Organization's (UN FAO) Land Cover Classification System (LCCS).
In addition to the land cover (LC) maps, four quality flags are produced to
document the reliability of the classification and change detection.

Two STAC Collections, and corresponding Items, can be generated with this package:

1. esa-cci-lc: A Collection of COG tiles generated from the source NetCDF data files.
2. esa-cci-lc-netcdf: A Collection describing the source NetCDF data files.

If you are interested in creating single STAC Items for each source NetCDF file along with worldwide COGs (not tiled), see release [v0.1.0](https://github.com/stactools-packages/esa-cci-lc/releases/tag/v0.1.0).

## STAC Examples

- Collections
  - [Tiled COGs](examples/esa-cci-lc/collection.json)
  - [Source NetCDF](examples/esa-cci-lc-netcdf/collection.json)

- Items
  - [Tiled COGs](examples/esa-cci-lc/C3S-LC-L4-LCCS-Map-300m-P1Y-2018-v2.1.1-N79W180/C3S-LC-L4-LCCS-Map-300m-P1Y-2018-v2.1.1-N79W180.json)
  - [Source NetCDF](examples/esa-cci-lc-netcdf/C3S-LC-L4-LCCS-Map-300m-P1Y-2018-v2.1.1/C3S-LC-L4-LCCS-Map-300m-P1Y-2018-v2.1.1.json)

The example Collections and Items in the `examples` directory can be created by running `./scripts/create_examples.py`.

## Installation

```shell
pip install stactools-esa-cci-lc
```

## Command-line Usage

To create the NetCDF Collection:

```shell
stac esa-cci-lc netcdf create-collection collection.json
```

To convert a NetCDF to tiled COGs and create an Item for each tile:

```shell
stac esa-cci-lc cog create-items /path/to/source/file.nc /path/to/output/directory
```

Use `stac esa-cci-lc --help` to see all subcommands and options.

## Contributing

We use [pre-commit](https://pre-commit.com/) to check any changes.
To set up your development environment:

```shell
pip install -e .
pip install -r requirements-dev.txt
pre-commit install
```

To check all files:

```shell
pre-commit run --all-files
```

To run the tests:

```shell
pytest -vv
```
