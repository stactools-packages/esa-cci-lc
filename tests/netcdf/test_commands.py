import os
from tempfile import TemporaryDirectory
from typing import Callable, List

import pystac
from click import Command, Group
from stactools.testing.cli_test import CliTestCase

from stactools.esa_cci_lc.commands import create_esaccilc_command
from tests import test_data


class CommandsTest(CliTestCase):
    def create_subcommand_functions(self) -> List[Callable[[Group], Command]]:
        return [create_esaccilc_command]

    def test_create_netcdf_item(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            nc_filename = "C3S-LC-L4-LCCS-Map-300m-P1Y-2018-v2.1.1.nc"
            nc_path = test_data.get_external_data(nc_filename)

            result = self.run_command(
                f"esa-cci-lc netcdf create-item {nc_path} "
                f"{os.path.join(tmp_dir, 'C3S-LC-L4-LCCS-Map-300m-P1Y-2018-v2.1.1.json')}"
            )
            assert result.exit_code == 0, "\n{}".format(result.output)

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            assert len(jsons) == 1
            item = pystac.read_file(os.path.join(tmp_dir, jsons[0]))

            item.validate()

    def test_create_netcdf_collection(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            result = self.run_command(
                f"esa-cci-lc netcdf create-collection "
                f"{os.path.join(tmp_dir, 'collection.json')}"
            )
            assert result.exit_code == 0, "\n{}".format(result.output)

            collection = pystac.read_file(os.path.join(tmp_dir, "collection.json"))
            assert collection.id == "esa-cci-lc-netcdf"

            collection.validate()
