from typing import Any, Dict

from stactools.testing.test_data import TestData

files = [
    "C3S-LC-L4-LCCS-Map-300m-P1Y-2018-v2.1.1.nc",
    "ESACCI-LC-L4-LCCS-Map-300m-P1Y-2008-v2.0.7cds.nc",
]

url_base = "https://ai4epublictestdata.blob.core.windows.net/stactools/esa-cci-lc"

external_data: Dict[str, Dict[str, Any]] = dict()
for file in files:
    external_data[file] = {"url": f"{url_base}/{file}"}

test_data = TestData(__file__, external_data=external_data)
