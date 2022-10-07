#!/usr/bin/env python3

import sys

import rasterio.shutil
import xarray
from rasterio import Affine, MemoryFile

filename = sys.argv[1]

with xarray.open_dataset(filename) as dataset:
    variable = "lccs_class"
    profile = {
        "crs": "EPSG:4326",
        "width": 129600,
        "height": 64800,
        "dtype": "uint8",
        "nodata": 0,
        "count": 1,
        "transform": Affine(
            0.002777777777777778,
            0.0,
            -180.0,
            0.0,
            -0.0027777777777777783,
            90.00000000000001,
        ),
        "driver": "GTiff",
    }
    print("Squeezing values")
    values = dataset[variable].values.squeeze()
    with MemoryFile() as memory_file:
        with memory_file.open(**profile) as open_memory_file:
            print("Writing memory file")
            open_memory_file.write(values, 1)
            print("Writing COG")
            rasterio.shutil.copy(
                open_memory_file,
                "cog.tif",
                **{"compress": "deflate", "blocksize": 512, "driver": "COG"},
            )
