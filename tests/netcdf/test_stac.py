from stactools.esa_cci_lc.netcdf.stac import create_collection, create_item
from tests import test_data


def test_create_item_v21() -> None:
    nc_filename = "C3S-LC-L4-LCCS-Map-300m-P1Y-2018-v2.1.1.nc"
    nc_path = test_data.get_external_data(nc_filename)
    item = create_item(nc_path)
    assert item.id == "C3S-LC-L4-LCCS-Map-300m-P1Y-2018-v2.1.1"
    assert len(item.assets) == 1
    assert "netcdf" in item.assets
    assert "processing:software" in item.properties
    assert "processing:lineage" in item.properties

    item.validate()


def test_create_item_v20() -> None:
    nc_filename = "ESACCI-LC-L4-LCCS-Map-300m-P1Y-2008-v2.0.7cds.nc"
    nc_path = test_data.get_external_data(nc_filename)
    item = create_item(nc_path)
    assert item.id == "ESACCI-LC-L4-LCCS-Map-300m-P1Y-2008-v2.0.7cds"
    assert len(item.assets) == 1
    assert "netcdf" in item.assets
    assert "processing:software" in item.properties
    assert "processing:lineage" in item.properties

    item.validate()


def test_create_collection() -> None:
    collection = create_collection()
    assert collection.id == "esa-cci-lc-netcdf"
