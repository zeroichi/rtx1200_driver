#!/usr/bin/env python3

import json
from rtx1200_driver import RTX1200Controller, CliProtocol
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('ppnum', nargs='?', help='PP interface number (default=1)', type=int, default=1)
parser.add_argument('--config', '-c', nargs=1, help='config file (default: config.json)', default='config.json')
parser.add_argument('--verbose', '-v', action='store_true', help='enable verbose output')

if __name__ == '__main__':
    # parse command line arguments
    args = parser.parse_args()

    # load configuration file
    if args.verbose:
        print("Using config file: %s" % args.config)
    with open(args.config, 'r') as jsonfp:
        config = json.load(jsonfp)
    router_config = config['router']

    # connect to a router and send wake on lan packet
    controller = RTX1200Controller(router_config['address'], 22, CliProtocol.SSH,
                                   router_config['username'], router_config['password'],
                                   router_config['admin_password'])
    if args.verbose:
        # output communication log to stdout
        controller.logfile = sys.stdout.buffer
    controller.login()
    ip = controller.get_pp_ip(args.ppnum)
    controller.disconnect()

    print('ip = %s' % ip)
