import logging
from pathlib import Path
from typing import List, Optional

import click
from click import Command, Group

from stactools.esa_cci_lc import constants
from stactools.esa_cci_lc.cog import stac

logger = logging.getLogger(__name__)


def create_command(esaccilc: Group) -> Command:
    @esaccilc.group(
        "cog",
        short_help=("Commands for working with ESA CCI COG tiles"),
    )
    def cog() -> None:
        pass

    @cog.command(
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
        collection = stac.create_collection(id, start_time, end_time)
        collection.set_self_href(destination)
        collection.save_object()

        return None

    @cog.command(
        "create-items",
        short_help="Creates STAC items for COG tiles derived from a NetCDF file",
    )
    @click.argument("source")
    @click.argument("destination_directory")
    @click.option(
        "--cog_tile_dim",
        default=constants.COG_TILE_DIM,
        help="COG tile dimension in pixels. Defaults to 16200.",
        type=int,
    )
    @click.option(
        "--tile_col_row",
        type=(int, int),
        help="Limit COG creation to a single tile within the tile grid at "
        "index location 'column' 'row'. Indices are 0 based.",
    )
    def create_items_command(
        source: str,
        destination_directory: str,
        cog_tile_dim: int,
        tile_col_row: Optional[List[int]],
    ) -> None:
        """Creates tiled COGs and Items from a source NetCDF file.

        \b
        Args:
            source (str): Local path to the NetCDF file.
            destination_directory (str): Directory to store created COGs and
                Items.
        """
        items = stac.create_items(
            source,
            destination_directory,
            cog_tile_dim=cog_tile_dim,
            tile_col_row=tile_col_row,
        )
        for item in items:
            dest_href = str(Path(destination_directory, f"{item.id}.json"))
            item.save_object(dest_href=dest_href)

        return None

    return cog
