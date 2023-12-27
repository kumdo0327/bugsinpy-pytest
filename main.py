import subprocess
import sys
import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.main import Session
from _pytest.nodes import Item

def collect_tests(test_dir):
    # Configuring pytest
    config = Config()
    parser = Parser()
    config._parser = parser
    config.parse([test_dir])

    # Creating a session
    session = Session(config)
    session.perform_collect()

    # Collecting test items
    return session.items

def run_test(test_item):
    # Running an individual test
    return pytest.main(['-k', test_item.name])

def run_tests(test_dir):
    # Collect tests
    test_items = collect_tests(test_dir)

    # Execute tests individually
    for item in test_items:
        print(f"Running test: {item.name}")
        result = run_test(item)
        if result == 0:
            print(f"Test {item.name} passed")
        else:
            print(f"Test {item.name} failed")

if __name__ == "__main__":
    # Directory containing tests
    test_dir = "./tests"
    run_tests(test_dir)
