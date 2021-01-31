#!/usr/bin/env python
__author__ = "OBI"
__copyright__ = "Copyright 2021, DPV e.V."
__license__ = "MIT"

import logging
from logging import handlers
import smtplib

logger = logging.getLogger("dpv_backup")


def init_mail(fromaddr, password, toaddrs, mailhost, mailport, subject="DPV Cloud Backup", ):
    logging.getLogger('').addHandler(
        SMTPHandler(fromaddr=fromaddr, password=password, toaddrs=toaddrs,
                    subject=subject, mailhost=mailhost,
                    mailport=mailport))


class SMTPHandler(logging.handlers.BufferingHandler):
    def __init__(self, fromaddr: str, password: str, toaddrs: str, subject: str, mailhost: str,
                 mailport: int = smtplib.SMTP_SSL_PORT, capacity=1000):
        logging.handlers.BufferingHandler.__init__(self, capacity=capacity)
        self.buffer = []
        self.setFormatter(logging.Formatter("%(asctime)s %(levelname)-5s %(message)s"))
        self._smtp_server = mailhost
        self._smtp_port = int(mailport)
        self._fromaddr = fromaddr
        self._password = password
        self._toaddrs = toaddrs
        self._subject = subject

    def __sendmail(self, msg: str) -> bool:
        # Try to log in to server and send email
        with smtplib.SMTP_SSL(self._smtp_server, self._smtp_port) as server:
            server.login(self._fromaddr, self._password)
            server.sendmail(self._fromaddr, self._toaddrs, msg)
            return True

        return False

    def flush(self):
        self.acquire()
        try:
            if len(self.buffer) > 0:
                msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (
                    self._fromaddr, self._toaddrs, self._subject)
                for record in self.buffer:
                    s = self.format(record)
                    msg = msg + s + "\r\n"
                if self.__sendmail(msg):
                    print("Message send")
                else:
                    print("Error sending message")
        finally:
            self.buffer = []
            self.release()
