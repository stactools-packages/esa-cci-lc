from typing import Any, Dict

from pystac import Link, Provider, ProviderRole

from . import classes

# Collections
COG_COLLECTION_TITLE = "ESA Climate Change Initiative Land Cover Maps - COG Tiles"
COG_COLLECTION_DESCRIPTION = (
    "The ESA Climate Change Initiative (CCI) dataset provides global maps "
    "describing land surface classes, which have been defined using the "
    "United Nations Food and Agriculture Organization's (UN FAO) Land Cover "
    "Classification System (LCCS). In addition to the land cover (LC) maps, "
    "four quality flags are produced to document the reliability of the "
    "classification and change detection. This Collection describes tiled Cloud "
    "Optimized GeoTIFFs (COGs) that were generated from the source NetCDF data."
)
NETCDF_COLLECTION_TITLE = "ESA Climate Change Initiative Land Cover Maps - NetCDF Data"
NETCDF_COLLECTION_DESCRIPTION = (
    "The ESA Climate Change Initiative (CCI) dataset provides global maps "
    "describing land surface classes, which have been defined using the "
    "United Nations Food and Agriculture Organization's (UN FAO) Land Cover "
    "Classification System (LCCS). In addition to the land cover (LC) maps, "
    "four quality flags are produced to document the reliability of the "
    "classification and change detection. This Collection describes the source "
    "NetCDF data."
)
START_DATETIME = "1992-01-01T00:00:00Z"
END_DATETIME = "2020-12-31T23:59:59Z"
BBOX = [-180.0, -90.0, 180.0, 90.0]
KEYWORDS = ["Land Cover", "ESA", "CCI", "Global"]

PROVIDERS = [
    Provider(
        name="VITO",
        roles=[ProviderRole.LICENSOR],
        description="Provides the PROBA-V source data (for v2.0).",
        url="https://vito.be",
    ),
    Provider(
        name="UCLouvain",
        roles=[ProviderRole.PRODUCER],
        description="UCLouvain produces the dataset (v2.1) for the ESA Climate Change Initiative.",
        url="https://uclouvain.be",
    ),
    Provider(
        name="Brockmann Consult",
        roles=[ProviderRole.PROCESSOR],
        description=(
            "Brockmann Consult is responsible for the required pre-processing "
            "and the distribution of the dataset (v2.1)."
        ),
        url="https://brockmann-consult.de",
    ),
    Provider(
        name="ESA Climate Change Initiative",
        roles=[ProviderRole.LICENSOR],
        description="The ESA Climate Change Initiative (CCI) is leading the product creation.",
        url="http://esa-landcover-cci.org",
    ),
    Provider(
        name="Copernicus",
        roles=[ProviderRole.HOST, ProviderRole.LICENSOR],
        description="Hosts the data on the Copernicus Climate Data Store (CDS).",
        url="https://copernicus.eu",
    ),
]

LINK_LICENSE_ESA = Link(
    target="https://cds.climate.copernicus.eu/api/v2/terms/static/satellite-land-cover.pdf",
    media_type="text/html",
    title="ESA CCI license",
    rel="license",
)
LINK_LICENSE_COPERNICUS = Link(
    target="https://cds.climate.copernicus.eu/api/v2/terms/static/licence-to-use-copernicus-products.pdf",  # noqa: E501
    media_type="text/html",
    title="COPERNICUS license",
    rel="license",
)
LINK_LICENSE_VITO = Link(
    target="https://cds.climate.copernicus.eu/api/v2/terms/static/vito-proba-v.pdf",
    media_type="text/html",
    title="VITO License",
    rel="license",
)
LINK_LANDING_PAGE = Link(
    target="https://cds.climate.copernicus.eu/cdsapp#!/dataset/satellite-land-cover",
    media_type="text/html",
    title="Product Landing Page",
    rel="about",
)
LINK_USER_GUIDE_V20 = Link(
    target="https://datastore.copernicus-climate.eu/documents/satellite-land-cover/D3.3.11-v1.0_PUGS_CDR_LC-CCI_v2.0.7cds_Products_v1.0.1_APPROVED_Ver1.pdf",  # noqa: E501
    media_type="application/pdf",
    title="Product user guide for version 2.0",
    rel="about",
)
LINK_USER_GUIDE_V21 = Link(
    target="https://datastore.copernicus-climate.eu/documents/satellite-land-cover/D5.3.1_PUGS_ICDR_LC_v2.1.x_PRODUCTS_v1.1.pdf",  # noqa: E501
    media_type="application/pdf",
    title="Product user guide for version 2.1",
    rel="about",
)

