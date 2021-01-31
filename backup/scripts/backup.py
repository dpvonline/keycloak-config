#!/usr/bin/env python
__author__ = "OBI"
__copyright__ = "Copyright 2021, DPV e.V."
__license__ = "MIT"

import argparse
import logging
import os
import re
from pathlib import Path
from typing import List

import rotate_backups

from docker import DockerUtils, DockerContainer
from logger import logger, init_mail
from params import PARAMS
from util import init_params, timestamp_string, str2bool, check_file_exists, check_dir_empty


class BackupManager(object):
    def __init__(self, params):
        self._backup_dir = Path(params['BACKUP_DIR'])
        self._latest_dir = self._backup_dir.joinpath('latest')

        self._db_user = params['MYSQL_USER']
        self._db_password = params['MYSQL_PASSWORD']
        self._database = params['MYSQL_DATABASE']
        self._db_server = params['MYSQL_HOST']

    def __activate_maintenance(self):
        DockerUtils.run_cmd(cmd="docker stop keycloak_keycloak", container=DockerContainer.LOCAL)

    def __deactivate_maintenance(self):
        DockerUtils.run_cmd(cmd="docker start keycloak_keycloak",
                            container=DockerContainer.LOCAL)

    def __verify_prior_backup(self):
        # Check if data dir is present and non-empty
        if check_dir_empty(self._backup_dir, container=DockerContainer.LOCAL):
            logger.error("Backup dir empty. Check mount")
            raise

    def __backup_database(self, backup_dir: str):
        cmd_mkdir = "mkdir -p {}".format(backup_dir)
        DockerUtils.run_cmd(cmd=cmd_mkdir, container=DockerContainer.LOCAL)

        cmd = "mysqldump --single-transaction --column-statistics=0 -h {server} -u {user} -p{pwd} {db} > {path}/backup.sql".format(
            server=self._db_server,
            user=self._db_user,
            pwd=self._db_password,
            db=self._database,
            path=Path(backup_dir))
        DockerUtils.run_cmd(cmd=cmd, container=DockerContainer.LOCAL)

    def __verify_post_backup(self, backup_dir: str):
        # Check that database backup is there
        logger.info("Verifying backup sanity from {}".format(backup_dir))
        db_backup_fn = "{path}/backup.sql".format(path=Path(backup_dir))
        if not check_file_exists(db_backup_fn, container=DockerContainer.LOCAL):
            logger.error("Database backup file {} not present.".format(db_backup_fn))
            raise

    def __verify_prior_restore(self, backup_dir: str):
        self.__verify_post_backup(backup_dir=backup_dir)

    def __restore_database(self, backup_dir: str):
        # Drop
        cmd_drop = "mysql -h {server} -u {user} -p{pwd} -e \"DROP DATABASE {db}\"".format(server=self._db_server,
                                                                                          user=self._db_user,
                                                                                          pwd=self._db_password,
                                                                                          db=self._database)
        DockerUtils.run_cmd(cmd=cmd_drop, container=DockerContainer.LOCAL)

        # Create
        cmd_create = "mysql -h {server} -u {user} -p{pwd} -e \"CREATE DATABASE {db}\"".format(server=self._db_server,
                                                                                              user=self._db_user,
                                                                                              pwd=self._db_password,
                                                                                              db=self._database)
        DockerUtils.run_cmd(cmd=cmd_create, container=DockerContainer.LOCAL)

        # Restore
        cmd_restore = "mysql -h {server} -u {user} -p{pwd} {db} < {path}/backup.sql".format(server=self._db_server,
                                                                                            user=self._db_user,
                                                                                            pwd=self._db_password,
                                                                                            db=self._database,
                                                                                            path=Path(backup_dir))
        DockerUtils.run_cmd(cmd=cmd_restore, container=DockerContainer.LOCAL)


    def __verify_post_restore(self):
        self.__verify_prior_backup()

    def backup(self, incremental=False) -> bool:
        ts_string = timestamp_string()
        backup_dir = os.path.join(self._backup_dir, ts_string)
        logger.info("Starting backup to folder {}".format(backup_dir))
        try:
            self.__activate_maintenance()
            self.__verify_prior_backup()
            self.__backup_database(backup_dir=backup_dir)
            self.__verify_post_backup(backup_dir=backup_dir)
        finally:
            self.__deactivate_maintenance()
            logger.info("Finished backup to folder {}".format(backup_dir))
            return True

    def restore_backup(self, backup_dir: str) -> bool:
        # Backup current state first
        self.backup()
        logger.info("Start restoring backup from folder {}".format(backup_dir))
        try:
            self.__activate_maintenance()
            self.__verify_prior_restore(backup_dir=backup_dir)
            self.__restore_database(backup_dir=backup_dir)
            self.__verify_post_restore()
        finally:
            self.__deactivate_maintenance()
            logger.info("Finished restoring backup from folder {}".format(backup_dir))
            return True

    def list_backups(self) -> List[str]:
        backup_dirs = []
        regexp = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}')
        for f in os.scandir(self._backup_dir):
            if f.is_dir() and bool(regexp.search(f.path)):
                backup_dirs.append(f.path)

        backup_dirs.sort()
        return backup_dirs

    def clean_backups(self):
        rotation_fn = os.path.dirname(os.path.realpath(__file__)) + '/rotation.ini'
        res = rotate_backups.load_config_file(rotation_fn)
        for location, rotation_scheme, options in res:
            options['prefer_recent'] = True
            rotate_backups.RotateBackups(rotation_scheme=rotation_scheme, **options).rotate_backups(location)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--restore', required=False,
                        help="Restore backup.", action="store_true")
    parser.add_argument('-b', '--backup', required=False,
                        help="Create backup.", action="store_true")
    parser.add_argument('-c', '--clean', required=False,
                        help="Rotate backups.", action="store_true")
    parser.add_argument('-i', '--incremental', required=False,
                        help="Incremental backup.", action="store_true")
    parser.add_argument('-v', '--verbose', required=False,
                        help="Increase verbosity backup.", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        logger.setLevel(level=logging.INFO)

    incremental_backup = False
    if args.incremental:
        incremental_backup = True

    init_params(PARAMS)

    if str2bool(PARAMS['SEND_MAIL']):
        init_mail(fromaddr=PARAMS['SMTP_FROM'], password=PARAMS['SMTP_PWD'], toaddrs=PARAMS['SMTP_TO'],
                  subject="DPV Cloud Backup", mailhost=PARAMS['SMTP_HOST'],
                  mailport=PARAMS['SMTP_PORT'])

    backup_manager = BackupManager(params=PARAMS)

    if args.backup:
        backup_manager.backup(incremental=incremental_backup)

    if args.restore:
        backups = backup_manager.list_backups()
        for c, val in enumerate(backups):
            logger.info("   #{}:    {}".format(c, val))

        backup_id = int(input("Enter backup to restore:"))
        assert backup_id < len(backups)
        backup_manager.restore_backup(backups[backup_id])

    if args.clean:
        backup_manager.clean_backups()
