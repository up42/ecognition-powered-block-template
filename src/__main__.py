import logging
import logging.config
from os import environ

import ecognition
import config

logging.config.dictConfig(config.LOGGER_CONFIG)
logger = logging.getLogger("EcognitionBlock")

try:
    logger.info("Initializing block")
    ecognition.initialize_directories(
        [config.INPUT_PATH, config.OUTPUT_PATH, config.QUICKLOOK_PATH]
    )

    block_parameters = ecognition.load_params(environ)
    logger.info(f"Blocks parameters retrieved: {block_parameters}")

    result = ecognition.process(
        parameters=dict(
            input=config.INPUT_PATH,
            output=config.OUTPUT_PATH,
            ruleset_path=config.RULESET_PATH,
            block_parameters=block_parameters,
        ),
        input_fc=ecognition.load_metadata(config.INPUT_METADATA_PATH),
    )
    ecognition.save_metadata(config.OUTPUT_METADATA_PATH, result)
    logger.info("Metadata saved")
except BaseException as exp:
    logger.info(f"Processing failed with an exception {exp}", exc_info=True)
    raise exp