# Items
GEOMETRY = {
    "type": "Polygon",
    "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]],
}

# Extensions
CLASSIFICATION_EXTENSION = (
    "https://stac-extensions.github.io/classification/v1.1.0/schema.json"
)
DATACUBE_EXTENSION = "https://stac-extensions.github.io/datacube/v2.1.0/schema.json"
PROCESSING_EXTENSION = "https://stac-extensions.github.io/processing/v1.1.0/schema.json"
# For summaries, until supported: https://github.com/stac-utils/pystac/issues/890
PROJECTION_EXTENSION = "https://stac-extensions.github.io/projection/v1.0.0/schema.json"
# For item asset definitions, until supported: https://github.com/stac-utils/pystac/issues/890
RASTER_EXTENSION = "https://stac-extensions.github.io/raster/v1.1.0/schema.json"
VERSION_EXTENSION = "https://stac-extensions.github.io/version/v1.1.0/schema.json"

# Common
V1 = "2.0.7cds"
V2 = "2.1.1"
VERSIONS = [V1, V2]

# Raster
RESOLUTION = 300
SAMPLING = "area"

# Projection
EPSG_CODE = 4326

# Scientific
DOI = "10.24381/cds.006f2c9a"

# Assets
COG_MEDIA_TYPE = "image/tiff; application=geotiff; profile=cloud-optimized"
COG_ROLES_DATA = ["data", "cloud-optimized"]
COG_ROLES_QUALITY = ["quality", "cloud-optimized"]
COG_TILE_DIM = 16200
COG_ASSETS: Dict[str, Dict[str, Any]] = {
    "change_count": {
        "title": "Number of Class Changes",
        "description": (
            "Number of years where land cover class changes have occurred, since 1992. "
            "0 for stable, greater than 0 for changes."
        ),
        "roles": COG_ROLES_QUALITY,
        "data_type": "uint8",
    },
    "current_pixel_state": {
        "title": "Land Cover Pixel Type Mask",
        "description": (
            "Pixel identification from satellite surface reflectance observations, "
            "mainly distinguishing between land, water, and snow/ice."
        ),
        "roles": COG_ROLES_QUALITY,
        "data_type": "uint8",
        "nodata": 255,
    },
    "lccs_class": {
        "title": "Land Cover Class Defined in the Land Cover Classification System",
        "description": (
            "Land cover class per pixel, defined using the Land Cover Classification System "
            "developed by the United Nations Food and Agriculture Organization."
        ),
        "roles": COG_ROLES_DATA,
        "data_type": "uint8",
        "nodata": 0,
    },
    "observation_count": {
        "title": "Number of Valid Observations",
        "description": (
            "Number of valid satellite observations that have contributed to each "
            "pixel's classification."
        ),
        "roles": COG_ROLES_QUALITY,
        "data_type": "uint16",
    },
    "processed_flag": {
        "title": "Land Cover Map Processed Area Flag",
        "description": "Flag to mark areas that could not be classified.",
        "roles": COG_ROLES_QUALITY,
        "data_type": "uint8",
        "nodata": 255,
    },
}

NETCDF_ASSET_TITLE = "Original NetCDF 4 file"
NETCDF_MEDIA_TYPE = "application/netcdf"
NETCDF_ROLES = ["data", "quality", "source"]
NETCDF_KEY = "netcdf"
NETCDF_DATA_SHAPE = [64800, 129600]

TABLES = {
    "current_pixel_state": classes.CURRENT_PIXEL_STATE_TABLE,
    "processed_flag": classes.PROCESSED_FLAG_TABLE,
    "lccs_class": classes.TABLE,
}
DATA_VARIABLES = [
    "change_count",
    "current_pixel_state",
    "lccs_class",
    "observation_count",
    "processed_flag",
]
