import sys
import os
import pytest


global_counter = 1
skip_flag = False


class CollectPlugin:
    def __init__(self) -> None:
        self.collection = list()

    def pytest_collection_modifyitems(self, items):
        for item in items:
            self.collection.append(item.nodeid)


class SkipAlarmPlugin:
    def pytest_runtest_protocol(self, item, nextitem):
        global skip_flag
        reports = yield
        # Check if the test has been skipped
        if reports.setup.outcome == "skipped" or reports.call.outcome == "skipped":
            # Perform the action you want when a test is skipped
            skip_flag = True            


def extract_test_functions():
    plugin = CollectPlugin()
    pytest.main(["--collect-only"], plugins=[plugin])
    return plugin.collection


def runCoverage(test_target, number, omission):
    print(f'>> coverage run -m pytest {test_target}')
    os.system(f'coverage run -m pytest {test_target}')
    print(f'>> coverage json -o coverage/{number}/summary.json --omit="{omission}"')
    os.system(f'coverage json -o coverage/{number}/summary.json --omit="{omission}"')


def run_pytest(test_function, omission):
    # Run a single test case using pytest
    global global_counter, skip_flag
    print(f"Testing... >>> {test_function}")
    exitcode = pytest.main([test_function])
    
    if skip_flag:
        print('ExitCode is SKIPPED')
        skip_flag = False
        return

    print(f"ExitCode is {exitcode}")

    if exitcode == 0:
        runCoverage(test_function, global_counter, omission)
        with open(f'coverage/{global_counter}/{global_counter}.test', 'w') as f:
            f.write('passed')
        global_counter += 1
    
    elif exitcode == 1:
        runCoverage(test_function, global_counter, omission)
        with open(f'coverage/{global_counter}/{global_counter}.test', 'w') as f:
            f.write('failed')
        global_counter += 1


def main():
    global skip_flag
    pytest.main(['tests/functional/test_bash.py::test_with_confirmation[proc0]'], plugins=[SkipAlarmPlugin()])
    print(f"Exitcode SKIPPED is {skip_flag}")
    return

    test_functions = extract_test_functions()
    
    omission = "/usr/local/lib/*,"
    for arg in sys.argv[1:]:
        omission = omission + os.path.join(arg, '*,')
    if omission.endswith(','):
        omission = omission[:-1]

    for test_function in test_functions:
        run_pytest(test_function, omission)


if __name__ == '__main__':
    main()
