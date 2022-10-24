from typing import Any, Dict, List, Optional

# import numpy as np
from netCDF4 import Dataset, Variable
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
        stac_dim = {"type": dim.name}
        if dim.name in dataset.variables:
            # assume that the index variable has the same name as the dimension
            index_var = dataset.variables[dim.name]
            attrs = index_var.ncattrs()
            if "valid_min" in attrs and "valid_max" in attrs:
                min = index_var.getncattr("valid_min")
                max = index_var.getncattr("valid_max")
                stac_dim["extent"] = [min, max]
            else:
                stac_dim["values"] = index_var[...].tolist()
        else:
            stac_dim["values"] = list(range(0, dim.size))

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

        if is_data_variable(var):
            type = VariableType.DATA
        else:
            type = VariableType.AUXILIARY

        stac_var = {"dimensions": var.dimensions, "type": type}
        if "long_name" in attrs:
            stac_var["description"] = var.getncattr("long_name")

        if "units" in attrs:
            stac_var["unit"] = var.getncattr("units")

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


def is_data_variable(var: Variable) -> bool:
    """
    Checks whether a variable contains "data" or "metadata"

    Args:
        dataset (Variable): A netCDF4 Variable

    Returns:
        bool: True for data, False for metadata
    """
    # if "lat" in var.dimensions and "lon" in var.dimensions and "time" in var.dimensions:
    if var.name in constants.DATA_VARIABLES:
        return True
    else:
        return False


def parse_transform(dataset: Dataset) -> Optional[List[float]]:
    """
    Gets the geotransform from the netcdf file and converts it into the
    format required for STAC (proj:transform).

    Args:
        dataset (Dataset): A netCDF4 Variable

    Returns:
        Optional[List[float]]: List of 6 numbers, or None if no geotransform is available
    """
    crs_var = dataset.variables["crs"]
    if "i2m" in crs_var.ncattrs():
        i2m = crs_var.getncattr("i2m")
        values = i2m.split(",")
        return [
            float(values[4]),
            float(values[0]),
            float(values[1]),
            float(values[5]),
            float(values[2]),
            float(values[3]),
        ]
    else:
        return None
