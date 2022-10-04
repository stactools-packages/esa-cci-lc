from typing import Any

import pytest
from pytest import Parser


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--withcog",
        action="store_true",
        default=False,
        help="also test cog conversion (slow)",
    )


@pytest.fixture()
def pass_parameter(request: Any) -> None:
    setattr(request.cls, "withcog", request.config.getoption("--withcog"))
