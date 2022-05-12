import datetime
import os
import hashlib
import base64

from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError

# When using rsg/datascience-python-cookiecutter to start a project:
# set the names of the GCP Project and Bucket you're using below.
# This is the project name and the bucket name
GCP_PROJECT = ""
GCP_BUCKET = ""

SRC_FOLDER = "models/"
DST_FOLDER = 'resources'

PACKAGE_NAME = "{{cookiecutter.package_name}}"


def set_file_last_modified(file_path, dt):
    """Sets file_path modification date/time."""
    dt_epoch = dt.timestamp()
    os.utime(file_path, (dt_epoch, dt_epoch))


def download_package_data():
    """Repo-specific function to download package data.

    For example, download a model file from GCS.
    """
    # When using rsg/datascience-python-cookiecutter to start a project:
    # You can remove the block below as part of setting up this script.
    if not GCP_PROJECT:
        print('download_package_data.py: No GCP Project specified, nothing to do.')
        return
    try:
        print('Downloading model files')

        # Since this gets run when we call script/publish, the person calling
        # this should have permissions to read from this GCS bucket.
        client = storage.Client(project=GCP_PROJECT)
        bucket = client.get_bucket(GCP_BUCKET)
        blobs = client.list_blobs(bucket, prefix=SRC_FOLDER)

        # Download the models.
        now = datetime.datetime.now()
        for blob in blobs:
            if blob.name != SRC_FOLDER:
                target_path = os.path.join(
                    PACKAGE_NAME,
                    DST_FOLDER,
                    os.path.basename(blob.name))

                if os.path.exists(target_path) and (blob.md5_hash == md5(target_path)):
                    # This scenario is most likely to occur during local testing.
                    print(f"The file at {target_path} already exists. Skipping download.")
                    continue

                print(f'\nDownloading file {blob.name} to {target_path}')
                blob.download_to_filename(target_path)

                # This is not required, but otherwise, the "modified" date/time
                # on the file reflects the last-modified date/time in GCS.
                # Setting it to "now" makes it easier to know when the download
                # ran and that it worked correctly.
                set_file_last_modified(target_path, now)

                # Verify that the file download was not corrupted
                md5_checksum = md5(target_path)
                if blob.md5_hash == md5_checksum:
                    print(f'Verified that {blob.name} was downloaded successfully to {target_path}. '
                          f'\nMD5 checksums are both {blob.md5_hash}')
                else:
                    error_text = f'ERROR: {blob.name} downloaded to {target_path} appears to be corrupted. ' \
                                 f'GCS MD5: {blob.md5_hash}, calculated MD5: {md5_checksum}.'
                    print(error_text)
                    raise Exception(error_text)
    except DefaultCredentialsError:
        # This happens during Docker builds of the dev image. In both dev
        # and Jenkins, we have subsequent steps (script/devenv and
        # script/dockerci) which run "python setup.py develop again in order
        # to ensure the model files are downloaded.
        print('ERROR: Model files not downloaded')
        raise


def md5(model_file):
    """
    A helper function to calculate the MD5 for a model file.
    :param model_file: a string file name for a model file
    :return: string MD5 hash in base64 encoding
    """
    hash_md5 = hashlib.md5()
    with open(model_file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    # GCS gives us their checksum in base64, so we have to convert it
    base64_md5_bytes = base64.b64encode(hash_md5.digest())
    return base64_md5_bytes.decode('utf-8')


if __name__ == '__main__':
    download_package_data()
