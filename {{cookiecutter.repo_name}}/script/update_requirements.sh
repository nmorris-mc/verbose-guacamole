#!/usr/bin/env bash

source script/helpers

set -e
docker_environment_check

truncate -s 0 requirements/*.txt && PYENV_VERSION=cli_env pip-compile-multi --directory requirements/

log "Please exit this Docker container, run script/setup-docker, and run script/shell-docker to load the updated requirements."
