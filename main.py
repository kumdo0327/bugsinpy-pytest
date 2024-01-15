import sys
import os
import re
import subprocess
import pytest


global_counter = 1


class Plugin:
    def __init__(self) -> None:
        self.collection = list()

    def pytest_collection_modifyitems(self, items):
        for item in items:
            self.collection.append(item.nodeid)


def extract_test_functions(path):
    plugin = Plugin()
    pytest.main(["--collect-only"], plugins=[plugin])
    return plugin.collection


def run_pytest(test_function, omission):
    # Run a single test case using pytest
    global global_counter
    print(f"Testing... >>> {test_function}")
    exitcode = pytest.main([test_function])
    print(f"ExitCode is {exitcode}")

    if exitcode == 0:
        subprocess.call(['coverage', 'run', '-m', 'pytest', test_function])
        subprocess.call(['coverage', 'json', '-o', f'coverage/{global_counter}/summary.json', f'--omit="{omission}"'])
        with open(f'coverage/{global_counter}/{global_counter}.test', 'w') as f:
            f.write('passed')
        global_counter += 1
    
    elif exitcode == 1:
        subprocess.call(['coverage', 'run', '-m', 'pytest', test_function])
        subprocess.call(['coverage', 'json', '-o', f'coverage/{global_counter}/summary.json', f'--omit="{omission}"'])
        with open(f'coverage/{global_counter}/{global_counter}.test', 'w') as f:
            f.write('failed')
        global_counter += 1


def main():
    test_functions = extract_test_functions(sys.argv[1])
    
    omission = "/usr/local/lib/*,"
    for arg in sys.argv[1:]:
        omission = omission + os.path.join(arg, '*,')
    if omission.endswith(','):
        omission = omission[:-1]

    for test_function in test_functions:
        run_pytest(test_function, omission)


if __name__ == '__main__':
    main()
