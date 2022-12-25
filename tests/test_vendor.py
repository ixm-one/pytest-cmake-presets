import json


def test_skip_if(pytester, cmake_project, cmake_presets, vendor):
    vendor["pytest-cmake-presets"] |= {"skip-if": dict(condition=True, reason="testing")}
    cmake_presets |= dict(vendor=vendor)
    pytester.maketxtfile(CMakeLists=cmake_project)
    pytester.makefile(".json", CMakePresets=json.dumps(cmake_presets))

    result = pytester.runpytest()
    result.assert_outcomes(skipped=1)
