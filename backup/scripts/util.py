#!/usr/bin/env python
__author__ = "OBI"
__copyright__ = "Copyright 2021, DPV e.V."
__license__ = "MIT"

from datetime import datetime
import os

from docker import DockerContainer, DockerUtils
from logger import logger


def get_folder_size_in_bytes(path, container: DockerContainer):
    """disk usage in bytes"""
    cmd_folder_size = "du -s --bytes {}".format(path)
    result = DockerUtils.run_cmd(cmd=cmd_folder_size, container=container)
    return result.split()[0].decode('utf-8')


def get_folder_size_human(path, container: DockerContainer):
    """disk usage in human readable format (e.g. '2,1GB')"""
    cmd_folder_size = "du -sh {}".format(path)
    result = DockerUtils.run_cmd(cmd=cmd_folder_size, container=container)
    return result.split()[0].decode('utf-8')


def check_dir_exist(path, container: DockerContainer) -> bool:
    cmd = "ls -A {}/".format(path)
    try:
        DockerUtils.run_cmd(cmd=cmd, container=container)
        return True
    except:
        return False


def check_dir_empty(path, container: DockerContainer) -> bool:
    cmd = "ls -A {} | [ $(wc -c) -gt 0 ]".format(path)
    try:
        DockerUtils.run_cmd(cmd=cmd, container=container)
        return False
    except:
        return True


def check_file_exists(path, container: DockerContainer) -> bool:
    cmd = "test -f {}".format(path)
    try:
        DockerUtils.run_cmd(cmd=cmd, container=container)
        return True
    except:
        return False


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


def list_files(directory, extension):
    return (f for f in os.listdir(directory) if f.endswith('.' + extension))


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise RuntimeError('Boolean value expected.')


def timestamp_string() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
