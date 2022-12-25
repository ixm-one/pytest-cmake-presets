import json


def test_single(pytester, cmake_project, cmake_presets):
    pytester.maketxtfile(CMakeLists=cmake_project)
    pytester.makefile(".json", CMakePresets=json.dumps(cmake_presets))

    result = pytester.runpytest(["--verbose"])
    result.assert_outcomes(passed=1)


def test_none(pytester, cmake_project):
    pytester.maketxtfile(CMakeLists=cmake_project)

    result = pytester.runpytest(["--verbose"])
    result.assert_outcomes()
