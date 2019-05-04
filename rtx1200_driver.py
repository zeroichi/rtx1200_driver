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
        self.logfile = None

    def login(self):
        if self.proto == CliProtocol.TELNET:
            self.p = pexpect.spawn('telnet %s' % self.address, echo=False)
            self.p.logfile_read = sys.stdout.buffer
            self.p.expect(r'Password:')
            self.p.sendline('')
        elif self.proto == CliProtocol.SSH:
            self.p = pexpect.spawn('ssh %s -p %d -l %s' % (self.address, self.port, self.user), echo=True)
            if self.logfile:
                self.p.logfile_read = self.logfile
            self.p.expect(r'password:')
            self.p.sendline(self.passwd)
        else:
            raise UnknownProtocolError()
        self.p.expect('RTX1200 (Rev.[0-9.]+)')
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

    # Gets PP(Point-to-Point) interface local IP.
    # Returns IP string if success, empty str if failed.
    def get_pp_ip(self, pp_num=1):
        self.p.sendline('show status pp %d' % pp_num)
        result = self.p.expect([r'PP IP Address Local: ([0-9.]+),', 'Error:', '> '])
        if result == 0:
            # successfully got an IP
            return self.p.match.group(1).decode()
        else:
            # error
            return ''
