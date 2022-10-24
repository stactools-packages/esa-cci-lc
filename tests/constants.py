from stactools.testing.test_data import TestData
import os

EXTERNAL_DATA = {
    "C3S-LC-L4-LCCS-Map-300m-P1Y-2020-v2.1.1.nc": {
        "url": (
            "https://ai4epublictestdata.blob.core.windows.net/"
            "stactools/esa-cci-lc/"
            "dataset-satellite-land-cover-6a61fb83-4c35-4ea5-b50c-e43a310a473a.zip"
        ),
        "year": 2020
    },
    "ESACCI-LC-L4-LCCS-Map-300m-P1Y-1992-v2.0.7cds.nc": {
        "url": (
            "https://ai4epublictestdata.blob.core.windows.net/"
            "stactools/esa-cci-lc/"
            "dataset-satellite-land-cover-fd650584-ea29-4ddc-919c-20f894c09d81.zip"
        ),
        "year": 1992
    },
}

test_data = TestData(__file__, EXTERNAL_DATA)
TEST_FILES = []
for key in EXTERNAL_DATA:
    data = EXTERNAL_DATA[key]
    path = test_data.get_external_data(key)
    TEST_FILES.append({
        "id": os.path.splitext(path)[0],
        "path": path,
        "year": data["year"]
    })

SRC_FOLDER = "./tests/data-files/"

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
GSD = 300
V1 = "2.0.7cds"
V2 = "2.1.1"
VERSIONS = [V1, V2]

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
