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
  - [processing](https://github.com/stac-extensions/processing/)
  - [proj](https://github.com/stac-extensions/projection/)
  - [raster](https://github.com/stac-extensions/raster/)
  - [version](https://github.com/stac-extensions/version/)
- Extra fields:
  - None

A stactools package for ESA's Climate Change Initiative (CCI) Land Cover (LC)
product.

This dataset provides global maps describing the land surface classes,
which have been defined using the United Nations Food and Agriculture
Organization's (UN FAO) Land Cover Classification System (LCCS).
In addition to the land cover (LC) maps, four quality flags are produced to
document the reliability of the classification and change detection.
In order to ensure continuity, these land cover maps are consistent with the
series of global annual LC maps from the 1990s to 2015 produced by the
European Space Agency (ESA) Climate Change Initiative (CCI).

This package can generate STAC files from netCDF files and that either link to
the original netCDF files or to Cloud-Optimized GeoTiff (COG) files.

## STAC Examples

- [Collection](examples/collection.json)
- [Item](examples/item.json)
- [Browse the example in human-readable form](https://radiantearth.github.io/stac-browser/#/external/raw.githubusercontent.com/stactools-packages/esa-cci-lc/main/examples/collection.json)

## Installation

```shell
pip install stactools-esa-cci-lc
```

## Command-line Usage

Use `stac esa-cci-lc --help` to see all subcommands and options.

### Collection

Create a collection:

```shell
stac esa-cci-lc create-collection collection.json
```

Get information about all options for collection creation:

```shell
stac esa-cci-lc create-collection --help
```

### Item

Create an item with netCDF and COG assets:

```shell
stac esa-cci-lc create-item /path/to/source/file.nc item.json --collection collection.json
```

Create an item with only COG assets:

```shell
stac esa-cci-lc create-item /path/to/source/file.nc item.json --collection collection.json --nonetcdf TRUE
```

Get information about all options for item creation:

```shell
stac esa-cci-lc create-item --help
```

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

**Note:** Due to the long processing time of the tests with COGs conversion (in total 3-4 hours on 
my local machine), the tests by default run without COG processing (i.e. `--nocog` is enabled).
To run the tests with COG generation, please run `pytest -vv --withcog`.
