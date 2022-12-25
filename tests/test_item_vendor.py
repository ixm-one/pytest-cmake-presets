import json
import textwrap


def test_skip_if(pytester, cmake_project, cmake_presets, vendor):
    vendor["pytest-cmake-presets"] |= {"skip-if": dict(condition=True, reason="testing")}
    cmake_presets["configurePresets"][0] |= dict(vendor=vendor)

    pytester.maketxtfile(CMakeLists=cmake_project)
    pytester.makefile(".json", CMakePresets=json.dumps(cmake_presets))

    result = pytester.runpytest()
    result.assert_outcomes(skipped=1)


def test_will_fail(pytester, cmake_project, cmake_presets, vendor):
    vendor["pytest-cmake-presets"] |= {"will-fail": True}
    cmake_presets["configurePresets"][0] |= dict(vendor=vendor)
    cmake_project.append('message(FATAL_ERROR "Expected Failure")')

    pytester.maketxtfile(CMakeLists=cmake_project)
    pytester.makefile(".json", CMakePresets=json.dumps(cmake_presets))

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_fail_regex(pytester, cmake_project, cmake_presets, vendor, request):
    vendor["pytest-cmake-presets"] |= {"fail-regex": request.node.name}
    cmake_presets["configurePresets"][0] |= dict(vendor=vendor)

    pytester.maketxtfile(CMakeLists=cmake_project)
    pytester.makefile(".json", CMakePresets=json.dumps(cmake_presets))

    result = pytester.runpytest()
    result.assert_outcomes(failed=1)


def test_pass_regex(pytester, cmake_project, cmake_presets, vendor, request):
    vendor["pytest-cmake-presets"] |= {"pass-regex": f"-- {request.node.name}"}
    cmake_presets["configurePresets"][0] |= dict(vendor=vendor)
    cmake_project.append(f'message(FATAL_ERROR "{request.node.name}")')

    pytester.maketxtfile(CMakeLists=cmake_project)
    pytester.makefile(".json", CMakePresets=json.dumps(cmake_presets))

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_skip_regex(pytester, cmake_project, cmake_presets, vendor, request):
    vendor["pytest-cmake-presets"] |= {"skip-regex": f"-- {request.node.name}"}
    cmake_presets["configurePresets"][0] |= dict(vendor=vendor)
    cmake_project.append(f'message(FATAL_ERROR "{request.node.name}")')

    pytester.maketxtfile(CMakeLists=cmake_project)
    pytester.makefile(".json", CMakePresets=json.dumps(cmake_presets))

    result = pytester.runpytest()
    result.assert_outcomes(skipped=1)


def test_skip_return_code(pytester, cmake_project, cmake_presets, vendor):
    vendor["pytest-cmake-presets"] |= {"skip-return-code": 0}
    cmake_presets["configurePresets"][0] |= dict(vendor=vendor)

    pytester.maketxtfile(CMakeLists=cmake_project)
    pytester.makefile(".json", CMakePresets=json.dumps(cmake_presets))

    result = pytester.runpytest()
    result.assert_outcomes(skipped=1)


def test_timeout(pytester, cmake_project, cmake_presets, vendor):
    vendor["pytest-cmake-presets"] |= dict(timeout=10)
    cmake_presets["configurePresets"][0] |= dict(vendor=vendor)

    pytester.maketxtfile(CMakeLists=cmake_project)
    pytester.makefile(".json", CMakePresets=json.dumps(cmake_presets))

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_timeout_fails(pytester, cmake_project, cmake_presets, vendor):
    vendor["pytest-cmake-presets"] |= dict(timeout=1)
    cmake_presets["configurePresets"][0] |= dict(vendor=vendor)

    command = textwrap.dedent("""execute_process(COMMAND "${CMAKE_COMMAND}" -E sleep 3)""")
    cmake_project.append(command)

    pytester.maketxtfile(CMakeLists=cmake_project)
    pytester.makefile(".json", CMakePresets=json.dumps(cmake_presets))

    result = pytester.runpytest()
    result.assert_outcomes(failed=1)
