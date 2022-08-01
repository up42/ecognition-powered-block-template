import json
import subprocess
from pathlib import Path
from typing import List

import geojson
from geojson import Feature, FeatureCollection


def initialize_directories(dirs: List[Path]) -> None:
    """Creates directory if they don't exist.

    Args:
        dirs (List[Path]): List of paths to the directories
    """
    for path in dirs:
        path.mkdir(parents=True, exist_ok=True)


def load_params(environment_dict: dict) -> dict:
    """Get the parameters for the current task directly from the task
    parameters parameters in `UP42_TASK_PARAMETERS` environment variable.

    Args:
        environment_dict (dict): Environment dictionary

    Returns:
        dict: Dictionary with task parameters
    """
    data: str = environment_dict.get("UP42_TASK_PARAMETERS", "{}")
    if data == "":
        data = "{}"
    return json.loads(data)


def load_metadata(metadata_path: Path) -> FeatureCollection:
    """At UP42 metadata context are passed from one block to other as geojson
    with feature collection. This function helps to load this metadata.

    Args:
        metadata_path (Path): Path to the metadata

    Returns:
        FeatureCollection: FeatureCollection with the metadata
    """
    if not metadata_path.exists():
        return FeatureCollection([])
    with open(metadata_path, encoding="utf-8") as fp:
        return geojson.load(fp)


def create_metadata_copy(feature: Feature, properties: dict) -> Feature:
    """Creates a new copy of single feature of metadata with additional properties.

    Args:
        feature (Feature): Input feature
        properties (dict): Properties to be added

    Returns:
        Feature: Copy of metadata as Feature
    """
    out_properties = {
        k: v
        for k, v in feature.properties.items()
        if not (k.startswith("up42.") or k.startswith("custom."))
    }
    out_properties.update(properties)
    return Feature(
        geometry=feature.geometry, bbox=feature.bbox, properties=out_properties
    )


def save_metadata(output_path: Path, result: FeatureCollection) -> None:
    """Save metadata FeatureCollection to a geojson file

    Args:
        output_path (Path): Output path for the metadata geojson
        result (FeatureCollection): Metadata of output as FeatureCollection
    """
    with open(output_path, "w", encoding="utf-8") as fp:
        geojson.dump(result, fp, indent=4)


def build_ecognition_cmd(
    ruleset_path: Path,
    input_product_path: Path,
    output_path: Path,
    ruleset_parameters: dict,
) -> List[str]:
    """Builds ecognition command

    Args:
        ruleset_path (Path): Path to the ruleset to be executed
        input_product_path (Path): Path to the input product
        output_path (Path): Path to the output folder
        ruleset_parameters (dict): Parameters expected by the ruleset

    Returns:
        List[str]: Subprocess command
    """
    ecognition_cmd = [
        "./DIACmdEngine",
        f"image={str(input_product_path)}",
        f"ruleset={str(ruleset_path)}",
        f"--output-dir={str(output_path)}",
    ]
    for key, value in ruleset_parameters.items():
        ecognition_cmd.append(f"param:{key}={value}")
    return ecognition_cmd


def run_ecognition(cmd: List[str]) -> None:
    """Run the ecognition command as a subprocess.

    Args:
        cmd(List[str]): The ecognition subprocess command string.
    """

    # Disable check to get return code
    # pylint: disable=subprocess-run-check
    try:
        completed_process = subprocess.run(cmd)
        if completed_process.returncode != 0:
            raise RuntimeError(
                f"eCognition run failed with error code {completed_process.returncode}"
            )
    except BaseException as exp:
        raise RuntimeError(f"eCognition run failed with exception: {exp}") from exp


def process(parameters: dict, input_fc: FeatureCollection) -> FeatureCollection:
    """Given a feature collection describing the input datasets, runs the ecognition
    processing on each input dataset and creates an output feature collection.

    Args:
        parameters (dict): Dictionary with parameters required to proccess eg.
            ```
            {
                "input": "INPUT_PATH",
                "output": "OUTPUT_PATH",
                "ruleset_path": "RULESET_PATH",
                "block_parameter": {}
            }
            ```
        input_fc (FeatureCollection): A GeoJSON FeatureCollection describing all input datasets

    Returns:
        FeatureCollection: A GeoJSON FeatureCollection describing all output datasets
    """
    try:
        input_path = Path(parameters.pop("input"))
        output_path = Path(parameters.pop("output"))
        ruleset_path = Path(parameters.pop("ruleset_path"))
        ruleset_parameters = parameters.pop("block_parameters", {})
    except KeyError as exp:
        raise ValueError(f"Missing parameter: {exp.args[0]}") from exp

    if not ruleset_path.exists():
        raise RuntimeError("No ruleset to execute")

    results: List[Feature] = []
    for in_feature in input_fc.features:
        # Resolve input product
        in_feature_path = input_path / in_feature.properties["up42.data_path"]
        if not in_feature_path.exists():
            raise ValueError(f"No product found at {str(in_feature_path)}")

        # Prepare output directory
        out_feature_path = output_path / in_feature_path.relative_to(input_path)
        if not out_feature_path.parent.exists():
            out_feature_path.mkdir(parents=True, exist_ok=True)

        # Build eCognition command
        cmd = build_ecognition_cmd(
            ruleset_path=ruleset_path,
            input_product_path=in_feature_path,
            ruleset_parameters=ruleset_parameters,
            output_path=output_path,
        )

        # Run eCognition command
        run_ecognition(cmd)

        # Prepare and return output metadata
        out_feature = create_metadata_copy(
            in_feature,
            properties={
                "up42.data_path": str(out_feature_path.relative_to(output_path))
            },
        )
        results.append(out_feature)
    return FeatureCollection(results)
