from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import rasterio
from rasterio.windows import Window
import rasterio.crs
import rasterio.shutil
from rasterio.io import MemoryFile
import numpy as np

from .. import constants, classes

COG_PROFILE = {
    "compress": "deflate",
    "blocksize": 512,
    "driver": "COG",
    "overview_resampling": "average",
}
COG_CLASS_PROFILE = {
    "compress": "deflate",
    "blocksize": 512,
    "driver": "COG",
    "overview_resampling": "mode",
}


def get_windows(tile_dim: int) -> List[Dict[str, Any]]:
    for dim in constants.NETCDF_DATA_SHAPE:
        if dim % tile_dim:
            raise ValueError(
                f"Source data shape '{constants.NETCDF_DATA_SHAPE}' is not evenly "
                "divisible by the tile dimension '{tile_dim}'."
            )

    num_rows = int(constants.NETCDF_DATA_SHAPE[0] / tile_dim)
    num_cols = int(constants.NETCDF_DATA_SHAPE[1] / tile_dim)
    deg_increment = int(360 / num_cols)

    windows = []
    for c in range(0, num_cols):
        for r in range(0, num_rows):
            window = {}
            window["window"] = Window(c * tile_dim, r * tile_dim, tile_dim, tile_dim)

            bottom = 90 - (r + 1) * deg_increment
            bottom_text = f"{'S' if bottom < 0 else 'N'}{abs(bottom):02d}"
            left = (c * deg_increment) - 180
            left_text = f"{'W' if left < 0 else 'E'}{abs(left):03d}"
            window["tile"] = f"{bottom_text}{left_text}"

            windows.append(window)

    return windows


def get_colors() -> Dict[str, Tuple[int]]:
    colors: Dict[str, Tuple[int]] = {}
    for row in classes.TABLE:
        colors[row[0]] = tuple([*row[1], 255])
    return colors


def make_cog_tiles(nc_path: str, cog_dir: str, tile_dim: int) -> Dict[str, List[str]]:
    windows = get_windows(tile_dim)
    cog_paths: Dict[str, List[str]] = {window["tile"]: [] for window in windows}
    for variable in constants.DATA_VARIABLES:
        with rasterio.open(f"netcdf:{nc_path}:{variable}") as src:
            for window in windows:
                window_transform = src.window_transform(window["window"])
                window_data = src.read(1, window=window["window"])

                dst_profile = {
                    "driver": "GTiff",
                    "width": window["window"].width,
                    "height": window["window"].height,
                    "count": 1,
                    "dtype": window_data.dtype,
                    "transform": window_transform,
                    "crs": "EPSG:4326",
                }

                if variable == "current_pixel_state" or variable == "processed_flag":
                    window_data[window_data == -1] = 100
                    window_data = np.uint8(window_data)
                    window_data[window_data == 100] = 255
                    dst_profile.update({"dtype": "uint8", "nodata": 255})
                if variable == "lccs_class":
                    dst_profile.update({"nodata": 0})

                cog_path = (
                    Path(cog_dir)
                    / f"{Path(nc_path).stem}-{window['tile']}-{variable}.tif"
                )

                with MemoryFile() as mem_file:
                    with mem_file.open(**dst_profile) as mem:
                        mem.write(window_data, 1)
                        if variable == "lccs_class":
                            mem.write_colormap(1, get_colors())
                            rasterio.shutil.copy(mem, cog_path, **COG_CLASS_PROFILE)
                        rasterio.shutil.copy(mem, cog_path, **COG_PROFILE)

                cog_paths[window["tile"]].append(str(cog_path))

    return cog_paths


def create_cog_asset(
    cog_href: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Creates a basic COG asset dict with shared core properties and optionally an href.
    An href should be given for normal assets, but can be None for Item Asset
    Definitions.

    Args:
        cog_href (str): The URL to the asset

    Returns:
        dict: Basic Asset object
    """
    key = Path(cog_href).stem.split("-")[-1]
    asset: Dict[str, Any] = {
        "type": constants.COG_MEDIA_TYPE,
        "href": cog_href,
        "title": constants.COG_INFO[key]["title"],
        "description": constants.COG_INFO[key]["description"],
        "roles": constants.COG_ROLES_DATA
        if key == "lccs_class"
        else constants.COG_ROLES_QUALITY,
    }

    band = {
        "spatial_resolution": constants.RESOLUTION,
        "sampling": constants.SAMPLING,
    }

    if key in constants.TABLES:
        table = constants.TABLES[key]
        asset["classification:classes"] = classes.to_stac(table)
        # Determine nodata value
        nodata = list(filter(lambda cls: len(cls) >= 6 and cls[5] is True, table))
        if len(nodata) == 1:
            band["nodata"] = nodata[0][0]

    asset["raster:bands"] = [band]

    # TODO: Add data type to raster band
    # TODO: Correct nodata to match new COGs

    return asset
