from click import Command, Group

from .cog.commands import create_command as create_cog_command
from .netcdf.commands import create_command as create_netcdf_command


def create_esaccilc_command(cli: Group) -> Command:
    """Creates the stactools-esa-cci-lc command line utility."""

    @cli.group(
        "esa-cci-lc",
        short_help=("Commands for working with ESA CCI data"),
    )
    def esaccilc() -> None:
        pass

    create_cog_command(esaccilc)
    create_netcdf_command(esaccilc)

    return esaccilc
