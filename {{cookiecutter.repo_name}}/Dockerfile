# syntax = docker/dockerfile:experimental
# The "syntax =" comment above is a special Docker comment that enables a set
# of features known as "BuildKit". This comment, along with a couple of
# environment variables set in script/setup-docker, enables use of special
# Docker build features, including a cache feature we use to speed up Python
# package download and installation.
# https://docs.docker.com/develop/develop-images/build_enhancements/#overriding-default-frontends

# When using rsg/datascience-python-cookiecutter to start a project:
# If this project might be used in the Data Service Fabric, consider using
# the data-service-runtime docker image instead, as seen in the FROM line in python-echo-model's Dockerfile:
# https://git.rsglab.com/rsg/dsf-runtime-services/blob/main/python-echo-model/Dockerfile

FROM dockerfactory.rsglab.com/rsg/datascience:cuda-10.2-ae90b96

# When using rsg/datascience-python-cookiecutter to start a project:
# It's fine to modify these version numbers, but it is recommended to keep them
# pinned to *something* in order to avoid unpleasant surprises.
# TRICKY: Use names ending in "VER", not "VERSION", because those names affect
# pyenv and can break things in confusing ways.
# :TRICKY: I've seen cases where newer versions of these files break
# pip-compile-multi, the tool we use for package version management. If you
# change these, make sure to test!
ENV PIP_VER==22.0.4
ENV SETUPTOOLS_VER==62.1.0

WORKDIR ${USER_HOME}
# NOTE: Setting a variable in .profile does not make that variable available
# in "docker run" unless the command being run explicitly sources .profile.
# IS_PROD is 1 (True) by default. docker-compose.yml sets IS_PROD to 0 for
# development and CI environments.
RUN echo 'export IS_PROD=1' >> .profile

# If you need to install additional system packages, add them here.
RUN apt-get update --fix-missing -y && \
    apt-get install -y \
      moreutils \
      vim


# Installs the gcloud SDK, giving you command-line tools like gcloud and bq for
# inspecting and administering GCP stuff.
# https://cloud.google.com/sdk/gcloud/
# https://cloud.google.com/bigquery/docs/bq-command-line-tool
# We install from a .tar.gz rather than using "apt-get", because for some reason,
# the apt-get repo installation does not support later installing the App Engine
# SDK (possibly other unknown issues as well).
# :TRICKY: Set up a special ".python-version" to ensure gcloud does not use a
# virtualenv. gcloud launches the Python interpreter with the "-S" option, which
# breaks pyenv virtualenvs.
USER ${USERNAME}
RUN curl https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-365.0.0-linux-x86_64.tar.gz | tar xvz \
    && ./google-cloud-sdk/install.sh --quiet \
    && echo "source ${USER_HOME}/google-cloud-sdk/path.bash.inc" >> ${USER_HOME}/.profile \
    && echo ${PYTHON_3_7_VERSION} > ${USER_HOME}/google-cloud-sdk/.python-version
# Switch back to root so subsequent commands work, e.g. virtualenv, pip install.
USER root


# If you need a different Python version than is available in the Data Science
# Python base image, you can install it as follows:
#ENV MY_PYTHON_3_VERSION=3.9.1
#RUN PYENV_VER=system PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install ${MY_PYTHON_3_VERSION}

ENV PYVERSION=3.9.1

# Create a separate virtualenv for CLI tools
RUN PYENV_VERSION=system pyenv virtualenv "${PYVERSION}" "cli_env"


# Library project: Create and use a virtualenv
RUN PYENV_VERSION=system pyenv virtualenv "${PYVERSION}" "{{cookiecutter.package_name}}-${PYVERSION}"
RUN PYENV_VERSION="{{cookiecutter.package_name}}-${PYVERSION}" pip install --upgrade pip==${PIP_VER} setuptools==${SETUPTOOLS_VER}
RUN pyenv local "{{cookiecutter.package_name}}-${PYVERSION}"



# When using rsg/datascience-python-cookiecutter to start a project:
# The COPY commands below set up the container for two use cases:
# 1. Production
# 2. Jenkins build/test
# The COPY commands don't matter in development because we mount the host
# source directory to ${USER_HOME}/src, hiding these COPY-ed files. If you
# create additional files or directories required for production or Jenkins, you
# may need additional "COPY" commands. Where practical, avoid this need by
# placing required files in the existing, cookiecutter-provided directories.
WORKDIR ${USER_HOME}/src

# Copy requirements files explicitly
COPY requirements/ requirements/

RUN chown -R ${USERNAME}: ${USER_HOME}/src/requirements

# Install CLI tools
RUN PYENV_VERSION="cli_env" pip install -r requirements/cli_requirements.txt
RUN chown -R ${USERNAME}: $(readlink $(dirname $(dirname $(PYENV_VERSION=cli_env pyenv which python))))

# Installing both requirements files with one `pip install` command will verify
# that the files specify consistent library versions.
RUN pip install -r requirements/dev_requirements.txt -r requirements/requirements.txt

# Copy package config files explicitly
COPY setup.py .
COPY MANIFEST.in .
COPY setup.cfg .
COPY pyproject.toml .
RUN pip install -e .

RUN chown -R ${USERNAME}: $(readlink $(dirname $(dirname $(pyenv which python))))


RUN chown -R "${USERNAME}:" "${PYENV_ROOT}/shims"

COPY . .
RUN mkdir -p ${USER_HOME}/.config
RUN chown -R ${USERNAME}: ${USER_HOME}

# Set up sitecustomize.py. This enables coverage tracking in subprocesses.
COPY tests/config/sitecustomize.py /usr/local/pyenv/versions/${PYVERSION}/
RUN chown root:root /usr/local/pyenv/versions/${PYVERSION}/sitecustomize.py

USER ${USERNAME}
