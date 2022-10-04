import json
import os.path
import shutil
from tempfile import TemporaryDirectory
from typing import Callable, List

import pytest
from click import Command, Group
from deepdiff import DeepDiff
from stactools.testing.cli_test import CliTestCase

from stactools.esa_cci_lc.commands import create_esaccilc_command

from . import constants


class CommandsTest(CliTestCase):
    def create_subcommand_functions(self) -> List[Callable[[Group], Command]]:
        return [create_esaccilc_command]

    def test_create_collection(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            src_file = os.path.join(constants.SRC_FOLDER, "collection.json")
            destination = os.path.join(tmp_dir, "collection.json")

            result = self.run_command(
                f"esa-cci-lc create-collection {destination}"
                f" --start_time 1995-01-01T00:00:00Z"
                f" --end_time 2022-12-31T23:59:59Z"
            )

            self.assertEqual(result.exit_code, 0, msg="\n{}".format(result.output))

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            collection = {}
            truth_collection = {}
            with open(destination) as f:
                collection = json.load(f)
            with open(src_file) as f:
                truth_collection = json.load(f)

            self.assertEqual(collection["id"], "esa-cci-lc")

            diff = DeepDiff(
                collection,
                truth_collection,
                ignore_order=True,
                exclude_regex_paths=r"root\['links'\]\[\d+\]\['href'\]",
            )
            if len(diff) > 0:
                print(diff)
            self.assertEqual(diff, {})

    @pytest.mark.usefixtures("pass_parameter")
    def test_create_item(self) -> None:
        for id in constants.TEST_FILES:
            with self.subTest(id=id):
                with TemporaryDirectory() as tmp_dir:
                    src_data_filename = f"{id}.nc"
                    stac_filename = f"{id}.json"

                    src_collection = os.path.join(
                        constants.SRC_FOLDER, "collection.json"
                    )
                    src_data_file = os.path.join(
                        constants.SRC_FOLDER, src_data_filename
                    )
                    dest_data_file = os.path.join(tmp_dir, src_data_filename)
                    shutil.copyfile(src_data_file, dest_data_file)

                    src_stac = os.path.join(constants.SRC_FOLDER, stac_filename)
                    dest_stac = os.path.join(tmp_dir, stac_filename)

                    cmd = (
                        f"esa-cci-lc create-item {dest_data_file} {dest_stac}"
                        f" --collection {src_collection}"
                    )
                    if not self.withcog:  # type: ignore[attr-defined]
                        cmd = cmd + " --nocog TRUE"

                    result = self.run_command(cmd)
                    self.assertEqual(
                        result.exit_code, 0, msg="\n{}".format(result.output)
                    )

                    files = os.listdir(tmp_dir)
                    jsons = [p for p in files if p.endswith(".json")]
                    self.assertEqual(len(jsons), 1)

                    item = {}
                    truth_item = {}
                    with open(dest_stac) as f:
                        item = json.load(f)
                    with open(src_stac) as f:
                        truth_item = json.load(f)

                    self.assertEqual(item["id"], id)

                    if self.withcog:  # type: ignore[attr-defined]
                        del truth_item["properties"]["classification:classes"]
                    else:
                        for key in constants.DATA_VARIABLES:
                            del truth_item["assets"][key]

                    diff = DeepDiff(
                        item,
                        truth_item,
                        ignore_order=True,
                        exclude_regex_paths=r"root\['(assets|links)'\]\[[\w']+\]\['href'\]",
                    )
                    if len(diff) > 0:
                        print(diff)
                    self.assertEqual(diff, {})
