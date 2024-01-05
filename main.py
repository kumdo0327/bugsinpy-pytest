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
    pytest.main(["--collect-only", path], plugins=[plugin])
    return plugin.collection


def run_pytest(test_function):
    # Run a single test case using pytest
    global global_counter
    print(test_function)
    exitcode = pytest.main([test_function])
    print(exitcode)

    if exitcode is pytest.ExitCode.OK:
        subprocess.call(['coverage', 'run', '-m', 'pytest', test_function])
        subprocess.call(['coverage', 'json', '-o', f'coverage/{global_counter}/summary.json', f'--omit={sys.argv[1]}/*.py'])
        with open(f'coverage/{global_counter}/{global_counter}.test', 'w') as f:
            f.write('passed')
        global_counter += 1
        return
    
    elif exitcode is pytest.ExitCode.TESTS_FAILED:
        subprocess.call(['coverage', 'run', '-m', 'pytest', test_function])
        subprocess.call(['coverage', 'json', '-o', f'coverage/{global_counter}/summary.json', f'--omit={sys.argv[1]}/*.py'])
        with open(f'coverage/{global_counter}/{global_counter}.test', 'w') as f:
            f.write('failed')
        global_counter += 1
        return


def main():
    test_functions = extract_test_functions(sys.argv[1])
    for test_function in test_functions:
        run_pytest(test_function)


if __name__ == '__main__':
    main()
