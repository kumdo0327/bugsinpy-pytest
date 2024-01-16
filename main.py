import sys
import os
import pytest


global_counter = 1


class CollectPlugin:
    def __init__(self) -> None:
        self.collection = list()

    def pytest_collection_modifyitems(self, session, config, items):
        for item in items:
            self.collection.append(item.nodeid)


class SkipAlarmPlugin:
    def __init__(self, collection: list) -> None:
        self.map = dict()
        self.list = list()

    def pytest_runtest_logreport(self, report):
        if report.when is 'setup':
            self.list.append((report.nodeid, report.outcome))
            self.map[report.nodeid] = report.outcome


def extract_test_functions():
    collecting_plugin = CollectPlugin()
    pytest.main(["--collect-only"], plugins=[collecting_plugin])
    return collecting_plugin.collection


def runCoverage(test_target, number, omission):
    print(f'>> coverage run -m pytest {test_target}')
    os.system(f'coverage run -m pytest {test_target}')
    print(f'>> coverage json -o coverage/{number}/summary.json --omit="{omission}"')
    os.system(f'coverage json -o coverage/{number}/summary.json --omit="{omission}"')


def run_pytest(test_function, omission):
    # Run a single test case using pytest
    global global_counter
    print(f"Testing... >>> {test_function}")
    exitcode = pytest.main([test_function])
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
    #pytest.main(['tests/functional/test_bash.py::test_with_confirmation[proc0]'], plugins=[SkipAlarmPlugin()])
    #test_functions = extract_test_functions()
    testing_plugin = SkipAlarmPlugin(['tests/functional/test_bash.py::test_with_confirmation[proc0]'])
    pytest.main(['tests/functional/test_bash.py::test_with_confirmation[proc0]'], plugins=[testing_plugin])

    failed = 0
    skipped = 0
    passed = 0
    for _, report in testing_plugin.map.items():
        if report is 'passed':
            passed += 1
        elif report is 'failed':
            failed += 1
        elif report is 'skipped':
            skipped += 1

    for nodeid, outcome in testing_plugin.list:
        print(nodeid, outcome)
    print(len(testing_plugin.list))
    print(failed, passed, skipped)
    return

    
    
    omission = "/usr/local/lib/*,"
    for arg in sys.argv[1:]:
        omission = omission + os.path.join(arg, '*,')
    if omission.endswith(','):
        omission = omission[:-1]

    for test_function in test_functions:
        run_pytest(test_function, omission)


if __name__ == '__main__':
    main()
