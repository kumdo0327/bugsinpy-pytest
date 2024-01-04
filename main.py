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


""""
def find_test_files(directory):
    # Find all test files in the given directory
    test_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith('test_') and file.endswith('.py') or file.endswith('_test.py'):
                test_files.append(os.path.join(root, file))
    return test_files
"""


def extract_test_functions(path):
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            test_functions = re.findall(r'def (test_\w+)', content)
    except UnicodeDecodeError:
        print(file_path)
    """
    
    plugin = Plugin()
    pytest.main(["--collect-only", path], plugins=[plugin])
    return plugin.collection


def run_pytest(test_function):
    # Run a single test case using pytest
    global global_counter

    subprocess.call(['coverage', 'run', '-m', 'pytest', test_function])
    subprocess.call(['coverage', 'json', '-o', f'coverage/{global_counter}/summary.json', f'--omit={sys.argv[1]}/*.py'])

    exitcode = pytest.main([test_function])
    with open(f'coverage/{global_counter}/{global_counter}.output', 'w') as f:
        pass
    with open(f'coverage/{global_counter}/{global_counter}.test', 'w') as f:
        f.write('passed' if exitcode is pytest.ExitCode.OK else 'failed')

    global_counter += 1



def main():
    test_functions = extract_test_functions(sys.argv[1])
    for test_function in test_functions:
        run_pytest(test_function)


if __name__ == '__main__':
    main()
