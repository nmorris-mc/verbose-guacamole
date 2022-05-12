import datetime
import os
import pytest


@pytest.fixture
def gcp_project_config_info():
    # TODO: remove the comments starting with TODO before merging!

    # TODO: put your DEV GCP project here. This is the project that tests will be run against.
    gcp_project = "YOUR DEV GCP PROJECT NAME GOES HERE"

    # TODO: in many cases, you'll be querying from a dataset that is named based on the current date
    # TODO: and/or user. This gets defined in the run_job.sh file. Specify the dataset name here
    # TODO: so you can reference it in your test.
    # TODO: Note that this code does NOT include the Git branch name. This is tricky to do in Python.
    # TODO: The easiest way to solve this problem is to remove the branch name reference in run_job.sh.
    today = datetime.date.today().strftime('%Y_%m_%d')
    host_user = os.environ.get('HOST_USER')
    dataset = f"dataset-name-{today}-{host_user}"

    # TODO: many integration tests will define a fixed date range so that the test results will
    # TODO: be consistent across different runs. This is optional but recommended.
    # TODO: you should change the below dates to fit your use case.
    start_date = "2018-01-01"
    end_date = "2020-01-01"

    return {
        'gcp_project': gcp_project,
        'dataset': dataset,
        'start_date': start_date,
        'end_date': end_date
    }
