#!/usr/bin/env bash
set -euo pipefail

git checkout main
git pull origin main

script/nuke-docker
rm requirements/*.txt && touch requirements/dev_requirements.txt requirements/requirements.txt

# Work around issue where "docker build" can't pull images from an authenticated
# image repository like Artifactory but "docker pull" can.
cat Dockerfile | sed -n 's/^FROM[[:space:]][[:space:]]*\(.*\)/\1/p' | xargs docker pull
docker-compose build
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Generate updated pip requirements files.
docker-compose exec app script/update_requirements.sh
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v --remove-orphans

# Create branch, commit changes, and create pull request.
BRANCH=${USER}-update_python_packages_$(date '+%Y_%m_%d')
# :TRICKY: The '|| true' ignores errors if the branch did not exist.
git push origin --delete ${BRANCH} || true
git checkout -b ${BRANCH}
git add requirements/*.txt
# Idea: Inspect the library differences -- is it just patch versions, or are
# there minor or major version changes as well? Include this info in the PR
# comment to guide reviewers how much review/testing is required.
git commit -m "Update Python packages"
git push origin ${BRANCH}
hub pull-request -m "Update Python packages" -m "Created by script/pip_upgrade.sh"
