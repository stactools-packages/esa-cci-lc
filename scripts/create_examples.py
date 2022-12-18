#!/usr/bin/env python3

"""Creates the example STAC and COGs.

Assumptions:
- The test suite has been run, so all external data have been downloaded.
"""

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import stactools.core.copy
from pystac import Catalog, CatalogType

from stactools.esa_cci_lc.cog import stac as cog_stac
from stactools.esa_cci_lc.netcdf import stac as netcdf_stac

root = Path(__file__).parent.parent
examples = root / "examples"
data_files = root / "tests" / "data-files" / "external"

DESCRIPTION = (
    "The ESA Climate Change Initiative (CCI) dataset provides global maps "
    "describing land surface classes, which have been defined using the "
    "United Nations Food and Agriculture Organization's (UN FAO) Land Cover "
    "Classification System (LCCS). In addition to the land cover (LC) maps, "
    "four quality flags are produced to document the reliability of the "
    "classification and change detection."
)

with TemporaryDirectory() as tmp_dir:
    catalog = Catalog("esa-cci-lc", DESCRIPTION, "ESA CCI Land Cover")

    print("Creating COG collection...")
    cog = cog_stac.create_collection()
    cog_item = cog_stac.create_items(
        str(data_files / "C3S-LC-L4-LCCS-Map-300m-P1Y-2018-v2.1.1.nc"),
        tmp_dir,
        cog_tile_dim=4050,
        tile_col_row=[0, 0],
    )[0]
    cog_item.properties.pop("created")
    cog.add_item(cog_item)
    cog.update_extent_from_items()
    catalog.add_child(cog)

    print("Creating NetCDF collection...")
    netcdf = netcdf_stac.create_collection()
    netcdf_item = netcdf_stac.create_item(
        str(data_files / "C3S-LC-L4-LCCS-Map-300m-P1Y-2018-v2.1.1.nc")
    )
    netcdf_item.properties.pop("created")
    netcdf.add_item(netcdf_item)
    netcdf.update_extent_from_items()
    catalog.add_child(netcdf)

    print("Saving catalog...")
    catalog.normalize_hrefs(str(examples))
    if examples.exists():
        shutil.rmtree(examples)
    for item in catalog.get_all_items():
        for asset in item.assets.values():
            if asset.href.startswith(tmp_dir):
                href = stactools.core.copy.move_asset_file_to_item(
                    item, asset.href, copy=False
                )
                asset.href = href
        item.make_asset_hrefs_relative()
    catalog.save(catalog_type=CatalogType.SELF_CONTAINED)

    print("Done!")
