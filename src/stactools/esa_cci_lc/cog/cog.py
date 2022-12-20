import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import rasterio
import rasterio.crs
import rasterio.shutil
from pystac.utils import make_absolute_href
from rasterio.io import MemoryFile
from rasterio.windows import Window
from shapely.geometry import box, mapping
from stactools.core.io import ReadHrefModifier

from .. import classes, constants

logger = logging.getLogger(__name__)

COG_PROFILE = {
    "compress": "deflate",
    "blocksize": 512,
    "driver": "COG",
    "overview_resampling": "average",
}


def make_cog_tiles(
    nc_path: str, cog_dir: str, tile_dim: int, tile_col_row: Optional[List[int]] = None
) -> List[List[str]]:
    """Generates tiled COGs from NetCDF variables. There are five variables of
    interest, so five COGs are generated for each tile.

    Args:
        nc_path (str): Local path to NetCDF file.
        cog_dir (str): Local directory to store creatd COGs.
        cog_tile_dim (Optional[int]): Optional COG tile dimension in pixels.
            Defaults to ``constants.COG_TILE_DIM``.
        tile_col_row (Optional[List[int]]): Optional tile grid column and row
            indices. Use to create an Item and COGs for a single tile. Indices
            are 0 based.

    Returns:
        List[List[str]]: List of lists of tiled COG paths. Each inner list
            contains the five COG paths for a single tile.
    """
    windows = get_windows(tile_dim, tile_col_row)
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
                            mem.write_colormap(1, _get_colormap())
                            cog_profile_mode = COG_PROFILE.copy()
                            cog_profile_mode["overview_resampling"] = "mode"
                            rasterio.shutil.copy(mem, cog_path, **cog_profile_mode)
                        else:
                            rasterio.shutil.copy(mem, cog_path, **COG_PROFILE)

                cog_paths[window["tile"]].append(str(cog_path))

    return [value for value in cog_paths.values()]


def get_windows(
    tile_dim: int, tile_col_row: Optional[List[int]] = None
) -> List[Dict[str, Any]]:
    """Creates rasterio ``Window`` objects and tile ID strings. The tile IDs are
    the geographic coordinates of the lower left tile corner rounded to the
    nearest degree. Unless ``tile_col_row`` is passed, objects and IDs will be
    generated for all tiles in a tile grid defined by ``tile_dim``.

    Args:
        cog_tile_dim (Optional[int]): Optional COG tile dimension in pixels.
            Defaults to ``constants.COG_TILE_DIM``.
        tile_col_row (Optional[List[int]]): Optional tile grid column and row
            indices. Use to create an Item and COGs for a single tile. Indices
            are 0 based.

    Returns:
        List[Dict[str, Any]]: List of dictionaries containing a rasterio
            ``Window`` object and Tile ID string.
    """
    for dim in constants.NETCDF_DATA_SHAPE:
        if dim % tile_dim:
            raise ValueError(
                f"Source data shape '{constants.NETCDF_DATA_SHAPE}' is not evenly "
                "divisible by the tile dimension '{tile_dim}'."
            )

    num_cols = int(constants.NETCDF_DATA_SHAPE[1] / tile_dim)
    cols = list(range(0, num_cols))
    num_rows = int(constants.NETCDF_DATA_SHAPE[0] / tile_dim)
    rows = list(range(0, num_rows))

    if 360 % num_cols:
        logger.warning(
            "Non-integer tile degree increment. Lower left corner coordinates "
            "in tile file names will be rounded to nearest integer degree."
        )
    deg_increment = 360 / num_cols

    if tile_col_row is not None:
        col, row = tile_col_row
        if col not in cols or row not in rows:
            raise ValueError(
                f"Specified tile column ({col}) or row ({row}) falls outside of "
                f"tile grid. Valid columns = 0 to {cols[-1]}, valid rows = "
                f"0 to {rows[-1]}."
            )
        cols = [col]
        rows = [row]

    windows = []
    for c in cols:
        for r in rows:
            window = {}
            window["window"] = Window(c * tile_dim, r * tile_dim, tile_dim, tile_dim)

            bottom = round(90 - (r + 1) * deg_increment)
            bottom_text = f"{'S' if bottom < 0 else 'N'}{abs(bottom):02d}"
            left = round((c * deg_increment) - 180)
            left_text = f"{'W' if left < 0 else 'E'}{abs(left):03d}"
            window["tile"] = f"{bottom_text}{left_text}"

            windows.append(window)

    return windows


def _get_colormap() -> Dict[str, Tuple[int, ...]]:
    colors: Dict[str, Tuple[int, ...]] = {}
    for row in classes.TABLE:
        colors[row[0]] = tuple([*row[1], 255])
    return colors


def create_cog_asset(
    key: str,
    cog_href: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Creates a basic COG asset dict with shared core properties and optionally an
    href. An href should be given for normal assets, but can be None for Item
    Asset Definitions.

    Args:
        key (str):
        cog_href (str): The URL to the asset

    Returns:
        Dict: Basic Asset object
    """
    asset: Dict[str, Any] = constants.COG_ASSETS[key].copy()
    asset["type"] = constants.COG_MEDIA_TYPE
    if cog_href:
        asset["href"] = make_absolute_href(cog_href)
    if key in constants.TABLES:
        table = constants.TABLES[key]
        asset["classification:classes"] = classes.to_stac(table)

    nodata = asset.pop("nodata", None)
    data_type = asset.pop("data_type")
    band = {
        "spatial_resolution": constants.RESOLUTION,
        "sampling": constants.SAMPLING,
        "data_type": data_type,
    }
    if nodata is not None:
        band["nodata"] = nodata

    asset["raster:bands"] = [band]

    return asset


@dataclass(frozen=True)
class COGMetadata:
    id: str
    title: str
    geometry: Dict[str, Any]
    bbox: List[float]
    start_datetime: str
    end_datetime: str
    version: str
    tile: str
    epsg: int
    proj_shape: List[int]
    proj_transform: List[float]

    @classmethod
    def from_cog(
        cls, href: str, read_href_modifier: Optional[ReadHrefModifier]
    ) -> "COGMetadata":
        if read_href_modifier:
            modified_href = read_href_modifier(href)
        else:
            modified_href = href
        with rasterio.open(modified_href) as dataset:
            bbox = dataset.bounds
            geometry = mapping(box(*bbox))
            shape = dataset.shape
            transform = list(dataset.transform)[0:6]
            epsg = dataset.crs.to_epsg()

        fileparts = Path(href).stem.split("-")
        id = "-".join(fileparts[:-1])
        start_datetime = f"{fileparts[-4]}-01-01T00:00:00Z"
        end_datetime = f"{fileparts[-4]}-12-31T23:59:59Z"
        version = fileparts[-3]
        tile = fileparts[-2]
        title = f"ESA CCI Land Cover Map for Year {fileparts[-4]}, Tile {tile}"

        return COGMetadata(
            id=id,
            title=title,
            geometry=geometry,
            bbox=list(bbox),
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            version=version,
            tile=tile,
            epsg=epsg,
            proj_shape=shape,
            proj_transform=transform,
        )
