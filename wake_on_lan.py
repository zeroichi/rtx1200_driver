#!/usr/bin/env python3

import sys
import pexpect
from datetime import datetime
import json
from rtx1200_driver import RTX1200Controller, CliProtocol
import argparse


def show_now():
    print(datetime.now().strftime('[%Y/%m/%d %H:%M:%S]'))


parser = argparse.ArgumentParser()
parser.add_argument('target', nargs=1, help='target name to be wake up, defined in config file')
parser.add_argument('--config', '-c', nargs=1, help='config file (default: config.json)', default='config.json')

if __name__ == '__main__':
    # parse command line arguments
    args = parser.parse_args()

    # load configuration file
    print("Reading configuration from %s" % args.config)
    with open(args.config, 'r') as jsonfp:
        config = json.load(jsonfp)
    router_config = config['router']
    targets = config['targets']
    target_name = args.target[0]
    if not target_name in targets:
        print('Error: Target name "%s" is not defined in config file.' % target_name)
        sys.exit(1)
    target_config = targets[target_name]

    # connect to a router and send wake on lan packet
    controller = RTX1200Controller(router_config['address'], 22, CliProtocol.SSH,
                                   router_config['username'], router_config['password'],
                                   router_config['admin_password'])
    controller.login()
    controller.admin()
    controller.wake_on_lan(target_config)
    controller.disconnect()

    # ping to the target host until receive a pong
    show_now()
    print('Waiting for server(%s) starting up ' % target_config["address"], end='')
    timeout = 120
    counter = 0
    while counter < timeout:
        sys.stdout.write('.')
        sys.stdout.flush()
        p = pexpect.spawn('ping -c 1 -W 2 %s' % target_config['address'])
        index = p.expect(['bytes from', pexpect.EOF, pexpect.TIMEOUT])
        if index == 0:
            # received a response
            break
        counter = counter + 1
    else:
        print("Error: timeout, server(%s) did not respond to ping.")
        sys.exit(1)
    print()
    show_now()
    print('Server is running !')
