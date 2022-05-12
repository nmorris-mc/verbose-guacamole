# {{cookiecutter.package_name}}

<!-- To install the doctoc tool on your Mac, run: -->
<!--   brew update -->
<!--   brew install npm -->
<!--   npm install -g doctoc -->
<!-- Then, to add or update the table of contents for this file, run: -->
<!-- doctoc README.md -->

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Docker Development Environment](#docker-development-environment)
- [Running the Automated Tests in Docker](#running-the-automated-tests-in-docker)
- [Updating Python package requirements](#updating-python-package-requirements)
  - [While making other changes](#while-making-other-changes)
  - [Routine maintenance](#routine-maintenance)
- [Publishing New Versions](#publishing-new-versions)
- [Running Code Quality Checks Manually](#running-code-quality-checks-manually)
  - [Flake8](#flake8)
  - [pre-commit](#pre-commit)
    - [Disabling pre-commit](#disabling-pre-commit)
    - [SQLFluff in pre-commit and Continuous Integration](#sqlfluff-in-pre-commit-and-continuous-integration)
  - [Pylint](#pylint)
  - [McCabe Code Complexity Checker](#mccabe-code-complexity-checker)
  - [SQLFluff](#sqlfluff)
  - [Code Coverage](#code-coverage)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Docker Development Environment

Use Docker for development. To build, launch, and open a shell against a container,
ensure you're on VPN and run:

```
script/setup-docker
script/shell-docker
```

You can also use the `-s` option to open a shell immediately after setting up the container:
`script/setup-docker -s`

The project directory will be mounted in the container as a shared volume at
`/opt/app/src`, so changes you make to files on your
host machine will be reflected in the Docker container (the shared volume is configured
in `docker-compose.dev.yml`).

## Running the Automated Tests in Docker
Once you're in a bash session in the Docker container, run:

```
py.test -v tests/ integration_tests/
```

## Updating Python package requirements

There are two scenarios for updating requirements:
* While making other changes
* Routine maintenance (no other changes, just updating the project to use
  newer package versions)

### While making other changes

Edit `requirements/requirements.in`, then from inside Docker, run:

    script/update_requirements.sh

This script updates the `.txt` files in `requirements/`, but it's up to you to
include them in your PR.

### Routine maintenance

It's a good idea to do update the packages for a project at least 3 months.
This is particularly important packages that interact with Google Cloud, e.g.:

* `google-cloud-bigquery`
* `apache-beam`

To regenerate the `.txt` files in `requirements/` using the latest versions
allowed by the `.in` files, run the following command from *outside* Docker:

    script/pip_upgrade.sh

After updating the `.txt files`, this script also commits and pushes those
changes, then creates a PR titled "Update Python packages". This PR should be
reviewed and tested for problems before merging. (It's absolutely possible,
although unusual if you're using mature, mainstream packages, for new packages
to break previously working code.)


## Publishing New Versions

When submitting a Pull Request, update the version number in `setup.cfg` and `CHANGELOG.md`.
When your PR is merged to the `main` branch, Jenkins will build a source
distribution for the new version of the Python package and publish the new
version of the package to Artifactory. Jenkins will post a message to the
`#a-ds-blinken-lights` Slack channel indicating that the new version has been
published (or not published, for PRs that do not increment the version number).


## Running Code Quality Checks Manually

Cookiecutter projects run several code quality checks, both at git commit time
and during Jenkins builds. Sometimes it can be convenient to run these checks
manually, e.g. if you're introducing a new checking tool on a project with lots
of pre-existing code. Below are instructions for running these checks manually.

NOTE: Except for pre-commit, which is installed on the host machine, the packages
mentioned below are automatically included in the Docker development environment
for a cookiecutter project. Make sure to run these commands in the Docker
environment, not on the host machine. (If you want, you could install those
tools on the host as well, but that'll be an additional step, and you'll need
to keep an eye on whether you're using the same package version as the Docker
environment.)

### Flake8

Flake8 is a popular Python code style checking tool. The package
[documentation](https://flake8.pycqa.org/en/latest/#using-flake8) provides
instructions on running it manually.

### pre-commit

By default, cookiecutter projects include a tool called
[pre-commit](https://pre-commit.com/) It is a flexible tool that identifies
simple issues before submission to git and subsequent PR review. Running these
checks (aka "hooks") on every commit will automatically point out (and in many
cases, even fix) coding issues such as poor code formatting. By identifying and
addressing these issues prior to code review, this allows a reviewer to focus on
the design of a change while not wasting time with trivial style and formatting
nitpicks.

While pre-commit runs automatically as part of `git commit`, you can also run
it manually. For example, run `pre-commit` with the `--files` option to run on
a specific set of files or run `pre-commit --all-files` to run on all files.
[Docs](https://pre-commit.com/#pre-commit-run)

#### Disabling pre-commit

**You may find that pre-commit is too intrusive in the early stages of a project.
If so, you may wish to disable some of the checks or even disable pre-commit
entirely.** To do so:
* To disable pre-commit entirely, open the file `script/setup-docker` and
  comment out the line `pre-commit install`. Also, run the `pre-commit uninstall`
  from the project repo directory. This tells git not to run pre-commit anymore
  during `git commit`.
* To disable individual checks, open the file `.pre-commit-config.yaml` and
  comment out one or more of the checks.

**If you choose to partially or completely disable pre-commit, please consider
re-enabling it as a project nears production, when others are starting to review
and/or collaborate on the project.**

#### SQLFluff in pre-commit and Continuous Integration

The cookiecutter uses SQLFluff in two ways:
* Pre-commit step to automatically format the SQL (e.g. indentation)
* Continuous integration "lint" step to check for common SQL issues

Both these steps require a `.sqlfluff` configuration file in order to populate
the templated areas of the file. (SQLFluff cannot read the `run_job.sh` file
used when the SQL files actually run.) For more information on filling out the
`.sqlfluff` file, see the SQLFluff [documentation](https://docs.sqlfluff.com/en/stable/configuration.html)
or contact #ml-engineering in Slack.

### Pylint

PyLint is a popular Python code style checking tool. The package
[documentation](http://pylint.pycqa.org/en/latest/user_guide/run.html) provides
instructions on running it manually.

### McCabe Code Complexity Checker

McCabe is a package that analyzes code to look for functions that may be complex
and hard to understand. The package
[documentation](https://github.com/PyCQA/mccabe/blob/master/README.rst#standalone-script)
provides instructions on running it manually.

The complexity metric is determined by the number of possible paths through
the code, e.g. loops, conditionals, especially **nesting** of these. If mccabe
flags a function as too complex, you may wish to consider restructuringing the
code to reduce complexity. One common way to do this is to to extract one or
more helper functions that encapsulate logical subparts of the function. (Make
sure to do this sensibly, not just "mechanically"!)

### SQLFluff

SQLFluff is a SQL style and format checker.

The package
[documentation](https://docs.sqlfluff.com/en/stable/gettingstarted.html#basic-usage)
provides instructions on running it manually.

SQLFluff runs in two modes:
* Lint: Finds and warns about issues
* Fix: Certain lint issues can be fixed automatically. This mode updates your
  SQL files to apply those fixes.

### Code Coverage

To run the code coverage report locally, find the `py.test` command in
`script/dockerci` and run it the Docker shell. For more readable output,
include an additional option,
[`--cov-report html`](https://pytest-cov.readthedocs.io/en/latest/reporting.html).
This produces HTML output, which you can open locally in the browser. Unlike the
`term-missing` output, which simply lists files and line number ranges, HTML
output includes the entirety of each source file color coded by whether it was
covered by a test. Example command:

    py.test -v --cov-report term-missing --cov-report xml:coverage.xml \
        --cov-report html --cov=mcds_cookiecutter \
        --cov-config=tests/config/pytest_cov.cfg tests/

### `pytobash`

`pytobash` is invoked with the name of a Python module. It will load the Python
module and then echo module variables to standard output. `pytobash` output can be
passed to Bash's `source` built-in with process substitution. This will set
environment variables which can be used as parameters for other Bash scripts
(note: process substitution does not work in Bash on MacOS).

Usage:
```shell script
$ cat config/parameters.py
# Example config file
CONFIG_VAR = list(range(3))
$ pytobash config.parameters
CONFIG_VAR='[0, 1, 2]'
$ source <(pytobash config.parameters)
$ echo ${CONFIG_VAR}
[0, 1, 2]
```
