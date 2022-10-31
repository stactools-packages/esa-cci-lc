import os.path
import shutil
import unittest

# from datetime import datetime, timezone
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional

import pytest
from pystac import Collection, Item

from stactools.esa_cci_lc import stac

from . import constants

THUMBNAIL = "https://example.com/thumb.png"

TEST_COLLECTIONS: List[Dict[str, Any]] = [
    {
        "id": "my-id",
        "thumbnail": THUMBNAIL,
        "start_time": "2017-01-01T00:00:00.000Z",
        "end_time": "2019-12-31T23:59:59.999Z",
    },
    {
        "nocog": True,
    },
    {
        "nonetcdf": True,
    },
]

TEST_ITEMS: List[Dict[str, Any]] = [
    {
        "id": constants.TEST_FILES[0]["id"],
        "year": constants.TEST_FILES[0]["year"],
        "collection": "./tests/data-files/collection.json",
    },
    {
        "id": constants.TEST_FILES[1]["id"],
        "year": constants.TEST_FILES[1]["year"],
        "collection": "./tests/data-files/collection.json",
    },
    {
        "id": constants.TEST_FILES[0]["id"],
        "year": constants.TEST_FILES[0]["year"],
        "nocog": True,
    },
    {
        "id": constants.TEST_FILES[0]["id"],
        "year": constants.TEST_FILES[0]["year"],
        "nonetcdf": True,
    },
]


