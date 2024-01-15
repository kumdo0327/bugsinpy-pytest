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
        self.map = {nodeid : str() for nodeid in collection}
        self.list = list()

    def pytest_collectreport(self, report):
        self.list.append((report.nodeid, report.outcome))
        if report.nodeid in self.map.keys():
            self.map[report.nodeid] = report.outcome


def extract_test_functions(plugin):
    pytest.main(["--collect-only"], plugins=[plugin])
    return plugin.collection


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
    collecting_plugin = CollectPlugin()
    test_functions = extract_test_functions(collecting_plugin)

    testing_plugin = SkipAlarmPlugin(collecting_plugin.collection)
    pytest.main([], plugins=[testing_plugin])

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

    print(failed, passed, skipped)

    for nodeid, outcome in testing_plugin.list:
        print(nodeid, outcome)
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
