from pathlib import Path
from tempfile import TemporaryDirectory
from tests import test_data

from stactools.esa_cci_lc.cog.stac import create_items, create_collection


def test_create_items_v21() -> None:
    nc_filename = "C3S-LC-L4-LCCS-Map-300m-P1Y-2018-v2.1.1.nc"
    nc_path = test_data.get_external_data(nc_filename)
    with TemporaryDirectory() as tmp_dir:
        items = create_items(nc_path, tmp_dir, cog_tile_dim=4050, tile_row_col=[0, 0])
        assert len(items) == 1
        cogs = list(Path(tmp_dir).glob("*.tif"))
        assert len(cogs) == 5
    # TODO: Add stac api url for netcdf collection


def test_create_items_v20() -> None:
    nc_filename = "ESACCI-LC-L4-LCCS-Map-300m-P1Y-2008-v2.0.7cds.nc"
    nc_path = test_data.get_external_data(nc_filename)
    with TemporaryDirectory() as tmp_dir:
        items = create_items(nc_path, tmp_dir, cog_tile_dim=4050, tile_row_col=[0, 0])
        assert len(items) == 1
        cogs = list(Path(tmp_dir).glob("*.tif"))
        assert len(cogs) == 5
    # TODO: Add stac api url for netcdf collection


def test_create_collection() -> None:
    collection = create_collection()
    assert collection.id == "esa-cci-lc"
