import logging
import re
from datetime import datetime, timezone
from typing import Dict, Optional

from dateutil.parser import isoparse
from netCDF4 import Dataset
from pystac import (
    Asset,
    CatalogType,
    Collection,
    CommonMetadata,
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
        "Classification",
    ]
    if not nonetcdf:
        keywords.append("netCDF")
    if not nocog:
        keywords.append("COG")

    summaries = Summaries(
        {"gsd": [constants.GSD], "esa_cci_lc:version": constants.VERSIONS}
    )

    collection = Collection(
        stac_extensions=[
            constants.ESA_CCI_LC_EXTENSION,
            # constants.CLASSIFICATION_EXTENSION,
            # constants.DATACUBE_EXTENSION,
            # constants.PROCESSING_EXTENSION,
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
        asset = cog.create_asset()
        item_assets[constants.COG_KEY] = AssetDefinition(asset)

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

    with Dataset(asset_href, "r", format="NETCDF4") as dataset:
        id = dataset.id

        if dataset.product_version not in constants.VERSIONS:
            versions = ",".join(constants.VERSIONS)
            raise Exception(
                f"Given product version ({dataset.product_version}) is not supported. "
                f"Supports: {versions}"
            )

        # Times must be in UTC
        start = dataset.time_coverage_start
        end = dataset.time_coverage_end
        if start[0:4] != end[0:4]:
            raise Exception(
                "Expected a yearly land cover, but got different start and end years"
            )
        year = start[0:4]
        start_datetime = isoparse(f"{start[0:4]}-{start[4:6]}-{start[6:8]}T00:00:00Z")
        end_datetime = isoparse(f"{end[0:4]}-{end[4:6]}-{end[6:8]}T23:59:59Z")

        properties = {
            "esa_cci_lc:version": dataset.product_version,
        }

        item = Item(
            stac_extensions=[
                constants.ESA_CCI_LC_EXTENSION,
                # constants.CLASSIFICATION_EXTENSION,
            ],
            id=id,
            properties=properties,
            geometry=constants.GEOMETRY,
            bbox=constants.BBOX,
            datetime=center_datetime(start_datetime, end_datetime),
            collection=collection,
        )

        common_item = CommonMetadata(item)
        common_item.title = f"Land Cover Map of {year}"
        common_item.gsd = constants.GSD
        common_item.start_datetime = start_datetime
        common_item.end_datetime = end_datetime

        # It is a good idea to include proj attributes to optimize for libs like stac-vrt
        proj_attrs = ProjectionExtension.ext(item, add_if_missing=True)
        proj_attrs.epsg = constants.EPSG_CODE
        # proj_attrs.shape = [1, 1]  # Raster shape
        # proj_attrs.transform = [-180, 360, 0, 90, 0, 180]  # Raster GeoTransform

        software = parse_software_history(dataset.history)
        if len(software) > 0 or len(dataset.source) > 0:
            item.stac_extensions.append(constants.PROCESSING_EXTENSION)
            if len(software) > 0:
                item.properties["processing:software"] = software
            if len(dataset.source) > 0:
                item.properties[
                    "processing:lineage"
                ] = f"Produced based on the following data sources: {dataset.source}"

        # Add a assets to the item
        if not nocog:
            asset_dict = cog.create_asset("todo")  # todo
            asset = Asset.from_dict(asset_dict)
            common_asset = CommonMetadata(asset)
            common_asset.created = datetime.now(tz=timezone.utc)
            item.add_asset(constants.COG_KEY, asset)

        if not nonetcdf:
            # todo: replace with DataCube extension from PySTAC #16
            item.stac_extensions.append(constants.DATACUBE_EXTENSION)
            asset_dict = netcdf.create_asset(asset_href)
            asset_dict["cube:dimensions"] = netcdf.to_cube_dimensions(dataset)
            asset_dict["cube:variables"] = netcdf.to_cube_variables(dataset)
            asset = Asset.from_dict(asset_dict)
            common_asset = CommonMetadata(asset)
            common_asset.created = isoparse(dataset.creation_date)
            item.add_asset(constants.NETCDF_KEY, asset)

        return item


def parse_software_history(history: str) -> Dict[str, str]:
    """
    Parses a comma delimited string with software and version number into
    a dict compliant to `processing:software`.

    Args:
        history (str): string with software and version numbers

    Returns:
        Dict[str, str]
    """
    software: Dict[str, str] = {}
    tools = re.findall(r"([\w-]+)-(\d+[.,]\d+)", history)
    for tool in tools:
        name = tool[0].strip()
        version = tool[1].strip()
        if name in software:
            # solve conflicts
            software[f"{name}(1)"] = software[name]
            software[f"{name}(2)"] = version
            del software[name]
        else:
            software[name] = version

    return software


def center_datetime(start: datetime, end: datetime) -> datetime:
    """
    Takes the start and end datetime and computes the central datetime.

    Args:
        start (datetime): ISO 8601 compliant date-time
        end (datetime): ISO 8601 compliant date-time

    Returns:
        datetime: ISO 8601 compliant date-time
    """
    return start + (end - start) / 2
