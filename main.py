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
            if report.outcome is 'failed' or report.outcome is 'skipped' and self.map[report.nodeid] is 'passed':
                self.map[report.nodeid] = report.outcome
        else:
            self.map[report.nodeid] = report.outcome

    def toList(self) -> list:
        return [(nodeid, report) for nodeid, report in self.map.items()]
    

def runPytest() -> list:
    plugin = SkipAlarmPlugin()
    pytest.main([], plugins=[plugin])
    return plugin.toList()


def commandCoverage(test_target, number, omission):
    print(f'>> >> {number} : "{test_target}"')
    subprocess.run(['coverage', 'run', '-m', 'pytest', f'"{test_target}"', ';', 'coverage', 'json', '-o', f'coverage/{number}/summary.json', f'--omit="{omission}"'])


def runCoverage(test_function, report, omission):
    global global_counter
    if report is 'skipped':
        return
    
    if report is 'passed':
        commandCoverage(test_function, global_counter, omission)
        with open(f'coverage/{global_counter}/{global_counter}.test', 'w') as f:
            f.write('passed')
        global_counter += 1
    
    elif report is 'failed':
        commandCoverage(test_function, global_counter, omission)
        with open(f'coverage/{global_counter}/{global_counter}.test', 'w') as f:
            f.write('failed')
        global_counter += 1


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
