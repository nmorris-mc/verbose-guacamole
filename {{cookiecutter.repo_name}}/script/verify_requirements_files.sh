#!/usr/bin/env bash
set -euo pipefail

# Are there any staged changes to the requirements/ directory?
requirements_dir_state=$(git diff --cached requirements/)
if [ ! -z "${requirements_dir_state}" ]
then
    # Yes. Verify the requirements files (i.e. that the .txt files are
    # consistent with the .in files).
    running_containers=$(docker-compose ps --quiet)
    if [ -z "${running_containers}" ]
    then
        echo "When you run \"git commit\" with changes to files in the"
        echo "requirements/ directory, cookiecutter needs to verify that you"
        echo "ran \"script/update_requirements.sh\" after changing the files,"
        echo "i.e. that the *.in and *.txt files are \"in sync\". This requires"
        echo "the Docker development container to be running. Please run"
        echo "\"script/setup-docker\" to start the container. Once you have"
        echo "done that, try running \"git commit\" again."
        exit 1
    else
        docker-compose exec -T --env PYENV_VERSION=cli_env app pip-compile-multi verify
    fi
fi
