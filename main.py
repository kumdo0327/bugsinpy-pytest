import sys
import os
import re
import subprocess

def find_test_files(directory):
    """Find all test files in the given directory."""
    test_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith('test_') and file.endswith('.py') or file.endswith('_test.py'):
                test_files.append(os.path.join(root, file))
    return test_files

def extract_test_functions(file_path):
    """Extract test function names from a test file."""
    test_functions = []
    with open(file_path, 'r') as file:
        content = file.read()
        test_functions = re.findall(r'def (test_\w+)', content)
    return test_functions

def run_pytest(test_file, test_function):
    """Run a single test case using pytest."""

    cmd = f'pytest {test_file}::{test_function}'
    print(cmd)
    #subprocess.run(cmd, shell=True)

def main():
    test_directory = './tests'  # Replace with the path to your test directory
    test_files = find_test_files(test_directory)

    for test_file in test_files:
        test_functions = extract_test_functions(test_file)
        for test_function in test_functions:
            run_pytest(test_file, test_function)

if __name__ == '__main__':
    main()
