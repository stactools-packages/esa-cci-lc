import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# import rioxarray  # noqa: F401
# import xarray
from netCDF4 import Variable
from pystac import Asset, CommonMetadata

from . import constants

logger = logging.getLogger(__name__)


def create_asset(
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
        "roles": constants.COG_ROLES,
    }
    if title is not None:
        asset["title"] = title
    if href is not None:
        asset["href"] = href
    return asset


# todo
def create_from_var(source: str, dest: str, var: Variable) -> Asset:
    dest_path = os.path.join(dest, f"{var.name}.tif")
    # xds = xarray.open_dataset(source, cache=False)
    # todo: this is incredibly slow
    # xds[var.name].rio.to_raster(dest_path, driver="COG", windowed=True)

    title = var.getncattr("long_name")
    if isinstance(title, str) and len(title) > 0:
        title = title[0].upper() + title[1:]
    else:
        title = None
    asset_dict = create_asset(dest_path, title)
    asset = Asset.from_dict(asset_dict)

    common_asset = CommonMetadata(asset)
    common_asset.created = datetime.now(tz=timezone.utc)

    return asset
