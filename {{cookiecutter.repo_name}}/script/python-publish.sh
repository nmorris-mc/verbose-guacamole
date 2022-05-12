#!/bin/bash -l

set -e

cat <<EOF >~/.pypirc
[distutils]
index-servers = local
[local]
repository: https://artifactory.rsglab.com/artifactory/api/pypi/pypi
username: $ARTIFACTORY_USERNAME
password: $ARTIFACTORY_TOKEN
EOF

if [[ -z "$BUILD_NUMBER" ]]; then
  echo "Please don't push to artifactory from your local box. Rely on a build server!"
  exit 1
fi

script/build_package
twine_output=$(PYENV_VERSION=cli_env twine upload --skip-existing --repository local dist/*)
# Write outcome to file that will be read by Jenkinsfile.
if [[ $twine_output == *"because it appears to already exist" ]]; then
  echo "already_exists" > /run/.twine_output/twine-exit
else
  echo "published" > /run/.twine_output/twine-exit
fi
