from pathlib import Path
import shutil

from pytest import Collector, Parser, PytestPluginManager

from . import hooks, items


def pytest_addoption(parser: Parser):
    group = parser.getgroup("cmake-presets", description="cmake presets options")
    group.addoption(
        "--cmake",
        help="Path to the cmake executable to use in configure, build, and workflow presets",
        default=shutil.which("cmake"),
        type=Path,
    )
    group.addoption(
        "--ctest",
        help="Path to the ctest executable to use for test presets",
        default=shutil.which("ctest"),
        type=Path,
    )
    group.addoption(
        "--cpack",
        help="Path to the cpack executable to use for package presets",
        default=shutil.which("cpack"),
        type=Path,
    )


def pytest_addhooks(pluginmanager: PytestPluginManager):
    pluginmanager.add_hookspecs(hooks)
    pluginmanager.register(items)


def pytest_collect_file(parent: Collector, file_path: Path) -> Collector | None:
    if file_path.name == "CMakePresets.json":
        return items.CMakePresetsFile.from_parent(parent, path=file_path.parent)
