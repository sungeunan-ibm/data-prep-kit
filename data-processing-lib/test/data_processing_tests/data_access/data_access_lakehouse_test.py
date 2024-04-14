# (C) Copyright IBM Corp. 2024.
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import pytest
from data_processing.data_access import DataAccessLakeHouse
from data_processing.utils import DPLConfig


s3_cred = {
    # Running these tests requires the credentials to be provided in the env vars.
    "access_key": DPLConfig.S3_ACCESS_KEY,
    "secret_key": DPLConfig.S3_SECRET_KEY,
    "url": "https://s3.us-east.cloud-object-storage.appdomain.cloud",
}

# Configure lakehouse unit test tables
lakehouse_config = {
    "lh_environment": "STAGING",
    "input_table": "academic.ieee",
    "input_dataset": "",
    "input_version": "main",
    "output_table": "academic.ieee.lh_unittest",
    "output_path": "lh-test/tables/academic/ieee/lh_unittest",
    # Running these tests requires the credentials to be provided in the env vars.
    "token": DPLConfig.LAKEHOUSE_TOKEN,
}


@pytest.mark.skipif(
    DPLConfig.LAKEHOUSE_TOKEN is None, reason="LAKEHOUSE_TOKEN needs to be set, generally via env vars"
)
def test_table_read_write():
    """
    Testing table read/write
    :return: None
    """
    # create data access
    d_a = DataAccessLakeHouse(
        s3_credentials=s3_cred, lakehouse_config=lakehouse_config, d_sets=None, checkpoint=False, m_files=-1
    )

    input_location = (
        "lh-test/tables/academic/ieee/data/version=0.0.1/"
        "language=en/00000-1-345d10e3-ed3c-46b3-8f0d-cb81af19898b-00001.parquet"
    )
    # read the table
    r_table = d_a.get_table(path=input_location)
    r_columns = r_table.column_names
    print(f"number of columns in the read table {len(r_columns)}, number of rows {r_table.num_rows}")
    assert 6220 == r_table.num_rows
    assert 14 == len(r_columns)
    # get table output location
    output_location = d_a.get_output_location(input_location)
    print(f"Output location {output_location}")
    assert (
        "lh-test/tables/academic/ieee/lh_unittest/data/version=0.0.1/"
        "language=en/00000-1-345d10e3-ed3c-46b3-8f0d-cb81af19898b-00001.parquet" == output_location
    )
    # save the table
    l, result = d_a.save_table(path=output_location, table=r_table)
    print(f"length of saved table {l}, result {result}")
    assert 220549646 == l
    s_columns = d_a.get_table(output_location).column_names
    assert len(r_columns) == len(s_columns)
    assert r_columns == s_columns


@pytest.mark.skipif(
    DPLConfig.LAKEHOUSE_TOKEN is None, reason="LAKEHOUSE_TOKEN needs to be set, generally via env vars"
)
def test_get_folder():
    """
    Testing get folder
    :return: None
    """
    # create data access
    d_a = DataAccessLakeHouse(
        s3_credentials=s3_cred, lakehouse_config=lakehouse_config, d_sets=None, checkpoint=False, m_files=-1
    )
    # get the folder
    files = d_a.get_files_to_process()
    print(f"got {len(files[0])} files to process with checkpoint False")
    assert 14 == len(files[0])


@pytest.mark.skipif(
    DPLConfig.LAKEHOUSE_TOKEN is None, reason="LAKEHOUSE_TOKEN needs to be set, generally via env vars"
)
def test_get_todo_list():
    """
    Testing get todo list by setting checkpoint to True
    : return: None
    """
    # create data access
    d_a = DataAccessLakeHouse(
        s3_credentials=s3_cred, lakehouse_config=lakehouse_config, d_sets=None, checkpoint=True, m_files=-1
    )

    print(f"got {len(d_a.get_files_to_process()[0])} files to process with checkpoint True")
    assert 12 == len(d_a.get_files_to_process()[0])


@pytest.mark.skipif(
    DPLConfig.LAKEHOUSE_TOKEN is None, reason="LAKEHOUSE_TOKEN needs to be set, generally via env vars"
)
def test_files_to_process():
    """
    Testing get files to process
    :return: None
    """
    # create data access
    path_conf = {
        "input_folder": "lh-test/tables/academic/ieee/data/version=0.0.1/language=en/",
        "output_folder": "lh-test/tables/academic/ieee/lh_unittest/data/version=0.0.1/language=en/",
    }
    # get files to process with checkpoint set to False
    d_a = DataAccessLakeHouse(
        s3_credentials=s3_cred, lakehouse_config=lakehouse_config, d_sets=None, checkpoint=False, m_files=-1
    )
    files, profile = d_a.get_files_to_process()
    print(f"files with checkpointing set to False {len(files)}, profile {profile}")
    assert 14 == len(files)
    assert 344.0891418457031 == profile["max_file_size"]
    assert 0.00907135009765625 == profile["min_file_size"]
    assert 1794.700538635254 == profile["total_file_size"]

    # use checkpoint
    d_a = DataAccessLakeHouse(
        s3_credentials=s3_cred, lakehouse_config=lakehouse_config, d_sets=None, checkpoint=True, m_files=-1
    )
    files, profile = d_a.get_files_to_process()
    print(f"files with checkpointing set to True {len(files)}, profile {profile}")
    assert 12 == len(files)
    assert 344.0891418457031 == profile["max_file_size"]
    assert 0.00907135009765625 == profile["min_file_size"]
    assert 1463.8405895233154 == profile["total_file_size"]

    # using data sets
    lakehouse_config["input_table"] = "bluepile.academic.doabooks"
    lakehouse_config["input_dataset"] = "doabooks"
    d_a = DataAccessLakeHouse(
        s3_credentials=s3_cred, lakehouse_config=lakehouse_config, d_sets=["doabooks"], checkpoint=False, m_files=-1
    )
    files, profile = d_a.get_files_to_process()
    print(f"using data sets files {len(files)}, profile {profile}")
    assert 26 == len(files)
    assert 666.0280637741089 == profile["max_file_size"]
    assert 0.05837726593017578 == profile["min_file_size"]
    assert 1439.3532075881958 == profile["total_file_size"]
    # using data sets with checkpointing
    d_a = DataAccessLakeHouse(
        s3_credentials=s3_cred, lakehouse_config=lakehouse_config, d_sets=["doabooks"], checkpoint=True, m_files=-1
    )
    files, profile = d_a.get_files_to_process()
    print(f"using data sets files {len(files)}, profile {profile}")
    assert 26 == len(files)
    assert 666.0280637741089 == profile["max_file_size"]
    assert 0.05837726593017578 == profile["min_file_size"]
    assert 1439.3532075881958 == profile["total_file_size"]


if __name__ == "__main__":
    test_table_read_write()
    test_get_folder()
    test_get_todo_list()
    test_files_to_process()
