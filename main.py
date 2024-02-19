import sys
import os
import pytest
import subprocess


global_counter = 1
timeout = 30



class BaseState:
    def __init__(self):
        outcome: str
    def newState(self, report: str):
        match report:
            case 'passed':
                return self
            case 'skipped':
                return self._caseSkipped()
            case 'failed':
                if 'Timeout' in str(report.longrepr) and report.duration > timeout - 1:
                    return self._caseTimeout()
                else:
                    return self._caseFailed()
    def _caseSkipped(self):
        return self
    def _caseFailed(self):
        return self
    def _caseTimeout(self):
        return self

class PassedState(BaseState):
    def __init__(self):
        outcome: str = 'passed'
    def _caseSkipped(self) -> None:
        return SkippedState()
    def _caseFailed(self) -> None:
        return FailedState()
    def _caseTimeout(self) -> None:
        return TimeoutState()

class SkippedState(BaseState):
    def __init__(self):
        outcome: str = 'skipped'
    def _caseFailed(self) -> None:
        return FailedState()
    def _caseTimeout(self) -> None:
        return TimeoutState()

class FailedState(BaseState):
    def __init__(self):
        outcome: str = 'failed'
    def _caseTimeout(self) -> None:
        return TimeoutState()

class TimeoutState(BaseState):
    def __init__(self):
        outcome: str = 'timeout'



class SkipAlarmPlugin:
    def __init__(self) -> None:
        self.map = dict[str, BaseState]

    def pytest_runtest_logreport(self, report):
        if report.nodeid not in self.map.keys():
            self.map[report.nodeid] = PassedState()
        self.map[report.nodeid] = self.map[report.nodeid].newState(report.nodeid)

    def toList(self) -> list:
        f = 0
        p = 0
        s = 0
        failed_tcs = list()
        for nodeid, report in self.map.items():
            f += 1 if report.outcome == 'failed' else 0
            p += 1 if report.outcome == 'passed' else 0
            s += 1 if report.outcome == 'skipped' or 'timeout' else 0
            if report.outcome == 'failed':
                failed_tcs.append(nodeid)

        print(f"=== {f} failed, {p} passed, {s} skipped ===")
        for nodeid in failed_tcs:
            print('FAILED', nodeid)
        return [(nodeid, report.outcome) for nodeid, report in self.map.items()]



def runPytest() -> list:
    plugin = SkipAlarmPlugin()
    print('=== pytest', sys.argv[1], f"--timeout={timeout}", '--ignore='+sys.argv[2] if len(sys.argv) > 2 else '')
    pytest.main([sys.argv[1], f"--timeout={timeout}", '--ignore='+sys.argv[2] if len(sys.argv) > 2 else ''], plugins=[plugin])
    return plugin.toList()
    # '--continue-on-collection-errors',



def commandCoverage(test_target, omission, text):
    global global_counter

    print(f'\n===> Pytest {global_counter}')
    exit_code = pytest.main([test_target])
    print(f'\n===> ExitCode is {exit_code}')
    if exit_code == 0 or exit_code == 1:

        print(f'\n===> Run Coverage {global_counter} : "{test_target}"')
        subprocess.run(['coverage', 'run', '-m', 'pytest', test_target])

        print(f'\n===> Wrote Json {global_counter} : "{test_target}"')
        subprocess.run(['coverage', 'json', '-o', f'coverage/{global_counter}/summary.json', '--omit', omission])
        
        with open(f'coverage/{global_counter}/{global_counter}.test', 'w') as f:
            f.write(text)
        global_counter += 1



def runCoverage(test_function, report, omission):
    if report == 'timeout' or 'skipped':
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
