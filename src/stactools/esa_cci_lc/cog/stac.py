import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from dateutil.parser import isoparse
from pystac import (
    Asset,
    CatalogType,
    Collection,
    Extent,
    Item,
    Link,
    MediaType,
    SpatialExtent,
    Summaries,
    TemporalExtent,
)
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.scientific import ScientificExtension
from stactools.core.io import ReadHrefModifier

from .. import constants
from .cog import COGMetadata, create_cog_asset, make_cog_tiles

logger = logging.getLogger(__name__)


def create_items(
    nc_path: str,
    cog_dir: str,
    *,
    cog_tile_dim: int = constants.COG_TILE_DIM,
    tile_row_col: Optional[List[int]] = None,
    nc_api_url: Optional[str] = None,
) -> List[Item]:
    """Tiles NetCDF variables to COGs and creates an Item with COG assets for
    each tile.

    Args:
        nc_href (str): _description_
        cog_dir (str): _description_
        cog_tile_dim (Optional[int], optional): _description_. Defaults to constants.COG_TILE_DIM.
        nc_api_url (Optional[str], optional): _description_. Defaults to None.

    Returns:
        List[Item]: _description_
    """
    item_cog_lists = make_cog_tiles(nc_path, cog_dir, cog_tile_dim, tile_row_col)

    items = []
    for item_cog_list in item_cog_lists:
        item = create_item_from_asset_list(item_cog_list, nc_api_url)
        items.append(item)

    return items


def create_item_from_asset_list(
    cog_hrefs: List[str],
    nc_api_url: Optional[str] = None,
    read_href_modifier: Optional[ReadHrefModifier] = None,
) -> Item:
    """_summary_

    Args:
        cog_hrefs (str): _description_
        nc_api_url (Optional[str], optional): _description_. Defaults to None.
        read_href_modifier (Optional[ReadHrefModifier], optional): _description_. Defaults to None.

    Raises:
        ValueError: _description_

    Returns:
        Item: _description_
    """
    if len(cog_hrefs) != 5:
        raise ValueError(
            f"Incorrect number of asset HREFs supplied. Expected 5, supplied "
            f"{len(cog_hrefs)}."
        )

    metadata = COGMetadata.from_cog(cog_hrefs[0], read_href_modifier)

    item = Item(
        id=metadata.id,
        geometry=metadata.geometry,
        bbox=metadata.bbox,
        datetime=None,
        properties={
            "start_datetime": metadata.start_datetime,
            "end_datetime": metadata.end_datetime,
            "esa_cci_lc:version": metadata.version,
            "esa_cci_lc:tile": metadata.tile,
        },
    )
    item.common_metadata.created = datetime.now(tz=timezone.utc)
    item.common_metadata.title = metadata.title

    projection = ProjectionExtension.ext(item, add_if_missing=True)
    projection.epsg = metadata.epsg
    projection.shape = metadata.proj_shape
    projection.transform = metadata.proj_transform

    for cog_href in cog_hrefs:
        key = Path(cog_href).stem.split("-")[-1]
        item.add_asset(key, Asset.from_dict(create_cog_asset(key, cog_href)))

    if nc_api_url:
        nc_stac_item_id = "-".join(cog_hrefs[0].split("-")[:-1])
        item.add_link(
            Link(
                rel="derived_from",
                target=str(Path(nc_api_url) / nc_stac_item_id),
                media_type=MediaType.JSON,
                title="Source NetCDF",
            )
        )

    item.stac_extensions.append(constants.CLASSIFICATION_EXTENSION)
    item.stac_extensions.append(constants.RASTER_EXTENSION)

    item.validate()

    return item


def create_collection(
    id: str = "esa-cci-lc",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> Collection:
    """Create a STAC Collection for ESA CCI data.

    Args:
        id (str): A custom collection ID, defaults to 'esa-cci-lc'
        start_time (str): The start timestamp for the temporal extent, defaults
            to ``constants.START_DATETIME``.  Timestamps consist of a date and time
            in UTC and must follow RFC 3339, section 5.6.
        end_time (str): The end timestamp for the temporal extent, default to
            ``constants.END_DATETIME``.  Timestamps consist of a date and time in
            UTC and must follow RFC 3339, section 5.6.  To specify an open-ended
            temporal extent, set this option to 'open-ended'.

    Returns:
        Collection: STAC Collection object
    """
    # TODO: Add version in summaries

    # Time must be in UTC
    if start_time is None:
        start_datetime = isoparse(constants.START_DATETIME)
    else:
        start_datetime = isoparse(start_time)
    # Time must be in UTC
    if end_time is None:
        end_datetime = isoparse(constants.END_DATETIME)
    elif end_time == "open-ended":
        end_datetime = None
    else:
        end_datetime = isoparse(end_time)

    extent = Extent(
        SpatialExtent([constants.BBOX]),
        TemporalExtent([[start_datetime, end_datetime]]),
    )

    extensions = [
        constants.CLASSIFICATION_EXTENSION,
        constants.PROJECTION_EXTENSION,
        constants.RASTER_EXTENSION,
    ]

    summaries = Summaries({"esa_cci_lc:version": constants.VERSIONS})

    collection = Collection(
        stac_extensions=extensions,
        id=id,
        title=constants.TITLE,
        description=constants.DESCRIPTION,
        keywords=constants.KEYWORDS,
        license="proprietary",
        providers=constants.PROVIDERS,
        extent=extent,
        summaries=summaries,
        catalog_type=CatalogType.SELF_CONTAINED,
    )

    collection.add_link(constants.LINK_LICENSE_ESA)
    collection.add_link(constants.LINK_LICENSE_COPERNICUS)
    collection.add_link(constants.LINK_LICENSE_VITO)
    collection.add_link(constants.LINK_LANDING_PAGE)
    collection.add_link(constants.LINK_USER_GUIDE_V21)
    collection.add_link(constants.LINK_USER_GUIDE_V20)

    sci_ext = ScientificExtension.ext(collection, add_if_missing=True)
    sci_ext.doi = constants.DOI

    item_assets = {}
    for var in constants.DATA_VARIABLES:
        asset = create_cog_asset(var)
        item_assets[var] = AssetDefinition(asset)

    item_assets_attrs = ItemAssetsExtension.ext(collection, add_if_missing=True)
    item_assets_attrs.item_assets = item_assets

    return collection
