#!/usr/bin/env python

import pexpect
import sys


class CliProtocol():
    TELNET = 1
    SSH = 2

    def __init__(self):
        pass


class UnknownProtocolError(Exception):
    """Exception raised for invalid protocol"""
    pass


class InvalidOperationError(Exception):
    pass


class RTX1200Controller():
    def __init__(self, address, port, proto, user, passwd, admin_passwd):
        self.address = address
        self.port = port
        self.proto = proto
        self.user = user
        self.passwd = passwd
        self.admin_passwd = admin_passwd
        self.is_admin = False

    def login(self):
        if self.proto == CliProtocol.TELNET:
            self.p = pexpect.spawn('telnet %s' % self.address, echo=False)
            self.p.logfile_read = sys.stdout.buffer
            self.p.expect(r'Password:')
            self.p.sendline('')
        elif self.proto == CliProtocol.SSH:
            print('using ssh')
            print('ssh %s -p %d -l %s' % (self.address, self.port, self.user))
            self.p = pexpect.spawn('ssh %s -p %d -l %s' % (self.address, self.port, self.user), echo=True)
            self.p.logfile_read = sys.stdout.buffer
            self.p.expect(r'password:')
            self.p.sendline(self.passwd)
        else:
            raise UnknownProtocolError()
        self.p.expect(r'> ')

    def admin(self):
        self.p.sendline('administrator')
        self.p.expect(r'Password:')
        self.p.sendline(self.admin_passwd)
        self.p.expect(r'# ')
        self.is_admin = True

    def wake_on_lan(self, target):
        if not self.is_admin:
            raise InvalidOperationError()
        self.p.sendline('wol send %s %s' % (target['interface'], target['mac_addr']))
        self.p.expect(r'# ')

    def disconnect(self):
        if self.is_admin:
            self.p.sendline('exit')
            self.p.expect(r'> ')
            self.is_admin = False
        self.p.sendline('exit')
        self.p.wait()
        self.p.close()