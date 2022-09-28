import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import rasterio
import rioxarray  # noqa: F401
import xarray
from netCDF4 import Variable
from osgeo import gdal
from pystac import Asset, CommonMetadata

from . import classes, constants

logger = logging.getLogger(__name__)


def create_asset(
    key: str,
    href: Optional[str] = None,
    title: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Creates a basic COG asset dict with shared core properties (title,
    type, roles) and optionally an href.
    An href should be given for normal assets, but can be None for Item Asset
    Definitions.

    Args:
        title (str): A title for the asset
        href (str): The URL to the asset (optional)

    Returns:
        dict: Basic Asset object
    """
    asset: Dict[str, Any] = {
        "type": constants.COG_MEDIA_TYPE,
        "roles": constants.COG_ROLES_DATA
        if key == "lcss_class"
        else constants.COG_ROLES_QUALITY,
    }

    if href is not None:
        asset["href"] = href
    if title is not None:
        asset["title"] = title
    if key in constants.COG_DESCRIPTIONS:
        asset["description"] = constants.COG_DESCRIPTIONS[key]
    if key in constants.TABLES:
        asset["classification:classes"] = classes.to_stac(constants.TABLES[key])

    return asset


def create_from_var(source: str, dest: str, var: Variable) -> Asset:
    dest_path = os.path.join(dest, f"{var.name}.tif")

    t1 = time.time()
    logger.info(f"Open {source}")
    xds = xarray.open_dataset(source)

    t2 = time.time() - t1
    temp_path = dest_path + "f"
    logger.info(f"Write GeoTiff {temp_path} - elapsed: {t2}")
    xds[var.name].rio.to_raster(
        temp_path,
        windowed=True,
        compress="PACKBITS",
        bigtiff=True,
        tiled=True,
        blockxsize=2048,
        blockysize=2048,  # closest to the 2025 tiling in the netcdf
    )

    overviews = "AUTO"
    if var.name != "observation_count":
        t3 = time.time() - t1
        logger.info(f"Generate overviews {temp_path} - elapsed: {t3}")
        OVERVIEW_LEVELS = [2, 4, 8, 16, 32, 64, 128, 256]
        with rasterio.open(temp_path, "r+") as dst:
            dst.build_overviews(OVERVIEW_LEVELS, rasterio.enums.Resampling.average)
            dst.update_tags(ns="rio_overview", resampling="average")
            overviews = "FORCE_USE_EXISTING"
    else:
        logger.info(f"SKIPPED Overviews {temp_path}")
        overviews = "NONE"

    t4 = time.time() - t1
    logger.info(f"Convert to COG {dest_path} - elapsed: {t4}")
    src = gdal.Open(temp_path)
    src = gdal.Translate(
        dest_path,
        src,
        format="COG",
        creationOptions=[
            "COMPRESS=DEFLATE",
            "LEVEL=9",
            "NUM_THREADS=ALL_CPUS",
            "PREDICTOR=YES",
            f"OVERVIEWS={overviews}",
        ],
    )
    src = None

    t5 = time.time() - t1
    logger.info(f"Finished {dest_path} - elapsed: {t5}")

    title = var.getncattr("long_name")
    if isinstance(title, str) and len(title) > 0:
        title = title[0].upper() + title[1:]
    else:
        title = None

    asset_dict = create_asset(var.name, dest_path, title)
    asset = Asset.from_dict(asset_dict)

    common_asset = CommonMetadata(asset)
    common_asset.created = datetime.now(tz=timezone.utc)

    return asset
