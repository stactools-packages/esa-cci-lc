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
        if key == "lccs_class"
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


def create_from_var(source: str, dest: str, dataset: Dataset, var: Variable) -> Asset:
    dest_path = os.path.join(dest, f"{var.name}.tif")

    t1 = time.time()
    logger.info(f"Open {source}")
    xds = xarray.open_dataset(source)

    with tempfile.TemporaryDirectory() as tmpdirname:
        t2 = time.time() - t1
        temp_path = os.path.join(tmpdirname, os.path.basename(dest_path))
        logger.info(f"[{t2}] Write intermediate GeoTiff {temp_path}")
        # Convert to a GeoTiff as quickly as possible to be able to add overviews
        xds[var.name].rio.to_raster(
            temp_path,
            windowed=True,
            compress="PACKBITS",  # Best compromise of speed and size
            bigtiff=True,  # observation_count may reach 4GB in some cases
            tiled=True,
            blockxsize=2048,  # closest to the 2025 tiling in the netcdf and
            blockysize=2048,  # and was most efficient in my tests
        )

        t3 = time.time() - t1
        logger.info(f"[{t3}] Prepare final file")
        OVERVIEW_LEVELS = [2, 4, 8, 16, 32, 64, 128, 256]
        with rasterio.open(temp_path, "r+") as src:
            if var.name == "observation_count":
                logger.info(f"SKIPPED Overviews for variable {var.name}")
                overviews = "NONE"
            else:
                # Add overviews (to the end of the file, i.e. this is not a COG yet)
                # By default average is good for the imagery with the counts, but average
                # leads to black artifacts in the land cover imagery so use nearest instead
                resampling = Resampling.average
                if var.name == "lccs_class":
                    resampling = Resampling.nearest
                src.build_overviews(OVERVIEW_LEVELS, resampling)
                src.update_tags(ns="rio_overview", resampling=resampling.name)
                overviews = "FORCE_USE_EXISTING"

            t4 = time.time() - t1
            logger.info(f"[{t4}] Convert to COG {dest_path}")
            profile = src.profile
            profile["driver"] = "COG"
            profile["COMPRESS"] = "DEFLATE"
            profile["LEVEL"] = 9
            profile["NUM_THREADS"] = "ALL_CPUS"
            profile["PREDICTOR"] = "Yes"
            profile["OVERVIEWS"] = overviews
            with rasterio.open(dest_path, "w", **profile) as dst:
                # Add missing CRS
                crs_var = dataset.variables["crs"]
                if "wkt" in crs_var.ncattrs():
                    src.crs = rasterio.crs.CRS.from_wkt(crs_var.getncattr("wkt"))

                # Add color map
                if var.name == "lccs_class":
                    colors: Dict[str, Tuple[int]] = {}
                    for row in classes.TABLE:
                        if row[1] is not None:
                            colors[row[0]] = tuple(row[1]) + (255,)  # type: ignore[assignment]

                    if len(colors) > 0:
                        dst.write_colormap(1, colors)
                
                # Write data (windowed)
                for _, window in src.block_windows(1):
                    dst.write(src.read(window=window))

                # Write data (all at once)
                # dst.write(src.read())


            t5 = time.time() - t1
            logger.info(f"[{t5}] Finished {dest_path}")

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
