from pystac import Link, Provider, ProviderRole

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
        description="Provides source data, e.g. PROBA-V.",
        url="https://vito.be",
    ),
    Provider(
        name="ESA",
        roles=[ProviderRole.PRODUCER, ProviderRole.LICENSOR],
        description="The ESA Climate Change Initiative (CCI) lets produce the dataset.",
        url="https://esa.int",
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

# Extensions
PROCESSING_EXTENSION = "https://stac-extensions.github.io/processing/v1.1.0/schema.json"
DATACUBE_EXTENSION = "https://stac-extensions.github.io/datacube/v2.1.0/schema.json"

# Scientific
DOI = "10.24381/cds.006f2c9a"

# Assets
COG_TITLE = "Processed Cloud-Optimized GeoTIFF file"
COG_KEY = "cog"
COG_MEDIA_TYPE = "image/tiff; application=geotiff; profile=cloud-optimized"
COG_ROLES = ["data", "cloud-optimized"]

NETCDF_TITLE = "Original netCDF 4 file"
NETCDF_MEDIA_TYPE = "application/netcdf"
NETCDF_ROLES = ["data", "source"]
NETCDF_KEY = "netcdf"

IGNORED_UNITS = [""]
