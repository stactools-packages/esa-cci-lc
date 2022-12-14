from pathlib import Path
from typing import Any, Dict, List, Tuple

from netCDF4 import Dataset
import rasterio
from rasterio.windows import Window
import rasterio.crs
import rasterio.shutil
from rasterio.io import MemoryFile
import numpy as np

from stactools.esa_cci_lc import constants, classes

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
    for dim in constants.DATA_SHAPE:
        if dim % tile_dim:
            raise ValueError(
                f"Source data shape '{constants.DATA_SHAPE}' is not evenly "
                "divisible by the tile dimension '{tile_dim}'."
            )

    num_rows = int(constants.DATA_SHAPE[0] / tile_dim)
    num_cols = int(constants.DATA_SHAPE[1] / tile_dim)
    deg_increment = int(360 / num_cols)

    windows = []
    for c in np.arange(0, num_cols):
        for r in np.arange(0, num_rows):
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


def make_cog_tiles(nc_href: str, cog_dir: str, tile_dim: int) -> Dict[str, List[str]]:
    windows = get_windows(tile_dim)
    cog_paths: Dict[str, List[str]] = {window["tile"]: [] for window in windows}
    for variable in constants.DATA_VARIABLES:
        with rasterio.open(f"netcdf:{nc_href}:{variable}") as src:
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
                    / f"{Path(nc_href).stem}-{window['tile']}-{variable}.tif"
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


# if __name__ == "__main__":
#     nc_href = "/Volumes/Samsung_T5/data/esa-cci/ESACCI-LC-L4-LCCS-Map-300m-P1Y-1992-v2.0.7cds.nc"
#     cog_dir = "pjh/cogs"
#     tile_dim = 16200
#     cogs = make_cog_tiles(
#         nc_href,
#         cog_dir,
#         tile_dim,
#     )
#     print(cogs)
