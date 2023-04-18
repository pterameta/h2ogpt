import shutil

import pandas as pd
import os

import huggingface_hub
import pytest
from datasets import load_dataset


@pytest.mark.parametrize(
    "dataset_name, link_to_source",
    [
        (
                "openassistant_oasst1",
                """
- [original OpenAssistant data in tree structure](https://huggingface.co/datasets/OpenAssistant/oasst1)
- [flattened version created by h2oGPT repository](https://github.com/h2oai/h2ogpt/blob/45e6183171fb16691ad7d3ab006fad973f971e98/create_data.py#L1253)
"""
        ),
         (
                 "h2ogpt-oig-oasst1-instruct-cleaned-v1",
                 """
- [original OpenAssistant data in tree structure](https://huggingface.co/datasets/OpenAssistant/oasst1)
- [flattened version created by h2oGPT repository](https://github.com/h2oai/h2ogpt/blob/45e6183171fb16691ad7d3ab006fad973f971e98/create_data.py#L1253)
"""
         ),
    ],
)
def test_create_data_cards(dataset_name, link_to_source):
    assert os.path.exists("README-template.md"), "must be running this test from the data dir."
    shutil.rmtree(dataset_name, ignore_errors=True)
    try:
        repo = huggingface_hub.Repository(
            local_dir=dataset_name,
            clone_from="h2oai/%s" % dataset_name,
            repo_type="dataset",
            skip_lfs_files=True,
            token=True,
        )
        repo.git_pull()
    except Exception as e:
        print(str(e))
        print("call 'huggingface_cli login' first and provide access token with write permission")
    dataset = load_dataset("h2oai/%s" % dataset_name)["train"]

    pd.set_option('display.max_columns', None)
    with open("README-template.md", "r") as f:
        content = f.read()
        assert "<<DATASET_NAME>>" in content
        content = content.replace("<<DATASET_NAME>>", dataset_name)

        assert "<<NROWS>>" in content
        content = content.replace("<<NROWS>>", str(dataset.num_rows))

        assert "<<NCOLS>>" in content
        content = content.replace("<<NCOLS>>", str(dataset.num_columns))

        assert "<<COLNAMES>>" in content
        content = content.replace("<<COLNAMES>>", str(dataset.column_names))

        assert "<<PREVIEW>>" in content
        content = content.replace("<<PREVIEW>>", str(dataset.to_pandas().iloc[:3, :]))

        assert "<<SOURCE_LINK>>" in content
        content = content.replace("<<SOURCE_LINK>>", link_to_source)

        assert "<<" not in content
        assert ">>" not in content

    with open(os.path.join(dataset_name, "README.md"), "w") as f:
        f.write(content)
    try:
        repo.commit("Update README.md")
        repo.push_to_hub()
    except Exception as e:
        print(str(e))