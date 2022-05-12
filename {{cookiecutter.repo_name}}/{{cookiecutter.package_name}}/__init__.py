import importlib.resources
from pathlib import Path

from . import resources


def get_resource_path(basename: str) -> Path:  # pragma: no cover
    """
    Returns a pathlib.Path of a resource file (e.g. machine-learning model file)
    embedded in the package in the {{cookiecutter.package_name}}/resources
    directory.

    >>> es_json: Path = get_resource_path('familiar_spanish.json')
    """
    with importlib.resources.path(resources, basename) as resource_path:
        # :TRICKY: The docs for this function
        # (https://docs.python.org/3.7/library/importlib.html?highlight=importlib#importlib.resources.path)
        # point out that it may return the path to a temporary file that is
        # deleted upon exiting the "with" block, but for packages built using
        # datascience-python-cookiecutter, it should always be the path of a
        # normal, long-lived file.
        return resource_path


def get_resource_directory(*subdirectories: str) -> Path:  # pragma: no cover
    """
    Returns the resources/ directory.

    If subdirectories are provided, returns the specified subdirectory path
    under resources/.

    >>> TORCH_HOME: Path = get_resource_directory()
    >>> COLA_TOKENIZER_PATH: Path = get_resource_directory(
        "offline_roberta_base_cola_tokenizer")

    >>> import os
    >>> os.environ['TORCH_HOME'] = str(TORCH_HOME)
    >>> os.environ['COLA_TOKENIZER_PATH'] = str(COLA_TOKENIZER_PATH)
    """
    return get_resource_path('__init__.py').parent.joinpath(*subdirectories)
