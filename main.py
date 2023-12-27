import sys
import os
import re
import subprocess
import pytest

global_counter = 1

def find_test_files(directory):
    # Find all test files in the given directory
    test_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith('test_') and file.endswith('.py') or file.endswith('_test.py'):
                test_files.append(os.path.join(root, file))
    return test_files

def extract_test_functions(file_path):
    # Extract test function names from a test file
    test_functions = []
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            test_functions = re.findall(r'def (test_\w+)', content)
    except UnicodeDecodeError:
        print(file_path)
    return test_functions

def run_pytest(test_file, test_function):
    # Run a single test case using pytest
    global global_counter

    subprocess.call(['coverage', 'run', '-m', 'pytest', f'{test_file}::{test_function}'])
    subprocess.call(['coverage', 'json', '-o', f'coverage/{global_counter}/summary.json', f'--omit={sys.argv[1]}/*.py'])

    _, exitcode = pytest.main([f'{test_file}::{test_function}'])
    with open(f'coverage/{global_counter}/{global_counter}.output', 'w') as f:
        pass
    with open(f'coverage/{global_counter}/{global_counter}.test', 'w') as f:
        f.write('passed' if exitcode == 0 else 'failed')

    global_counter += 1



def main():
    test_files = find_test_files(sys.argv[1])

    for test_file in test_files:
        test_functions = extract_test_functions(test_file)
        for test_function in test_functions:
            run_pytest(test_file, test_function)

if __name__ == '__main__':
    main()
