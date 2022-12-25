from .items import CMakePresetItem


def pytest_cmake_setup_preset(item: CMakePresetItem):  # pyright: ignore
    """runs before a preset is executed"""


def pytest_cmake_teardown_preset(item: CMakePresetItem):  # pyright: ignore
    """runs after a preset is executed"""
