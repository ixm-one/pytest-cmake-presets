import os

import pytest

pytest_plugins = ["pytester", "cmake-presets"]


@pytest.fixture
def cmake_project(request):
    return [
        "cmake_minimum_required(VERSION 3.24)",
        f"project({request.node.name} LANGUAGES NONE)",
        "message(STATUS ${PROJECT_NAME})",
    ]


@pytest.fixture
def preset_prelude():
    return dict(
        version=5,
        cmakeMinimumRequired=dict(major=3, minor=24, patch=0),
    )


@pytest.fixture
def cmake_presets(pytester):
    return dict(
        version=5,
        cmakeMinimumRequired=dict(major=3, minor=24, patch=0),
        configurePresets=[
            dict(
                name="default",
                generator="Ninja",
                binaryDir=f"{os.fspath(pytester.path)}/build/${{presetName}}",
            )
        ],
    )


@pytest.fixture
def vendor():
    return {"pytest-cmake-presets": dict()}


@pytest.fixture
def configure_preset(pytester):
    return dict(
        name="default",
        generator="Ninja",
        binaryDir=f"{os.fspath(pytester.path)}/build/${{presetName}}",
    )
