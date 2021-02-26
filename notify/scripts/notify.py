#!/usr/bin/env python
__author__ = "OBI"
__copyright__ = "Copyright 2021, DPV e.V."
__license__ = "MIT"

import argparse
import datetime
import logging
import os
import time

from keycloak import KeycloakAdmin

from logger import init_mail
from params import PARAMS
from util import init_params, format_url, str2bool

logger = logging.getLogger("dpv_notify")


class KeycloakManager(object):
    def __init__(self, params):
        self._ts_file = '/tmp/notify_ts.txt'
        self._url = format_url(params['VIRTUAL_HOST'] + "/auth/")
        self._keycloak_admin = KeycloakAdmin(
            server_url=self._url,
            username=params['KEYCLOAK_USER'],
            password=params['KEYCLOAK_PASSWORD'],
            realm_name="DPV",
            user_realm_name="master",
            verify=True)

    def check_registrations(self):
        logger.debug("Requesting user:")
        users = self._keycloak_admin.get_users({})
        logger.debug("Got {} users".format(len(users)))

        current_ts_s = time.time()

        ts_s = 0
        if os.path.exists(self._ts_file):
            with open(self._ts_file, 'r') as f:
                val = f.read()
                if val:
                    # 3 seconds grace period
                    ts_s = float(val) + 3

        if ts_s == 0:
            ts_s = current_ts_s - 24 * 60 * 60

        last_ts_ms = int(ts_s * 1000.0)

        for user in users:
            user_ts_ms = user['createdTimestamp']
            if user_ts_ms >= last_ts_ms:
                date = datetime.datetime.fromtimestamp(user_ts_ms / 1000.0)
                logger.info("New user registered: {username} at {date}".format(username=user['username'], date=date))

        with open(self._ts_file, 'w') as f:
            last_ts_s = time.time()
            f.write(str(last_ts_s))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', required=False,
                        help="Increase verbosity.", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        logger.setLevel(level=logging.INFO)

    init_params(PARAMS)

    if str2bool(PARAMS['SEND_MAIL']):
        init_mail(fromaddr=PARAMS['SMTP_FROM'], password=PARAMS['SMTP_PWD'], toaddrs=PARAMS['SMTP_TO'],
                  subject="DPV Cloud Backup", mailhost=PARAMS['SMTP_HOST'],
                  mailport=PARAMS['SMTP_PORT'])

    manager = KeycloakManager(params=PARAMS)
    manager.check_registrations()
