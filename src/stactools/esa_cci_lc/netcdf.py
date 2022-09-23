from typing import Any, Dict, Optional

import numpy as np
from netCDF4 import Dataset
from pystac.extensions.datacube import VariableType

from . import constants


def to_cube_dimensions(dataset: Dataset) -> Dict[str, Any]:
    """
    Creates the cube:dimensions dict for a netCDF dataset.

    Args:
        dataset (Dataset): A netCDF4 Dataset

    Returns:
        dict: Dimensions Object
    """
    cube_dims = {}
    for key, dim in dataset.dimensions.items():
        stac_dim = {"type": dim.name, "extent": [None, None]}
        if not dim.isunlimited():
            dim_vars = [
                var for var in dataset.variables.values() if dim.name in var.dimensions
            ]
            if len(dim_vars) == 1:
                data = np.asarray(dim_vars).tolist()
                stac_dim["extent"] = data[0]
            elif len(dim_vars) > 1:
                flat = np.asarray(dim_vars).flatten().tolist()
                stac_dim["extent"] = [min(flat), max(flat)]

        cube_dims[dim.name] = stac_dim

    return cube_dims


def to_cube_variables(dataset: Dataset) -> Dict[str, Any]:
    """
    Creates the cube:variables dict for a netCDF dataset.

    Args:
        dataset (Dataset): A netCDF4 Dataset

    Returns:
        dict: Variables Object
    """
    cube_vars = {}
    for key, var in dataset.variables.items():
        attrs = var.ncattrs()

        if "standard_name" in attrs and len(var.dimensions) > 0:
            type = VariableType.DATA
        else:
            type = VariableType.AUXILIARY

        stac_var = {"dimensions": var.dimensions, "type": type}
        if "long_name" in attrs:
            stac_var["description"] = var.getncattr("long_name")

        if "units" in attrs:
            unit = var.getncattr("units")
            if unit == "percent":
                stac_var["unit"] = "%"
            elif unit not in constants.IGNORED_UNITS:
                stac_var["unit"] = unit

        # not defined in the datacube extension, but might be useful
        if "axis" in attrs:
            stac_var["axis"] = var.getncattr("axis")
        cube_vars[var.name] = stac_var

    return cube_vars


def create_asset(href: Optional[str] = None) -> Dict[str, Any]:
    """
    Creates a basic netCDF asset dict with shared properties (title, type, roles)
    and optionally an href. An href should be given for normal assets, but can
    be None for Item Asset Definitionss

    Args:
        href (str): The URL to an asset (optional)

    Returns:
        dict: Basic Asset object
    """
    asset: Dict[str, Any] = {
        "title": constants.NETCDF_TITLE,
        "type": constants.NETCDF_MEDIA_TYPE,
        "roles": constants.NETCDF_ROLES,
    }
    if href is not None:
        asset["href"] = href
    return asset
