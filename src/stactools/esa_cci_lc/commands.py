import logging
from typing import Optional

import click
from click import Command, Group
from pystac import Collection

from stactools.esa_cci_lc import stac

logger = logging.getLogger(__name__)


def create_esaccilc_command(cli: Group) -> Command:
    """Creates the stactools-esa-cci-lc command line utility."""

    @cli.group(
        "esa-cci-lc",
        short_help=("Commands for working with stactools-esa-cci-lc"),
    )
    def esaccilc() -> None:
        pass

    @esaccilc.command(
        "create-collection",
        short_help="Creates a STAC collection",
    )
    @click.argument("destination")
    @click.option(
        "--id",
        default="esa-cci-lc",
        help="A custom collection ID, defaults to 'esa-cci-lc'",
    )
    @click.option(
        "--thumbnail",
        default="",
        help="URL for the PNG or JPEG collection thumbnail asset (none if empty)",
    )
    @click.option(
        "--nocog",
        default=False,
        help="Does not include the COG-related metadata in the collection if set to `TRUE`.",
    )
    @click.option(
        "--nonetcdf",
        default=False,
        help="Does not include the netCDF-related metadata in the collection if set to `TRUE`.",
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
        id: str = "",
        thumbnail: str = "",
        nocog: bool = False,
        nonetcdf: bool = False,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> None:
        """Creates a STAC Collection

        Args:
            destination (str): An HREF for the Collection JSON
        """
        collection = stac.create_collection(
            id, thumbnail, nocog, nonetcdf, start_time, end_time
        )
        collection.set_self_href(destination)
        collection.save_object()

        return None

    @esaccilc.command("create-item", short_help="Create a STAC item")
    @click.argument("source")
    @click.argument("destination")
    @click.option(
        "--collection",
        default="",
        help="An HREF to the Collection JSON. "
        "This adds the collection details to the item, but doesn't add the item to the collection.",
    )
    @click.option(
        "--nocog",
        default=False,
        help="Does not create COG files for the given netCDF file if set to `TRUE`.",
    )
    @click.option(
        "--nonetcdf",
        default=False,
        help="Does not include the netCDF file in the created metadata if set to `TRUE`.",
    )
    def create_item_command(
        source: str,
        destination: str,
        collection: str = "",
        nocog: bool = False,
        nonetcdf: bool = False,
    ) -> None:
        """Creates a STAC Item

        Args:
            source (str): HREF of the Asset associated with the Item
            destination (str): An HREF for the STAC Item
        """
        stac_collection = None
        if len(collection) > 0:
            stac_collection = Collection.from_file(collection)

        item = stac.create_item(source, stac_collection, nocog, nonetcdf)
        item.save_object(dest_href=destination)

        return None

    return esaccilc
