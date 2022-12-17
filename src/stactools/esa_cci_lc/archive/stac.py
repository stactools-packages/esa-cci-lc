import logging
import os
import re
from typing import Any, Dict, List, Optional

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
from stactools.core.io import ReadHrefModifier
from stactools.esa_cci_lc.tiler import make_cog_tiles

from . import classes, cog, constants, netcdf

logger = logging.getLogger(__name__)


def create_collection(
    id: str = "esa-cci-lc",
    thumbnail: str = "",
    nocog: bool = False,
    nonetcdf: bool = False,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> Collection:
    """Create a STAC Collection for ESA CCI data.

    Args:
        id (str): A custom collection ID, defaults to 'esa-cci-lc'
        thumbnail (str): URL for the PNG or JPEG collection thumbnail asset (none if empty)
        nocog (bool): If set to True, the collection does not include the
            COG-related metadata
        nonetcdf (bool): If set to True, the collection does not include the
            netCDF-related metadata
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

    classification = classes.to_stac()
    summaries = Summaries(
        {
            "classification:classes": classification,
            "proj:epsg": [constants.EPSG_CODE],
        },
        # Up the maxcount for the classes, otherwise the classes will be omitted from output
        maxcount=len(classification) + 1,
    )

    # todo: replace with Projection and raster extension from PySTAC
    # https://github.com/stac-utils/pystac/issues/890
    extensions = [
        constants.CLASSIFICATION_EXTENSION,
        constants.PROJECTION_EXTENSION,
    ]
    if not nocog:
        extensions.append(constants.RASTER_EXTENSION)

    collection = Collection(
        stac_extensions=extensions,
        id=id,
        title=constants.TITLE,
        description=constants.DESCRIPTION,
        keywords=keywords,
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
        for var in constants.DATA_VARIABLES:
            asset = cog.create_asset(var)
            item_assets[var] = AssetDefinition(asset)

    if not nonetcdf:
        asset = netcdf.create_asset()
        item_assets[constants.NETCDF_KEY] = AssetDefinition(asset)

    item_assets_attrs = ItemAssetsExtension.ext(collection, add_if_missing=True)
    item_assets_attrs.item_assets = item_assets

    return collection


def create_items(
    nc_path: str,
    cog_dir: str,
    *,
    cog_tile_dim: Optional[int] = constants.COG_TILE_DIM,
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
    item_cog_lists = make_cog_tiles(nc_path, cog_dir, cog_tile_dim)

    items = []
    for item_cog_list in item_cog_lists:
        item = create_item_from_asset_list(
            item_cog_list,
            nc_api_url
        )
        items.append(item)

    return items


def create_item(
    asset_href: str,
    collection: Optional[Collection] = None,
    nocog: bool = False,
    nonetcdf: bool = False,
    ovr_class_resampling: str = "mode",
) -> Item:
    """Create a STAC Item

    Args:
        asset_href (str): The HREF pointing to an asset associated with the item
        collection (pystac.Collection): HREF to an existing collection
        nocog (bool): If set to True, no COG file is generated for the Item
        nonetcdf (bool): If set to True, the netCDF file is not added to the Item
        ovr_class_resampling (str): Resampling method for the COG overviews of the classes.

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
        }
        if nocog:
            properties["classification:classes"] = classes.to_stac()

        extensions = [
            constants.CLASSIFICATION_EXTENSION,
        ]
        # todo: replace with raster extension from PySTAC
        # https://github.com/stac-utils/pystac/issues/890
        if not nocog:
            extensions.append(constants.RASTER_EXTENSION)

        item = Item(
            stac_extensions=extensions,
            id=id,
            properties=properties,
            geometry=constants.GEOMETRY,
            bbox=constants.BBOX,
            datetime=None,
            collection=collection,
        )

        common_item = CommonMetadata(item)
        common_item.title = f"Land Cover Map of {year}"
        # We can't add it here due to https://github.com/stac-utils/pystac/issues/905
        # common_item.start_datetime = start_datetime
        # common_item.end_datetime = end_datetime

        proj_attrs = ProjectionExtension.ext(item, add_if_missing=True)
        proj_attrs.epsg = constants.EPSG_CODE

        software = parse_software_history(dataset.history)
        if len(software) > 0 or len(dataset.source) > 0:
            item.stac_extensions.append(constants.PROCESSING_EXTENSION)
            if len(software) > 0:
                item.properties["processing:software"] = software
            if len(dataset.source) > 0:
                lineage = (
                    f"Produced based on the following data sources: {dataset.source}"
                )
                item.properties["processing:lineage"] = lineage

        # Add a assets to the item
        if not nocog:
            dest_folder = os.path.dirname(asset_href)
            for key, var in dataset.variables.items():
                if not netcdf.is_data_variable(var):
                    continue

                asset = cog.create_from_var(
                    asset_href, dest_folder, dataset, var, ovr_class_resampling
                )
                item.add_asset(key, asset)

        if not nonetcdf:
            asset_dict = netcdf.create_asset(asset_href)

            item.stac_extensions.append(constants.VERSION_EXTENSION)
            asset_dict["version"] = dataset.product_version

            # todo: replace with DataCube extension from PySTAC
            item.stac_extensions.append(constants.DATACUBE_EXTENSION)
            asset_dict["cube:dimensions"] = netcdf.to_cube_dimensions(dataset)
            asset_dict["cube:variables"] = netcdf.to_cube_variables(dataset)

            asset = Asset.from_dict(asset_dict)
            item.add_asset(constants.NETCDF_KEY, asset)

            common_asset = CommonMetadata(asset)
            common_asset.created = isoparse(dataset.creation_date)

            proj_asset_attrs = ProjectionExtension.ext(asset, add_if_missing=True)
            proj_asset_attrs.shape = [
                dataset.dimensions["lon"].size,
                dataset.dimensions["lat"].size,
            ]
            transform = netcdf.parse_transform(dataset)
            if transform is not None:
                proj_asset_attrs.transform = transform

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
