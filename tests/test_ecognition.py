import shutil
import json
import mock

import pytest
import geojson


def test_initialize_directories(ecognition, root_path):
    paths = [root_path / "test_dir_1", root_path / "test_dir_1"]
    try:
        ecognition.initialize_directories(paths)
        for path in paths:
            assert path.exists()
    finally:
        for path in paths:
            if path.exists():
                shutil.rmtree(path)


@pytest.mark.parametrize(
    "input_environ, output_param",
    [
        ({"UP42_TASK_PARAMETERS": json.dumps({"parameter": 1})}, {"parameter": 1}),
        ({"UP42_TASK_PARAMETERS": json.dumps({})}, {}),
        ({"UP42_TASK_PARAMETERS": ""}, {}),
        ({}, {}),
    ],
)
def test_load_params(ecognition, input_environ, output_param):
    parameters = ecognition.load_params(input_environ)
    assert parameters == output_param


@pytest.mark.parametrize(
    "metadata_path,num_features",
    [("mock_data/data.json", 1), ("mock_data/nodata.json", 0)],
)
def test_metadata(ecognition, root_path, metadata_path, num_features):
    metadata = ecognition.load_metadata(root_path / metadata_path)
    assert len(metadata.features) == num_features


def test_create_metadata_copy(ecognition, root_path):
    with open(root_path / "mock_data/data.json", encoding='utf-8') as f:
        metadata = geojson.load(f)
        feature = metadata.features[0]
        out_feature = ecognition.create_metadata_copy(
            feature, {"test_key": "test_value"}
        )
        assert feature.bbox == out_feature.bbox
        assert feature.geometry == out_feature.geometry
        assert "test_key" in out_feature.properties
        assert out_feature.properties["test_key"] == "test_value"


def test_save_metadata(ecognition, root_path):
    with open(root_path / "mock_data/data.json", encoding='utf-8') as f:
        output_metadata_path = root_path / "mock_data/output_data.json"
        try:
            metadata = geojson.load(f)
            ecognition.save_metadata(output_metadata_path, metadata)
            assert output_metadata_path.exists()
        finally:
            if output_metadata_path.exists():
                output_metadata_path.unlink()


def test_construct_ecognition_cmd(ecognition, ruleset_path):
    cmd = ecognition.build_ecognition_cmd(
        ruleset_path=str(ruleset_path),
        input_product_path="abc/defg",
        output_path="/tmp/output",
        ruleset_parameters={},
    )
    assert cmd == [
        "./DIACmdEngine",
        "image=abc/defg",
        f"ruleset={str(ruleset_path)}",
        "--output-dir=/tmp/output",
    ]


def test_construct_ecognition_cmd_with_params(ecognition, output_path, ruleset_path):
    cmd = ecognition.build_ecognition_cmd(
        ruleset_path=str(ruleset_path),
        input_product_path="abc/defg",
        output_path=str(output_path),
        ruleset_parameters={"ruleset_param1": 5},
    )
    assert cmd == [
        "./DIACmdEngine",
        "image=abc/defg",
        f"ruleset={str(ruleset_path)}",
        f"--output-dir={str(output_path)}",
        "param:ruleset_param1=5",
    ]


def test_run_ecognition_unsuccessful(ecognition, output_path, ruleset_path):
    with pytest.raises(RuntimeError) as e:
        ecognition.run_ecognition(
            cmd=[
                "./DIACmdEngine",
                "image=abc/defg",
                f"ruleset={str(ruleset_path)}",
                f"--output-dir={output_path}",
            ]
        )
    assert e.type == RuntimeError
    assert str(e.value) == "eCognition run failed with exception: [Errno 2] No such file or directory: './DIACmdEngine'"

# pylint: disable=too-many-arguments,unused-argument
@mock.patch("subprocess.run")
def test_process(
    mock_subproc_run,
    test_ready_env,
    ecognition,
    root_path,
    input_path,
    output_path,
    ruleset_path,
):
    with open(root_path / "mock_data/data.json", encoding='utf-8') as fp:
        data = geojson.load(fp)
        for feature in data.features:
            rel_data_path = feature.properties["up42.data_path"]
            full_data_path = input_path / rel_data_path
            full_data_path.parent.mkdir(exist_ok=True)
            full_data_path.touch()
        mock_subproc_run.return_value = mock.Mock(
            communicate=("ouput", "error"), returncode=0
        )
        _ = ecognition.process(
            parameters=dict(
                input=input_path,
                output=output_path,
                ruleset_path=ruleset_path,
                block_parameters={},
            ),
            input_fc=data,
        )
        out_dir = output_path / "3159422e-6c53-4d97-9186-f52626f56b00"
        assert out_dir.exists()
        assert out_dir.is_dir()

def test_process_missing_parameters(ecognition):
    with pytest.raises(ValueError) as e:
        _ = ecognition.process(
            parameters=dict(
                output="output", ruleset_path="ruleset"
            ),
            input_fc=None,
        )
    assert str(e.value) == "Missing parameter: input"

# pylint: disable=too-many-arguments
@mock.patch("subprocess.run")
def test_run_mock_ecognition(
    mock_subproc_run, run_main, root_path, input_path, output_path
):
    # Prepare input
    fp_data = root_path / "mock_data/data.json"
    shutil.copy(str(fp_data), input_path)

    with open(fp_data, encoding='utf-8') as f:
        data = geojson.load(f)
        for feature in data.features:
            rel_data_path = feature.properties["up42.data_path"]
            full_data_path = input_path / rel_data_path
            full_data_path.parent.mkdir(exist_ok=True)
            full_data_path.touch()

    mock_subproc_run.return_value = mock.Mock(
        communicate=("ouput", "error"), returncode=0
    )

    run_main()

    out_dir = output_path / "3159422e-6c53-4d97-9186-f52626f56b00"
    assert out_dir.exists()
    assert out_dir.is_dir()
    out_data_json = output_path / "data.json"
    assert out_data_json.exists()
    assert out_data_json.is_file()