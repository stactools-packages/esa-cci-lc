from stactools.testing.test_data import TestData

external_data = {
    "dataset-satellite-land-cover-6a61fb83-4c35-4ea5-b50c-e43a310a473a.zip": {
        "url": (
            "https://ai4epublictestdata.blob.core.windows.net/"
            "stactools/esa-cci-lc/"
            "dataset-satellite-land-cover-6a61fb83-4c35-4ea5-b50c-e43a310a473a.zip"
        ),
        "compress": "zip",
    },
    "dataset-satellite-land-cover-fd650584-ea29-4ddc-919c-20f894c09d81.zip": {
        "url": (
            "https://ai4epublictestdata.blob.core.windows.net/"
            "stactools/esa-cci-lc/"
            "dataset-satellite-land-cover-fd650584-ea29-4ddc-919c-20f894c09d81.zip"
        ),
        "compress": "zip",
    },
}

test_data = TestData(__file__, external_data)
