import logging
from datetime import datetime, timezone
from typing import Optional

from dateutil.parser import isoparse
from pystac import (
    Asset,
    CatalogType,
    Collection,
    Extent,
    Item,
    MediaType,
    SpatialExtent,
    Summaries,
    TemporalExtent,
)
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.scientific import ScientificExtension

from . import cog, constants, netcdf

logger = logging.getLogger(__name__)


def create_collection(
    id: str = "esa-cci-lc",
    thumbnail: str = "",
    nocog: bool = False,
    nonetcdf: bool = False,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> Collection:
    """Create a STAC Collection for NOAA MRMS QPE sub-products.

    Args:
        id (str): A custom collection ID, defaults to 'esa-cci-lc'
        thumbnail (str): URL for the PNG or JPEG collection thumbnail asset (none if empty)
        nocog (bool): If set to True, the collections does not include the
            COG-related metadata
        nonetcdf (bool): If set to True, the collections does not include the
            netCDF-related metadata
        start_time (str): The start timestamp for the temporal extent, default to now.
            Timestamps consist of a date and time in UTC and must follow RFC 3339, section 5.6.
        end_time (str): The end timestamp for the temporal extent, default to now.
            Timestamps consist of a date and time in UTC and must follow RFC 3339, section 5.6.
            To specify an open-ended temporal extent, set this option to 'open-ended'.

    Returns:
        Collection: STAC Collection object
    """
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

    keywords = [
        "ESA",
        "Climate Change Initiative",
        "CCI",
        "Land Cover",
        "LC",
    ]
    if not nonetcdf:
        keywords.append("netCDF")
    if not nocog:
        keywords.append("COG")

    summaries = Summaries(
        {
            "esa-cci-lc:example": [1, 2, 3],  # todo
        }
    )

    collection = Collection(
        stac_extensions=[
            #           constants.PROCESSING_EXTENSION,
        ],
        id=id,
        title=constants.TITLE,
        description=constants.DESCRIPTION,
        keywords=keywords,
        license="proprietary",
        providers=constants.PROVIDERS,
        extent=extent,
        summaries=summaries,
        catalog_type=CatalogType.RELATIVE_PUBLISHED,
    )

    collection.add_link(constants.LINK_LICENSE_ESA)
    collection.add_link(constants.LINK_LICENSE_COPERNICUS)
    collection.add_link(constants.LINK_LICENSE_VITO)
    collection.add_link(constants.LINK_LANDING_PAGE)
    collection.add_link(constants.LINK_USER_GUIDE_V21)
    collection.add_link(constants.LINK_USER_GUIDE_V20)

    sci_ext = ScientificExtension.ext(collection, add_if_missing=True)
    sci_ext.doi = constants.DOI

    if len(thumbnail) > 0:
        if thumbnail.endswith(".png"):
            media_type = MediaType.PNG
        else:
            media_type = MediaType.JPEG

        collection.add_asset(
            "thumbnail",
            Asset(
                href=thumbnail,
                title="Preview",
                roles=["thumbnail"],
                media_type=media_type,
            ),
        )

    item_assets = {}

    if not nocog:
        item_assets[constants.COG_KEY] = AssetDefinition(
            cog.create_asset_metadata(constants.COG_TITLE)
        )

    if not nonetcdf:
        asset = netcdf.create_asset()
        item_assets[constants.NETCDF_KEY] = AssetDefinition(asset)

    item_assets_attrs = ItemAssetsExtension.ext(collection, add_if_missing=True)
    item_assets_attrs.item_assets = item_assets

    return collection


def create_item(
    asset_href: str,
    collection: Optional[Collection] = None,
    nocog: bool = False,
    nonetcdf: bool = False,
) -> Item:
    """Create a STAC Item

    This function should include logic to extract all relevant metadata from an
    asset, metadata asset, and/or a constants.py file.

    See `Item<https://pystac.readthedocs.io/en/latest/api.html#item>`_.

    Args:
        asset_href (str): The HREF pointing to an asset associated with the item
        collection (pystac.Collection): HREF to an existing collection
        nocog (bool): If set to True, no COG file is generated for the Item
        nonetcdf (bool): If set to True, the netCDF file is not added to the Item

    Returns:
        Item: STAC Item object
    """

    properties = {
        "title": "A dummy STAC Item",
        "description": "Used for demonstration purposes",
    }

    demo_geom = {
        "type": "Polygon",
        "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]],
    }

    # Time must be in UTC
    demo_time = datetime.now(tz=timezone.utc)

    item = Item(
        id="my-item-id",
        properties=properties,
        geometry=demo_geom,
        bbox=[-180, 90, 180, -90],
        datetime=demo_time,
        stac_extensions=[],
        collection=collection,
    )

    # It is a good idea to include proj attributes to optimize for libs like stac-vrt
    proj_attrs = ProjectionExtension.ext(item, add_if_missing=True)
    proj_attrs.epsg = 4326
    proj_attrs.bbox = [-180, 90, 180, -90]
    proj_attrs.shape = [1, 1]  # Raster shape
    proj_attrs.transform = [-180, 360, 0, 90, 0, 180]  # Raster GeoTransform

    # Add a assets to the item
    if not nocog:
        item.add_asset(
            constants.COG_KEY,
            Asset(
                href=asset_href,
                media_type=constants.COG_MEDIA_TYPE,
                roles=constants.COG_ROLES,
                title=constants.COG_TITLE,
            ),
        )

    if not nonetcdf:
        item.add_asset(
            constants.NETCDF_KEY,
            Asset(
                href=asset_href,
                media_type=constants.NETCDF_MEDIA_TYPE,
                roles=constants.NETCDF_ROLES,
                title=constants.NETCDF_TITLE,
            ),
        )

    return item
