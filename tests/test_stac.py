import unittest

# from datetime import datetime, timezone
from typing import Any, Dict, List

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

                self.assertEqual(collection_dict["sci:doi"], constants.DOI)

                self.assertTrue("summaries" in collection_dict)
                summaries = collection_dict["summaries"]
                self.assertEqual(summaries["gsd"], [constants.GSD])
                self.assertEqual(summaries["esa_cci_lc:version"], constants.VERSIONS)
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
                        if key in constants.TABLES:
                            self.assertIn("classification:classes", asset)
                        else:
                            self.assertNotIn("classification:classes", asset)

                # Check netCDF asset
                if nonetcdf:
                    self.assertFalse("netcdf" in assets)
                else:
                    self.assertTrue("netcdf" in assets)
                    asset = assets["netcdf"]
                    self.assertIn("title", asset)
                    self.assertNotIn("href", asset)
                    self.assertEqual(asset["type"], constants.NETCDF_MEDIA_TYPE)
                    self.assertIn("source", asset["roles"])
                    self.assertNotIn("classification:classes", asset)

    def test_create_item(self) -> None:
        self.assertTrue(True)
        # Write tests for each for the creation of STAC Items
        # Create the STAC Item...
        # item = stac.create_item("/path/to/asset.tif")

        # Check that it has some required attributes
        # assert item.id == "my-item-id"
        # self.assertEqual(item.other_attr...

        # Validate
        # item.validate()
