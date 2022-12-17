#!/usr/bin/env python3

"""Creates the example STAC and COGs.

Assumptions:
- The test suite has been run, so all external data have been downloaded.
"""

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from pystac import Catalog, CatalogType
import stactools.core.copy

from stactools.esa_cci_lc.cog import stac as cog_stac
from stactools.esa_cci_lc.constants import DESCRIPTION

root = Path(__file__).parent.parent
examples = root / "examples"
data_files = root / "tests" / "data-files" / "external"


with TemporaryDirectory() as tmp_dir:
    catalog = Catalog("esa-cci-lc", DESCRIPTION, "ESA CCI Land Cover")

    print("Creating COG collection...")
    cog = cog_stac.create_collection()
    cog_item = cog_stac.create_items(
        str(data_files / "C3S-LC-L4-LCCS-Map-300m-P1Y-2018-v2.1.1.nc"),
        tmp_dir,
        cog_tile_dim=4050,
        tile_row_col=[0, 0]
    )[0]
    cog_item.properties.pop("created")
    cog.add_item(cog_item)
    catalog.add_child(cog)

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
