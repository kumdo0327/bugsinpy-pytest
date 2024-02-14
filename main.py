import sys
import os
import pytest
import subprocess


global_counter = 1


class SkipAlarmPlugin:
    def __init__(self) -> None:
        self.map = dict()

    def pytest_runtest_logreport(self, report):
        if report.nodeid in self.map.keys():
            if report.outcome == 'failed' or report.outcome == 'skipped' and self.map[report.nodeid] == 'passed':
                self.map[report.nodeid] = report.outcome
        else:
            self.map[report.nodeid] = report.outcome

    def toList(self) -> list:
        return [(nodeid, report) for nodeid, report in self.map.items()]
    


def runPytest() -> list:
    plugin = SkipAlarmPlugin()
    pytest.main(["tests"], plugins=[plugin])
    return plugin.toList()



def commandCoverage(test_target, omission, text):
    global global_counter
    if 'test_multiprocessing.py' in test_target:
        return

    print(f'\n>> >> Pytest {global_counter}')
    exit_code = pytest.main([test_target])
    print(f'\n>> >> ExitCode is {exit_code}')
    if exit_code == 0 or exit_code == 1:

        print(f'\n>> >> Run Coverage {global_counter} : "{test_target}"')
        subprocess.run(['coverage', 'run', '-m', 'pytest', test_target])

        print(f'\n>> >> Wrote Json {global_counter} : "{test_target}"')
        subprocess.run(['coverage', 'json', '-o', f'coverage/{global_counter}/summary.json', '--omit', omission])
        
        with open(f'coverage/{global_counter}/{global_counter}.test', 'w') as f:
            f.write(text)
        global_counter += 1



def runCoverage(test_function, report, omission):
    if report == 'skipped':
        return
    if report == 'passed':
        commandCoverage(test_function, omission, 'passed')
    elif report == 'failed':
        commandCoverage(test_function, omission, 'failed')



def main():
    omission = "/usr/local/lib/*,"
    for arg in sys.argv[1:]:
        omission = omission + os.path.join(arg, '*,')
    if omission.endswith(','):
        omission = omission[:-1]

    for test_function, report in runPytest():
        runCoverage(test_function, report, omission)


if __name__ == '__main__':
    main()
