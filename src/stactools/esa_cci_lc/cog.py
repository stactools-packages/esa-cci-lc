import logging
from typing import Any, Dict, Optional

from . import constants

logger = logging.getLogger(__name__)


def create_asset_metadata(
    title: str,
    href: Optional[str] = None,
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
        "title": title,
        "type": constants.COG_MEDIA_TYPE,
        "roles": constants.COG_ROLES,
    }
    if href is not None:
        asset["href"] = href
    return asset
