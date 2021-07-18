#!/usr/bin/env python
__author__ = "OBI"
__copyright__ = "Copyright 2021, DPV e.V."
__license__ = "MIT"

import argparse
import logging
import sys

from keycloak_manager import KeycloakManager
from logger import init_mail
from params import PARAMS
from util import init_params, str2bool

logger = logging.getLogger("dpv_notify")

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

    smtp_handler = None
    if str2bool(PARAMS['SEND_MAIL']):
        smtp_handler = init_mail(fromaddr=PARAMS['SMTP_FROM'], password=PARAMS['SMTP_PWD'], toaddrs=PARAMS['SMTP_TO'],
                                 subject="DPV Auth User Notify", mailhost=PARAMS['SMTP_HOST'],
                                 mailport=PARAMS['SMTP_PORT'])

    try:
        manager = KeycloakManager(params=PARAMS)
        logger.info("Guckuck, ihr Räuber! Folgende neue Anmeldungen gab es:")
        user_changed = manager.check_registrations()
        permission_changed = manager.check_changed_permissions()
        data_changed = user_changed or permission_changed

        if smtp_handler:
            smtp_handler.set_send_mail(send_mail=data_changed)
    except:
        logger.error("Entweder es läuft ein Update oder etwas mächtig schief. \n"
                     "Sorgen solltest du dir erst machen, wenn du diese Nachricht regelmäßig bekommst.")

    logging.shutdown()
    sys.exit(0)
