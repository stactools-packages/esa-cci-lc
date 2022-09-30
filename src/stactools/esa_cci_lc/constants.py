from pystac import Link, Provider, ProviderRole

from . import classes

# Collection
TITLE = "ESA Climate Change Initiative Land Cover"
DESCRIPTION = (
    "This dataset provides global maps describing the land surface classes, "
    "which have been defined using the United Nations Food and Agriculture "
    "Organization's (UN FAO) Land Cover Classification System (LCCS). "
    "In addition to the land cover (LC) maps, four quality flags are produced "
    "to document the reliability of the classification and change detection. "
    "In order to ensure continuity, these land cover maps are consistent with "
    "the series of global annual LC maps from the 1990s to 2015 produced by "
    "the European Space Agency (ESA) Climate Change Initiative (CCI)."
)
START_DATETIME = "1992-01-01T00:00:00Z"
END_DATETIME = "2020-12-31T23:59:59Z"
BBOX = [-180.0, -90.0, 180.0, 90.0]

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

# Item
GEOMETRY = {
    "type": "Polygon",
    "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]],
}

# Extensions
ESA_CCI_LC_EXTENSION = "https://raw.githubusercontent.com/stactools-packages/esa-cci-lc/main/extension/schema.json"  # noqa: E501
CLASSIFICATION_EXTENSION = (
    "https://stac-extensions.github.io/classification/v1.0.0/schema.json"
)
DATACUBE_EXTENSION = "https://stac-extensions.github.io/datacube/v2.1.0/schema.json"
PROCESSING_EXTENSION = "https://stac-extensions.github.io/processing/v1.1.0/schema.json"
# For summaries, until supported: https://github.com/stac-utils/pystac/issues/890
PROJECTION_EXTENSION = "https://stac-extensions.github.io/projection/v1.0.0/schema.json"

# Common
GSD = 300
V1 = "2.0.7cds"
V2 = "2.1.1"
VERSIONS = [V1, V2]

# Projection
EPSG_CODE = 4326

# Scientific
DOI = "10.24381/cds.006f2c9a"

# Assets
COG_DESCRIPTIONS = {
    "change_count": (
        "Number of years where land cover class changes have occurred, since 1992. "
        "0 for stable, greater than 0 for changes."
    ),
    "current_pixel_state": (
        "Pixel identification from satellite surface reflectance observations, "
        "mainly distinguishing between land, water, and snow/ice."
    ),
    "lccs_class": (
        "Land cover class per pixel, defined using the Land Cover Classification System "
        "developed by the United Nations Food and Agriculture Organization."
    ),
    "observation_count": (
        "Number of valid satellite observations that have contributed to each "
        "pixel's classification.\n\n"
        "**Note:** The COG doesn't contain overviews!"
    ),
    "processed_flag": "Flag to mark areas that could not be classified.",
}

COG_MEDIA_TYPE = "image/tiff; application=geotiff; profile=cloud-optimized"
COG_ROLES_DATA = ["data", "cloud-optimized"]
COG_ROLES_QUALITY = ["quality", "cloud-optimized"]

NETCDF_TITLE = "Original netCDF 4 file"
NETCDF_MEDIA_TYPE = "application/netcdf"
NETCDF_ROLES = ["data", "quality", "source"]
NETCDF_KEY = "netcdf"

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
