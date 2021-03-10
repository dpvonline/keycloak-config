#!/usr/bin/env python
__author__ = "OBI"
__copyright__ = "Copyright 2021, DPV e.V."
__license__ = "MIT"

import logging
import smtplib
from logging import handlers

logger = logging.getLogger("dpv_auth_notify")


def init_mail(fromaddr: str, password: str, toaddrs: str, mailhost: str, mailport: int, send_mail: bool = True,
              subject="DPV Auth Notify"):
    handler = SMTPHandler(fromaddr=fromaddr, password=password, toaddrs=toaddrs,
                          subject=subject, mailhost=mailhost,
                          mailport=mailport, send_mail=send_mail)
    logging.getLogger('').addHandler(handler)
    return handler


class SMTPHandler(logging.handlers.BufferingHandler):
    def __init__(self, fromaddr: str, password: str, toaddrs: str, subject: str, mailhost: str,
                 mailport: int = smtplib.SMTP_SSL_PORT, send_mail: bool = True, capacity=1000):
        logging.handlers.BufferingHandler.__init__(self, capacity=capacity)
        self.buffer = []
        self.setFormatter(logging.Formatter("%(asctime)s %(levelname)-5s %(message)s"))
        self._smtp_server = mailhost
        self._smtp_port = int(mailport)
        self._fromaddr = fromaddr
        self._password = password
        self._toaddrs = toaddrs
        self._subject = subject
        self._send_mail = send_mail

    def __sendmail(self, msg: str) -> bool:
        # Try to log in to server and send email
        with smtplib.SMTP_SSL(self._smtp_server, self._smtp_port) as server:
            server.login(self._fromaddr, self._password)
            server.sendmail(self._fromaddr, self._toaddrs, msg.encode("utf8"))
            return True

        return False

    def set_send_mail(self, send_mail):
        self._send_mail = send_mail

    def flush(self):
        self.acquire()
        if len(self.buffer) > 0 and self._send_mail:
            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (
                self._fromaddr, self._toaddrs, self._subject)
            for record in self.buffer:
                s = self.format(record)
                msg = msg + s + "\r\n"
            try:
                self.__sendmail(msg)
                print("Message send")
            except:
                print("Error sending message")

            finally:
                self.buffer = []
            self.release()
