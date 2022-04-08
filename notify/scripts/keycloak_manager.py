#!/usr/bin/env python
__author__ = "OBI"
__copyright__ = "Copyright 2021, DPV e.V."
__license__ = "MIT"

import datetime
import json
import logging
import os
import time

from keycloak import KeycloakAdmin

from util import format_url

logger = logging.getLogger("dpv_notify")


class KeycloakManager(object):
    def __init__(self, params):
        self._ts_file = '/notify/timestamp.txt'
        self._pms_tile = '/notify/permissions.txt'
        self._url = format_url(params['VIRTUAL_HOST'])
        self._keycloak_admin = KeycloakAdmin(
            server_url=self._url,
            username=params['KEYCLOAK_ADMIN'],
            password=params['KEYCLOAK_ADMIN_PASSWORD'],
            realm_name="DPV",
            user_realm_name="master",
            verify=True)

    def check_registrations(self) -> bool:
        new_users = False
        users = self._keycloak_admin.get_users()

        current_ts_s = time.time()

        ts_s = 0
        if os.path.exists(self._ts_file):
            with open(self._ts_file, 'r') as f:
                val = f.read()
                if val:
                    # 3 seconds grace period
                    ts_s = float(val) + 3

        if ts_s == 0:
            # If no timestamp send new registrations from last 24 hours
            logger.info("Could not find initial timestamp. Send new registration from last 24 hours.")
            ts_s = current_ts_s - 24 * 60 * 60

        last_ts_ms = int(ts_s * 1000.0)

        for user in users:
            user_ts_ms = user['createdTimestamp']
            if user_ts_ms >= last_ts_ms:
                date = datetime.datetime.fromtimestamp(user_ts_ms / 1000.0)
                logger.info("New user registered: {username} at {date}".format(username=user['username'], date=date))
                new_users = True

        with open(self._ts_file, 'w') as f:
            last_ts_s = time.time()
            f.write(str(last_ts_s))

        return new_users

    def check_changed_permissions(self) -> bool:
        permissions_changed = False
        users = self._keycloak_admin.get_users()

        prev_permission_dict = dict()

        try:
            with open(self._pms_tile, 'r') as infile:
                prev_permission_dict = json.load(infile)
        except:
            logger.warning('Cloud not read last permissions')

        permission_dict = dict()
        for user in users:
            user_name = user['username']
            user_id = user['id']
            groups = self._keycloak_admin.get_user_groups(user_id)
            permission_dict[user_name] = list()
            for group in groups:
                group_name = group['path']
                permission_dict[user_name].append(group_name)

            current_groups = set(permission_dict[user_name])
            prev_groups = set()
            if user_name in prev_permission_dict.keys():
                prev_groups = set(prev_permission_dict[user_name])

            joined_groups = current_groups - prev_groups
            if joined_groups:
                logger.info("User: {user} joined groups: {groups}".format(user=user_name, groups=joined_groups))
                permissions_changed = True
            left_groups = prev_groups - current_groups
            if left_groups:
                logger.info("User: {user} left groups: {groups}".format(user=user_name, groups=left_groups))
                permissions_changed = True

        with open(self._pms_tile, 'w') as outfile:
            json.dump(permission_dict, outfile)

        return permissions_changed


