#!/usr/bin/env python
__author__ = "OBI"
__copyright__ = "Copyright 2021, DPV e.V."
__license__ = "MIT"

import subprocess
from enum import Enum

from logger import logger


class DockerContainer(Enum):
    BACKUP = 'keycloak_backup'
    LOCAL = 'localhost'


class DockerUtils:
    @staticmethod
    def run_cmd(cmd: str, container: DockerContainer) -> bool:
        if container == DockerContainer.LOCAL:
            command = cmd
        else:
            command = "docker exec -i {} bash -c '{}' ".format(container.value, cmd)

        logger.debug("Running command: {}".format(command))
        try:
            return subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as err:
            logger.error("Could not run command: {}. Exit code: {} Msg: {}".format(command, err.returncode, err.output))
            raise
