import logging

import click
from click import Command, Group

from stactools.esa_cci_lc import stac

logger = logging.getLogger(__name__)


def create_esaccilc_command(cli: Group) -> Command:
    """Creates the stactools-esa-cci-lc command line utility."""

    @cli.group(
        "esaccilc",
        short_help=("Commands for working with stactools-esa-cci-lc"),
    )
    def esaccilc() -> None:
        pass

    @esaccilc.command(
        "create-collection",
        short_help="Creates a STAC collection",
    )
    @click.argument("destination")
    def create_collection_command(destination: str) -> None:
        """Creates a STAC Collection

        Args:
            destination (str): An HREF for the Collection JSON
        """
        collection = stac.create_collection()

        collection.set_self_href(destination)

        collection.save_object()

        return None

    @esaccilc.command("create-item", short_help="Create a STAC item")
    @click.argument("source")
    @click.argument("destination")
    def create_item_command(source: str, destination: str) -> None:
        """Creates a STAC Item

        Args:
            source (str): HREF of the Asset associated with the Item
            destination (str): An HREF for the STAC Item
        """
        item = stac.create_item(source)

        item.save_object(dest_href=destination)

        return None

    return esaccilc
