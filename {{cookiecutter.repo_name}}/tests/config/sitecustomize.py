"""
This code enables coverage tracking in subprocesses.
https://coverage.readthedocs.io/en/coverage-5.3/subprocess.html#configuring-python-for-sub-process-coverage
It is never executed from the directory it's checked into git (tests/config/).
Rather, the Dockerfile copies it to the Python installation directory
(/usr/local/pyenv/versions/${PYVERSION}/), where it is loaded automatically
each time the Python interpreter starts up.
For more information, see:
* https://docs.python.org/3/library/site.html
* https://pymotw.com/3/site/#customizing-site-configuration
"""
try:
    import os

    import coverage

    # NOTE: This is equivalent to mcdsgcptools.is_production(), but this avoids
    # requiring that package be installed. (We'd like the cookiecutter to place
    # very few runtime dependencies on the projects it creates.)
    if not os.environ.get('IS_PROD', '0') != '0':
        coverage.process_startup()
except ImportError:
    pass
