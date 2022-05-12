#!/usr/bin/env bash

# Create a Docker Compose config file which makes the Google credentials file
# available via a directory mount, as well as discoverable via an environment
# variable. Note that parts of the file are set dynamically based on
# $GOOGLE_APPLICATION_CREDENTIALS, which was set in Jenkinsfile.

# Copy the JSON secrets file as provided by Jenkins into the local secrets/
# directory. This ensures the file is owned by the user the build runs as,
# rather than a special Jenkins user. This addresses some tricky file ownership
# UID issues.
touch secrets/google_application_credentials.json
cp $GOOGLE_APPLICATION_CREDENTIALS secrets/google_application_credentials.json

cat <<EOF >docker-compose.jenkins.yml
version: "2"

services:
  app:
    volumes:
      - $(pwd)/secrets:/run/secrets
      - $(pwd)/.twine_output:/run/.twine_output
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/google_application_credentials.json
      - HOST_USER=ciuser
EOF
# Tell Docker not to include the Google credentials file in the Docker image.
# This wouldn't break anything, but it's a security no-no.
echo $(basename $GOOGLE_APPLICATION_CREDENTIALS) >> .dockerignore
