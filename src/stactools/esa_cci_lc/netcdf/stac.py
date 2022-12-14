from datetime import datetime, timezone
from typing import Any, Dict, Optional

from dateutil.parser import isoparse
from netCDF4 import Dataset
from pystac import (
    Asset,
    CatalogType,
    Collection,
    CommonMetadata,
    Extent,
    Item,
    SpatialExtent,
    Summaries,
    TemporalExtent,
)
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.scientific import ScientificExtension

from .. import constants
from . import netcdf


def create_item(nc_href: str) -> Item:
    """Creates a STAC Item for a NetCDF file containing ESA CCI Land Cover data.

    Args:
        nc_href (str): HREF to a NetCDF file.

    Returns:
        Item: A STAC Item describing a NetCDF file.
    """

    with Dataset(nc_href, "r", format="NETCDF4") as dataset:
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
                "Expected a yearly land cover product, but got different start and end years"
            )
        year = start[0:4]

        # We can't use datetimes here due to https://github.com/stac-utils/pystac/issues/905
        # start_datetime = isoparse(f"{start[0:4]}-{start[4:6]}-{start[6:8]}T00:00:00Z")
        # end_datetime = isoparse(f"{end[0:4]}-{end[4:6]}-{end[6:8]}T23:59:59Z")
        start_datetime = f"{start[0:4]}-{start[4:6]}-{start[6:8]}T00:00:00Z"
        end_datetime = f"{end[0:4]}-{end[4:6]}-{end[6:8]}T23:59:59Z"

        properties: Dict[str, Any] = {
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "esa_cci_lc:version": dataset.product_version,
        }

        item = Item(
            id=id,
            properties=properties,
            geometry=constants.GEOMETRY,
            bbox=constants.BBOX,
            datetime=None,
        )

        common_item = CommonMetadata(item)
        common_item.created = datetime.now(tz=timezone.utc)
        common_item.title = f"ESA CCI Land Cover Map for {year}"
        # We can't add it here due to https://github.com/stac-utils/pystac/issues/905
        # common_item.start_datetime = start_datetime
        # common_item.end_datetime = end_datetime

        proj_attrs = ProjectionExtension.ext(item, add_if_missing=True)
        proj_attrs.epsg = constants.EPSG_CODE
        proj_attrs.shape = [
            dataset.dimensions["lon"].size,
            dataset.dimensions["lat"].size,
        ]
        transform = netcdf.parse_transform(dataset)
        if transform is not None:
            proj_attrs.transform = transform

        software = netcdf.parse_software_history(dataset.history)
        if len(software) > 0 or len(dataset.source) > 0:
            item.stac_extensions.append(constants.PROCESSING_EXTENSION)
            if len(software) > 0:
                item.properties["processing:software"] = software
            if len(dataset.source) > 0:
                lineage = (
                    f"Produced based on the following data sources: {dataset.source}"
                )
                item.properties["processing:lineage"] = lineage

        # Add asset to the item
        asset_dict = netcdf.create_asset(nc_href)

        # todo: replace with DataCube extension from PySTAC
        item.stac_extensions.append(constants.DATACUBE_EXTENSION)
        asset_dict["cube:dimensions"] = netcdf.to_cube_dimensions(dataset)
        asset_dict["cube:variables"] = netcdf.to_cube_variables(dataset)

        asset = Asset.from_dict(asset_dict)
        item.add_asset(constants.NETCDF_KEY, asset)

        common_asset = CommonMetadata(asset)
        common_asset.created = isoparse(dataset.creation_date)

        return item


def create_collection(
    id: str = "esa-cci-lc-netcdf",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> Collection:
    """Create a STAC Collection for ESA CCI source NetCDF data.

    Args:
        id (str): A custom collection ID, defaults to 'esa-cci-lc-netcdf'
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

    summaries = Summaries(
        {
            "esa_cci_lc:version": constants.VERSIONS,
        }
    )

    collection = Collection(
        id=id,
        title=constants.NETCDF_COLLECTION_TITLE,
        description=constants.NETCDF_COLLECTION_DESCRIPTION,
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
    asset = netcdf.create_asset()
    item_assets[constants.NETCDF_KEY] = AssetDefinition(asset)

    item_assets_attrs = ItemAssetsExtension.ext(collection, add_if_missing=True)
    item_assets_attrs.item_assets = item_assets

    return collection
