import logging
from typing import Optional

import click
from click import Command, Group

from stactools.esa_cci_lc.netcdf import stac

logger = logging.getLogger(__name__)


def create_command(esaccilc: Group) -> Command:
    @esaccilc.group(
        "netcdf",
        short_help=("Commands for working with ESA CCI NetCDF files"),
    )
    def netcdf() -> None:
        pass

    @netcdf.command(
        "create-collection",
        short_help="Creates a STAC collection",
    )
    @click.argument("destination")
    @click.option(
        "--id",
        default="esa-cci-lc-netcdf",
        help="A custom collection ID, defaults to 'esa-cci-lc-netcdf'",
    )
    @click.option(
        "--start_time",
        default=None,
        help="The start timestamp for the temporal extent, defaults to '1992-01-01T00:00:00Z'. "
        "Timestamps consist of a date and time in UTC and must be follow RFC 3339, section 5.6.",
    )
    @click.option(
        "--end_time",
        default=None,
        help="The start timestamp for the temporal extent, defaults to '2020-12-31T23:59:59Z'. "
        "Timestamps consist of a date and time in UTC and must be follow RFC 3339, section 5.6. "
        "To specify an open-ended temporal extent, set this option to 'open-ended'.",
    )
    def create_collection_command(
        destination: str,
        id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> None:
        """Creates a STAC Collection

        \b
        Args:
            destination (str): An HREF for the Collection JSON
        """
        collection = stac.create_collection(
            id, start_time, end_time
        )
        collection.set_self_href(destination)
        collection.save_object()

        return None

    @netcdf.command("create-item", short_help="Creates a STAC item")
    @click.argument("source")
    @click.argument("destination")
    def create_item_command(
        source: str,
        destination: str,
    ) -> None:
        """Creates a STAC Item

        \b
        Args:
            source (str): HREF of the NetCDF file associated with the Item
            destination (str): An HREF for the STAC Item
        """
        item = stac.create_item(source)
        item.save_object(dest_href=destination)

        return None

    return netcdf
