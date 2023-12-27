import subprocess
import sys
import pytest
import os

def is_test_file(file_name):
    return file_name.startswith("test_") or file_name.endswith("_test.py")

def discover_pytest_cases(directory):
    test_cases = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if is_test_file(file):
                file_path = os.path.join(root, file)
                module_name = os.path.splitext(file_path)[0].replace(os.sep, ".")
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.strip().startswith("def test_"):
                            function_name = line.split("(")[0].split()[1]
                            test_cases.append(f"{module_name}::{function_name}")
    return test_cases

def run_tests(test_dir):
    test_cases = discover_pytest_cases(test_dir)
    for test_case in test_cases:
        print(f"Running {test_case}")
        return
        result = pytest.main(['-k', test_case])
        if result == 0:
            print(f"{test_case} passed")
        else:
            print(f"{test_case} failed")

if __name__ == "__main__":
    test_dir = "./tests"  # replace with your test directory
    run_tests(test_dir)
