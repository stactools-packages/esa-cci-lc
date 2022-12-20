from pathlib import Path
from tempfile import TemporaryDirectory

from pystac import Item

from stactools.esa_cci_lc.cog import stac
from tests import test_data


def test_create_items_v21() -> None:
    nc_filename = "C3S-LC-L4-LCCS-Map-300m-P1Y-2018-v2.1.1.nc"
    nc_path = test_data.get_external_data(nc_filename)
    with TemporaryDirectory() as tmp_dir:
        items = stac.create_items(
            nc_path=nc_path,
            cog_dir=tmp_dir,
            cog_tile_dim=4050,
            tile_col_row=[0, 0],
            nc_api_url="https://dummyapi/collections/esa-cci-lc/items",
        )
        assert len(items) == 1
        cogs = list(Path(tmp_dir).glob("*.tif"))
        assert len(cogs) == 5

        def count_links(_item: Item) -> int:
            count = 0
            for link in _item.links:
                if link.rel == "derived_from":
                    count += 1
                    assert link.title == "Source NetCDF"
            return count

        assert count_links(items[0]) == 1

        items[0].validate()


def test_create_items_v20() -> None:
    nc_filename = "ESACCI-LC-L4-LCCS-Map-300m-P1Y-2008-v2.0.7cds.nc"
    nc_path = test_data.get_external_data(nc_filename)
    with TemporaryDirectory() as tmp_dir:
        items = stac.create_items(
            nc_path, tmp_dir, cog_tile_dim=4050, tile_col_row=[0, 0]
        )
        assert len(items) == 1
        cogs = list(Path(tmp_dir).glob("*.tif"))
        assert len(cogs) == 5

        items[0].validate()


def test_create_collection() -> None:
    collection = stac.create_collection()
    assert collection.id == "esa-cci-lc"
