#!/usr/bin/env bash

GCLOUD=~/google-cloud-sdk/bin/gcloud
if ! PYENV_VERSION=system ${GCLOUD} auth application-default print-access-token >/dev/null 2>&1
then
    # Run this command to authenticate with GCP. In some cases, several commands may
    # be needed because gcloud, Python, and Apache Beam authentication all work a
    # little differently. When it runs, this command stores credentials in a file
    # in the container: ~/.config/gcloud/application_default_credentials.json
    PYENV_VERSION=system ${GCLOUD} auth application-default login
fi

# Uncomment this section if you want the gcloud command-line to be authenticated.
# The similar line above only authenticates client *libraries*.
#if ! PYENV_VERSION=system ${GCLOUD} auth print-access-token >/dev/null 2>&1
#then
#    PYENV_VERSION=system ~/google-cloud-sdk/bin/gcloud auth login
#fi