class StacTest(unittest.TestCase):
    def test_create_collection(self) -> None:
        for test_data in TEST_COLLECTIONS:
            with self.subTest(test_data=test_data):
                id: str = test_data["id"] if "id" in test_data else "esa-cci-lc"
                nocog: bool = test_data["nocog"] if "nocog" in test_data else False
                nonetcdf: bool = (
                    test_data["nonetcdf"] if "nonetcdf" in test_data else False
                )

                collection = stac.create_collection(**test_data)
                collection.set_self_href("")
                collection.validate()
                collection_dict = collection.to_dict()

                self.assertEqual(collection.id, id)
                self.assertEqual(collection.title, constants.TITLE)

                self.assertEqual(collection_dict["sci:doi"], constants.DOI)

                self.assertTrue("summaries" in collection_dict)
                summaries = collection_dict["summaries"]
                self.assertIn("classification:classes", summaries)
                self.assertEqual(summaries["proj:epsg"], [constants.EPSG_CODE])

                self.assertTrue("item_assets" in collection_dict)
                assets: Dict[str, Dict[str, Any]] = collection_dict["item_assets"]

                asset_count = 6
                if nocog:
                    asset_count -= 5
                if nonetcdf:
                    asset_count -= 1
                self.assertEqual(len(assets), asset_count)

                # Check COG assets
                for key in constants.DATA_VARIABLES:
                    self.assertEqual(key in assets, not nocog)
                    if not nocog:
                        asset = assets[key]
                        self.assertNotIn("href", asset)
                        self.assertIn("description", asset)
                        self.assertEqual(asset["type"], constants.COG_MEDIA_TYPE)
                        self.assertIn("cloud-optimized", asset["roles"])
                        if key == "lccs_class":
                            self.assertIn("data", asset["roles"])
                        else:
                            self.assertIn("quality", asset["roles"])
                        self.assertEqual(
                            "classification:classes" in asset, key in constants.TABLES
                        )
                        self.assertIn("raster:bands", asset)
                        self.assertEqual(len(asset["raster:bands"]), 1)
                        band = asset["raster:bands"][0]
                        self.assertEqual(
                            band["spatial_resolution"], constants.RESOLUTION
                        )
                        self.assertEqual(band["sampling"], constants.SAMPLING)
                        self.assertEqual("nodata" in band, key == "lccs_class")

                # Check netCDF asset
                self.assertEqual(constants.NETCDF_KEY in assets, not nonetcdf)
                if not nonetcdf:
                    asset = assets[constants.NETCDF_KEY]
                    self.assertNotIn("href", asset)
                    self.assertEqual(asset["type"], constants.NETCDF_MEDIA_TYPE)
                    self.assertEqual(asset["title"], constants.NETCDF_TITLE)
                    self.assertEqual(asset["roles"], constants.NETCDF_ROLES)
                    self.assertNotIn("classification:classes", asset)

    @pytest.mark.usefixtures("pass_parameter")
    def test_create_item(self) -> None:
        for test_data in TEST_ITEMS:
            with self.subTest(test_data=test_data):
                id: str = test_data["id"]
                year: int = test_data["year"]
                test_data["nocog"] = (
                    False
                    if self.withcog  # type: ignore[attr-defined]
                    and ("nocog" not in test_data or test_data["nocog"] is False)
                    else True
                )
                nonetcdf: bool = (
                    test_data["nonetcdf"] if "nonetcdf" in test_data else False
                )

                collection: Optional[Collection] = None
                if "collection" in test_data:
                    collection = Collection.from_file(test_data["collection"])

                src_data_file = os.path.join(constants.SRC_FOLDER, f"{id}.nc")
                if not os.path.exists(src_data_file):
                    pytest.skip(
                        f"Data file {src_data_file} not available for test, skipping"
                    )
                    continue

                item: Optional[Item] = None
                with TemporaryDirectory() as tmp_dir:
                    dest_data_file = os.path.join(tmp_dir, f"{id}.nc")
                    shutil.copyfile(src_data_file, dest_data_file)

                    del test_data["id"]
                    del test_data["year"]
                    test_data["asset_href"] = dest_data_file
                    test_data["collection"] = collection

                    item = stac.create_item(**test_data)
                    item.validate()

                self.assertIsNotNone(item)
                self.assertEqual(item.id, id)
                self.assertEqual(item.bbox, constants.BBOX)
                self.assertEqual(item.geometry, constants.GEOMETRY)
                if collection is not None:
                    self.assertEqual(item.collection_id, collection.id)
                else:
                    self.assertIsNone(item.collection_id)

                self.assertIn("datetime", item.properties)
                self.assertEqual(
                    item.properties["start_datetime"], f"{year}-01-01T00:00:00Z"
                )
                self.assertEqual(
                    item.properties["end_datetime"], f"{year}-12-31T23:59:59Z"
                )
                self.assertEqual(item.properties["title"], f"Land Cover Map of {year}")
                self.assertEqual(
                    "classification:classes" in item.properties, test_data["nocog"]
                )
                self.assertEqual(item.properties["proj:epsg"], 4326)
                self.assertIn("processing:software", item.properties)
                self.assertIn("processing:lineage", item.properties)

                asset_count = 6
                if test_data["nocog"]:
                    asset_count -= 5
                if nonetcdf:
                    asset_count -= 1
                self.assertEqual(len(item.assets), asset_count)

                # Check COG assets
                for key in constants.DATA_VARIABLES:
                    self.assertEqual(key in item.assets, not test_data["nocog"])
                    if not test_data["nocog"]:
                        asset = item.assets[key].to_dict()
                        self.assertIn("href", asset)
                        self.assertEqual(asset["type"], constants.COG_MEDIA_TYPE)
                        self.assertIn("title", asset)
                        self.assertIn("description", asset)
                        self.assertIn("created", asset)
                        self.assertEqual(len(asset["proj:shape"]), 2)
                        self.assertEqual(len(asset["proj:transform"]), 6)
                        if key == "lccs_class":
                            self.assertIn("data", asset["roles"])
                        else:
                            self.assertIn("quality", asset["roles"])
                        self.assertIn("cloud-optimized", asset["roles"])
                        self.assertEqual(
                            "classification:classes" in asset, key in constants.TABLES
                        )
                        self.assertNotIn("cube:dimensions", asset)
                        self.assertNotIn("cube:variables", asset)

                # Check netCDF asset
                self.assertEqual(constants.NETCDF_KEY in item.assets, not nonetcdf)
                if not nonetcdf:
                    asset = item.assets[constants.NETCDF_KEY].to_dict()
                    self.assertIn("href", asset)
                    self.assertEqual(asset["type"], constants.NETCDF_MEDIA_TYPE)
                    self.assertEqual(asset["title"], constants.NETCDF_TITLE)
                    self.assertEqual(asset["roles"], constants.NETCDF_ROLES)
                    self.assertNotIn("description", asset)
                    self.assertIn("created", asset)
                    self.assertIn("cube:dimensions", asset)
                    self.assertIn("cube:variables", asset)
                    self.assertEqual(len(asset["proj:shape"]), 2)
                    self.assertEqual(len(asset["proj:transform"]), 6)
                    self.assertNotIn("classification:classes", asset)
                    self.assertIn("version", asset)
                    version_truth = constants.V1 if year < 2016 else constants.V2
                    self.assertEqual(asset["version"], version_truth)
                    self.assertTrue(id.endswith(asset["version"]))
