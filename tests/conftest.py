from pytest import Metafunc, Parser


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--withcog",
        action="store_true",
        default=False,
        help="also test cog conversion (slow)",
    )


def pytest_generate_tests(metafunc: Metafunc) -> None:
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.withcog
    if "withcog" in metafunc.fixturenames and option_value is True:
        metafunc.parametrize("withcog", [option_value])
