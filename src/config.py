import logging
from os import environ
from pathlib import Path

# Application Constants
INPUT_PATH = Path(environ.get("UP42_INPUT_PATH", "/tmp/input"))
OUTPUT_PATH = Path(environ.get("UP42_OUTPUT_PATH", "/tmp/output"))
QUICKLOOK_PATH = Path(environ.get("UP42_QUICKLOOK_PATH", "/tmp/quicklook"))
INPUT_METADATA_PATH = INPUT_PATH / "data.json"
OUTPUT_METADATA_PATH = OUTPUT_PATH / "data.json"
RULESET_PATH = Path(__file__).resolve().parents[1] / "ruleset/ruleset.dcp"

# LOGGER_CONFIG
LOGGER_CONFIG = {
    "version": 1,
    "formatter": {
        "simple": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    "handler": {
        "console": {
            "class": logging.StreamHandler,
            "formatter": "simple",
            "level": logging.INFO,
        }
    },
}
