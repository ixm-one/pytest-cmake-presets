from abc import abstractmethod
from collections.abc import Iterator, Mapping
from pathlib import Path
from subprocess import CalledProcessError, TimeoutExpired
from typing import Any, Optional, final
import contextlib
import copy
import functools
import os
import re
import shutil
import subprocess
import typing

from pytest import File, Item
import pytest

from . import presets
from .vendor import VendorProperties


class CMakePresetItem(Item):

    properties: VendorProperties
    process: Optional[subprocess.CompletedProcess]
    env: Mapping[str, str]

    def __init__(self, *, preset, **kwargs):
        super().__init__(**kwargs)
        self.preset = preset
        self.env = copy.deepcopy(os.environ) | dict(
            PYTEST_INVOCATION_DIR=os.fspath(self.config.invocation_params.dir),
            PYTEST_ROOT_DIR=os.fspath(self.config.rootpath),
        )
        vendor = self.preset.vendor.get("pytest-cmake-presets", {})
        self.properties = VendorProperties.from_dict(vendor)
        self.process = None

    def runtest(self) -> None:
        with self.run() as process:
            self.process = process

    def repr_failure(self, excinfo):
        # TODO: We need to properly display the stdout/stderr of the process.
        if isinstance(excinfo.value, CalledProcessError):
            command = " ".join(map(os.fspath, excinfo.value.cmd))
            return "\n".join(
                [
                    f"command: {command}",
                    f"returned: {excinfo.value.returncode}",
                    f"stdout: {excinfo.value.output}",
                    f"stderr: {excinfo.value.stderr}",
                ]
            )
        elif isinstance(excinfo.value, TimeoutExpired):
            command = " ".join(map(os.fspath, excinfo.value.cmd))
            return f"command: {command}\ntimeout: {excinfo.value.timeout}"
        return super().repr_failure(excinfo)

    def reportinfo(self):
        return self.path, 0, f"preset: {self.preset.display_name}"

    @contextlib.contextmanager
    def run(self) -> Iterator[subprocess.CompletedProcess]:
        self.config.hook.pytest_cmake_setup_preset(item=self)
        args: dict[str, Any] = dict(
            cwd=self.path,
            env=self.env,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if timeout := self.properties.timeout:
            args.update(timeout=timeout)
        if log_cli := self.config.getini("log_cli"):
            args.update(shell=log_cli)
        command = Path(typing.cast(str, self.config.getoption(self.option, skip=True)))
        if len(command.parts):
            command = shutil.which(command)
        if command is None:
            pytest.skip(f"could not find {command} on system PATH")
        try:
            yield subprocess.run([command, *self.arguments], **args)
        finally:
            self.config.hook.pytest_cmake_teardown_preset(item=self)

    # This should be defaulted to cmake
    # operations performed on the resulting value should just simply be
    # handled by this class, rather than on a per-class basis
    @property
    def option(self) -> str:
        return "cmake"

    @property
    @abstractmethod
    def arguments(self) -> list[str]:
        pass


@final
class CMakePresetConfigureItem(CMakePresetItem):
    @property
    def arguments(self) -> list[str]:
        return [f"--preset={self.preset.name}", "--fresh"]


@final
class CMakePresetBuildItem(CMakePresetItem):
    @property
    def arguments(self) -> list[str]:
        return ["--build", f"--preset={self.preset.name}"]


@final
class CMakePresetTestItem(CMakePresetItem):
    @property
    def option(self) -> str:
        return "ctest"

    @property
    def arguments(self) -> list[str]:
        return [f"--preset={self.preset.name}"]


@final
class CMakePresetPackageItem(CMakePresetItem):
    @property
    def option(self) -> str:
        return "cpack"

    @property
    def arguments(self) -> list[str]:
        return [f"--preset={self.preset.name}"]


@final
class CMakePresetWorkflowItem(CMakePresetItem):
    @property
    def arguments(self) -> list[str]:
        return ["--workflow", f"--preset={self.preset.name}"]


@final
class CMakePresetsFile(File):
    def collect(self) -> Iterator[CMakePresetItem]:
        cmake_presets = presets.load(self.path.joinpath("CMakePresets.json"))
        vendor = cmake_presets.vendor.get("pytest-cmake-presets", {})
        properties = VendorProperties.from_dict(vendor)
        content = {
            CMakePresetConfigureItem: cmake_presets.configure_presets,
            CMakePresetBuildItem: cmake_presets.build_presets,
        }
        for cls, values in content.items():
            for preset in values:
                if preset.hidden:
                    continue
                item = cls.from_parent(self, name=preset.name, preset=preset)
                if skip_if := properties.skip_if:
                    item.add_marker(pytest.mark.skipif(**skip_if))

                # TODO: This needs to be a hook call of some kind. That or we
                # do the marking in the constructor class.
                if item.properties is None:
                    yield item
                if reason := item.properties.skip:
                    item.add_marker(pytest.mark.skip(reason=reason))
                if skippable := item.properties.skip_if:
                    item.add_marker(pytest.mark.skipif(**skippable))
                if xfail := item.properties.xfail:
                    item.add_marker(pytest.mark.xfail(**xfail))
                for filename in item.properties.required_files:
                    if not filename.exists():
                        reason = f"required file '{filename}' does not exist"
                        item.add_marker(pytest.mark.skip(reason=reason))
                yield item


# TODO: This hook needs to be moved to the collect stage, as markers need to be
# applied *before* runtest.
# NOTE: This is currently repeated verbatim in the collect function
@pytest.hookimpl(tryfirst=True)
def pytest_cmake_setup_preset(item: CMakePresetConfigureItem):
    if item.properties is None:
        return
    if reason := item.properties.skip:
        item.add_marker(pytest.mark.skip(reason=reason))
    if skippable := item.properties.skip_if:
        item.add_marker(pytest.mark.skipif(**skippable))
    if xfail := item.properties.xfail:
        item.add_marker(pytest.mark.xfail(**xfail))
    for filename in item.properties.required_files:
        if not filename.exists():
            reason = f"required file '{filename}' does not exist"
            item.add_marker(pytest.mark.skip(reason=reason))


@pytest.hookimpl(trylast=True)
def pytest_cmake_teardown_preset(item: CMakePresetConfigureItem):
    if item.properties is None or item.process is None:
        return

    stdout = functools.partial(re.search, string=item.process.stdout, flags=re.MULTILINE)
    stderr = functools.partial(re.search, string=item.process.stderr, flags=re.MULTILINE)

    def match(pattern):
        return stdout(pattern) or stderr(pattern)

    def because(pattern, match):
        return f"regex '{pattern}' matched {match.string[match.start():match.end()]}"

    if (skip_regex := item.properties.skip_regex) and (matched := match(skip_regex)):
        pytest.skip(reason=because(skip_regex, matched))
    elif (fail_regex := item.properties.fail_regex) and (matched := match(fail_regex)):
        pytest.fail(reason=because(fail_regex, matched), pytrace=False)
    elif (pass_regex := item.properties.pass_regex) and (matched := match(pass_regex)):
        return

    skip_return_code = item.properties.skip_return_code
    if skip_return_code is not None and skip_return_code == item.process.returncode:
        reason = f"{item.preset.name} returned {item.process.returncode}"
        pytest.skip(reason=reason)

    # TODO: needs to actually fail *if* the returncode is 0
    if not item.properties.will_fail:
        item.process.check_returncode()
