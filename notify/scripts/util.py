#!/usr/bin/env python
__author__ = "OBI"
__copyright__ = "Copyright 2021, DPV e.V."
__license__ = "MIT"

import re
import os

from logger import logger


def format_url(url: str):
    if not re.match('(?:http|ftp|https)://', url):
        return 'https://{}'.format(url)
    return url


def init_params(params: dict):
    """
    Check if env variables are exported and update params
    """
    for key, value in params.items():
        if key in os.environ:
            if type(value) is not bool:
                params[key] = type(value)(os.environ.get(key))
            else:
                params[key] = str2bool(os.environ.get(key))

        if not params[key]:
            logger.warn("Key: {} not set.".format(key))

    # Print params
    for key, value in params.items():
        logger.info('ENV: %-20s = %s', key, value)


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise RuntimeError('Boolean value expected.')
