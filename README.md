# Overview

`pytest-cmake-presets` was written to find and "test" [cmake-presets(7)][1] as
part of the [IXM][2] test harness. Each test is a single CMake preset that
might be part of a larger project. There are two aspects to tests: running
presets directly, and then testing the layout/result of the
[cmake-file-api(7)][3] after the fact. These second tests are performed via
normal pytest functions.

Tests can use the `vendor.pytest-cmake-presets` field to modify the expected
outcome of some tests.

Specifically, fields like `pass-regex`, `will-fail`, etc., can all modify the
behavior of an executed `CMakePresetItem`, allowing for *some* behavior to be
modified in a data-oriented fashion, instead of requiring pytest fixtures to
execute.

[1]: https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html
[2]: https://github.com/ixm-one/ixm
[3]: https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html
