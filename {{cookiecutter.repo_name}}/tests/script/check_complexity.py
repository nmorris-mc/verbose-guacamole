import ast
import os
import re
import subprocess
import sys

# This specifies the level of complexity that will cause the "mccabe" tool to
# output the name and complexity of the function. In other words, the function
# is not necessarily too complex, but perhaps complex enough to inform the
# developers.
MEDIUM_COMPLEXITY = 5


def process_complexity_record(py_module_path, line):
    """
    Given a complexity record about a single function, print a message about it.
    If the complexity is too high, note that. Returns False if the function's
    complexity is acceptable and True if it is too high.
    :param py_module_path: Path to the .py file
    :param line: Output line from mccabe
    """
    m = re.search(
        r"(?P<line_number>(\d+)):\d+:\s+\'(?P<function>([a-zA-Z_0-9\.]+))'\s+(?P<complexity>(\d+))",
        line)
    if m is not None:
        print('{}:{}: {}() has McCabe complexity {}'.format(
            py_module_path, m.group('line_number'), m.group('function'),
            int(m.group('complexity'))))


def process_complexity_report(py_module_path, complexity_output):
    """
    Parse a string that contains the results from running 'mccabe' on a single
    .py file. Print the contents and flag any too-complex functions. Returns
    False if the function's complexity is acceptable and True if it is too high.
    :param py_module_path: Path to the .py file
    :param complexity_output: String output from 'mccabe'
    """
    for line in complexity_output.split('\n'):
        if len(line) > 1:
            process_complexity_record(py_module_path, line)


def main():
    # If the current branch has no new or modified Python files, this script
    # will be called with no arguments. Ignore this.
    if len(sys.argv) >= 2:
        py_module_path = sys.argv[1]
        if os.path.isfile(py_module_path):
            complexity_output = subprocess.check_output([
                sys.executable, '-m', 'mccabe', py_module_path, '--min',
                str(MEDIUM_COMPLEXITY)
            ]).decode('utf-8')
            if len(complexity_output) > 1:
                header = f'McCabe complexity for {py_module_path}'
                print(header)
                print('=' * len(header))
                process_complexity_report(py_module_path, complexity_output)
                print()


if __name__ == '__main__':
    main()
