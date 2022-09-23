# stactools-esa-cci-lc

[![PyPI](https://img.shields.io/pypi/v/stactools-esa-cci-lc)](https://pypi.org/project/stactools-esa-cci-lc/)

- Name: esa-cci-lc
- Package: `stactools.esa_cci_lc`
- [stactools-esa-cci-lc on PyPI](https://pypi.org/project/stactools-esa-cci-lc/)
- Owner: @m-mohr
- [Dataset homepage](http://example.com)
- STAC extensions used:
  - [proj](https://github.com/stac-extensions/projection/)
- Extra fields:
  - `esa-cci-lc:custom`: A custom attribute
- [Browse the example in human-readable form](https://radiantearth.github.io/stac-browser/#/external/raw.githubusercontent.com/stactools-packages/esa-cci-lc/main/examples/collection.json)

stactools package for ESA's Climate Change Initiative (CCI) Land Cover (LC) product.

## STAC Examples

- [Collection](examples/collection.json)
- [Item](examples/item/item.json)

## Installation

```shell
pip install stactools-esa-cci-lc
```

## Command-line Usage

Description of the command line functions

```shell
stac esa-cci-lc create-item source destination
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
