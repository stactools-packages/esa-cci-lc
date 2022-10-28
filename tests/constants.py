SRC_FOLDER = "./tests/data-files/external/"
TRUTH_FOLDER = "./tests/data-files/"
TEST_FILES = [
    "C3S-LC-L4-LCCS-Map-300m-P1Y-2020-v2.1.1",
    "C3S-LC-L4-LCCS-Map-300m-P1Y-2016-v2.1.1",
    "ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7cds",
    "ESACCI-LC-L4-LCCS-Map-300m-P1Y-1992-v2.0.7cds",
]

# Collection
TITLE = "ESA Climate Change Initiative Land Cover"
START_DATETIME = "1992-01-01T00:00:00Z"
END_DATETIME = "2020-12-31T23:59:59Z"
BBOX = [-180.0, -90.0, 180.0, 90.0]

# Item
GEOMETRY = {
    "type": "Polygon",
    "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]],
}

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

NETCDF_TITLE = "Original netCDF 4 file"
NETCDF_MEDIA_TYPE = "application/netcdf"
NETCDF_ROLES = ["data", "quality", "source"]
NETCDF_KEY = "netcdf"

DATA_VARIABLES = [
    "change_count",
    "current_pixel_state",
    "lccs_class",
    "observation_count",
    "processed_flag",
]

TABLES = [
    "current_pixel_state",
    "processed_flag",
    "lccs_class",
]
