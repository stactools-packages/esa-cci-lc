import logging
import os
import tempfile
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import rasterio
import rasterio.crs
import rioxarray  # noqa: F401
import xarray
from netCDF4 import Dataset, Variable
from osgeo import gdal
from pystac import Asset, CommonMetadata
from pystac.extensions.projection import ProjectionExtension
from rasterio.enums import Resampling

from . import classes, constants

logger = logging.getLogger(__name__)


def create_asset(
    key: str,
    href: Optional[str] = None,
    title: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Creates a basic COG asset dict with shared core properties and optionally an href.
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
        if key == "lccs_class"
        else constants.COG_ROLES_QUALITY,
    }

    band = {
        "spatial_resolution": constants.RESOLUTION,
        "sampling": constants.SAMPLING,
    }

    if href is not None:
        asset["href"] = href
    if title is not None:
        asset["title"] = title
    if key in constants.COG_DESCRIPTIONS:
        asset["description"] = constants.COG_DESCRIPTIONS[key]
    if key in constants.TABLES:
        table = constants.TABLES[key]
        asset["classification:classes"] = classes.to_stac(table)
        # Determine nodata value
        nodata = list(filter(lambda cls: len(cls) >= 6 and cls[5] is True, table))
        if len(nodata) == 1:
            band["nodata"] = nodata[0][0]

    asset["raster:bands"] = [band]

    return asset


def create_from_var(
    source: str, dest: str, dataset: Dataset, var: Variable, ovr_class_resampling: str
) -> Asset:
    """
    Converts the given variable to a COG stored in `dest`.
    This takes a three step approach for best efficiency:
    1. Writes the variable to GeoTiff as fast as possible
    2. It then adds additional metadata and overviews to the GeoTiff.
    3. Lastly, it restructures the GeoTiff into a proper COG.
    Some more details:
    https://github.com/stactools-packages/esa-cci-lc/issues/1

    Args:
        source (str): The source netCDF file
        dest (str): The path to the newly created COG file
        dataset (Dataset): The source netCDF4 dataset
        var (Variable): The source netCDF4 variable

    Returns:
        Asset: Asset object
    """
    dest_path = os.path.join(dest, f"{var.name}.tif")

    t1 = time.time()
    logger.info(f"Open {source}")
    xds = xarray.open_dataset(source)

    with tempfile.TemporaryDirectory() as tmpdirname:
        t2 = time.time() - t1
        temp_path = os.path.join(tmpdirname, os.path.basename(dest_path))
        logger.info(f"Write GeoTiff {temp_path} - elapsed: {t2}")
        xds[var.name].rio.to_raster(
            temp_path,
            windowed=True,
            compress="PACKBITS",
            bigtiff="YES",  # True throws a warning sometimes
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
                # Add missing CRS
                crs_var = dataset.variables["crs"]
                if "wkt" in crs_var.ncattrs():
                    dst.crs = rasterio.crs.CRS.from_wkt(crs_var.getncattr("wkt"))

                # by default average is good for the imagery with the counts, but average leads to
                # black artifacts in the land cover imagery so use mode (or nearest) instead
                resampling = Resampling.average

                # Special handling for the classes, other resampling and add a color map
                if var.name == "lccs_class":
                    # Add color map...
                    colors: Dict[str, Tuple[int]] = {}
                    for row in classes.TABLE:
                        if row[1] is not None:
                            colors[row[0]] = tuple(row[1]) + (255,)  # type: ignore[assignment]

                    if len(colors) > 0:
                        dst.write_colormap(1, colors)
                    # ... so that mode works for resampling
                    # https://github.com/rasterio/rasterio/issues/2624
                    if ovr_class_resampling == "nearest":
                        resampling = Resampling.nearest
                    else:
                        resampling = Resampling.mode

                dst.build_overviews(OVERVIEW_LEVELS, resampling)
                dst.update_tags(ns="rio_overview", resampling=resampling.name)
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

        t5 = time.time() - t1
        logger.info(f"Finished {dest_path} - elapsed: {t5}")

    title = var.getncattr("long_name")
    if isinstance(title, str) and len(title) > 0:
        title = title[0].upper() + title[1:]
    else:
        title = None

    asset_dict = create_asset(var.name, dest_path, title)
    asset = Asset.from_dict(asset_dict)

    # Creation time
    common_asset = CommonMetadata(asset)
    common_asset.created = datetime.now(tz=timezone.utc)

    # Projection details
    proj_asset_attrs = ProjectionExtension.ext(asset)
    proj_asset_attrs.shape = [src.RasterXSize, src.RasterYSize]
    proj_asset_attrs.transform = src.GetGeoTransform()

    # Close file handler for GDAL
    src = None

    return asset
