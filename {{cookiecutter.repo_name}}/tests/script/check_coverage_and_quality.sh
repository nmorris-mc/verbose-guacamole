#!/usr/bin/env bash
set -euo pipefail

# This script uses CLI tools and doesn't run any "regular" code, so we can use
# the CLI environment throughout.
export PYENV_VERSION=cli_env

COVERAGE_FILE=${1:-~/src/coverage.xml}
BASE_DIR=$(dirname ${COVERAGE_FILE})

cd ${BASE_DIR}

if [ ! -f ~/.config/flake8 ]
then
    mkdir -p ~/.config
    cp tests/config/flake8 ~/.config
fi
diff-quality --compare-branch main --violations=flake8 --fail-under=90

if [[ (! -f ~/.pylintrc) || "~/.pylintrc" -ot "tests/config/pylintrc" ]]
then
    cp --backup=numbered tests/config/pylintrc ~/.pylintrc
fi

# :HACK: Pylint complains about some patterns that in tests seem okay:
# - Lack of doc strings
# - Unused function parameters (py.test uses these for fixtures)
#
# Because of the way diff-quality runs pylint (i.e. a separate invocation for
# each source file), pylint does not respect the"ignore" and "ignore-patterns"
# settings. Here we temporarily patch the pylint script to ignore files in
# tests/ and integration_tests. Ugh.
cp $(pyenv which pylint) /tmp/pylint.bak
sed '/if __name__/a\ \ \ \ import os, re; sys.exit(0) if len(sys.argv) == 3 and os.path.exists(sys.argv[2]) and re.search(r"^(tests|integration_tests)", sys.argv[2]) else None' /tmp/pylint.bak > $(pyenv which pylint)
diff-quality --compare-branch main --violations=pylint --fail-under=90
cp /tmp/pylint.bak $(pyenv which pylint)
rm /tmp/pylint.bak

# :TRICKY: The '|| true' keeps it from failing if egrep finds no matches.
git diff --name-only main... | (egrep '\.py$' || true) | xargs --max-args 1 $(pyenv which python) tests/script/check_complexity.py

# Some data jobs (especially early prototypes) don't have any Python code, so
# no coverage file is generated. In this case, simply skip the coverage check,
# because it would fail anyway ("file not found").
if [[ -f "${COVERAGE_FILE}" ]]
then

    # BWH :TRICKY 2021-01-24 The coverage.xml produced when testing a package
    # uses relative paths starting from the package root. This is a workaround.
    # Ideally, the coverage file would use either absolute paths or paths
    # relative to the current directory, but haven't gotten that to work yet.
    pushd {{cookiecutter.package_name}}

    diff-cover --compare-branch main ${COVERAGE_FILE} --fail-under=90

    popd

fi

if [ -d "sql" ]
then
    # Run the SQL linter, but do not allow it to make builds fail.
    echo "SQL Quality Report"

    set +e
    diff-quality --compare-branch main --violations sqlfluff
    OUTPUT=$(sqlfluff lint --dialect bigquery sql 2>&1)
    RESULT=$?
    set -e
    echo "$OUTPUT"
    if [ $RESULT != 0 ]
    then
        echo "SQL check failed"
    else
        echo "SQL check complete"
    fi
fi
