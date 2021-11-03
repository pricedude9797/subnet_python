###########################################################
# subnet.py
# Author: Christopher Price
# Email: chris@pricedude.com
# Version: 2.0
# Date: 10/5/21
###########################################################

import re
import sys
import signal

def Exit_gracefully(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, Exit_gracefully)

###########################################################
# Start: Validation
###########################################################
def entry_format(entry):
    '''Return the entry format; "cidr" or "mask"'''
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$",entry): return 'cidr'
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",entry): return 'mask'

def validate_ip(ip):
    '''Validate the IP octet ranges. Allowed are class A through class C'''
    ip = ip.split('.')
    if int(ip[0]) < 1 or int(ip[0]) > 239: return False
    if int(ip[1]) < 0 or int(ip[1]) > 255: return False
    if int(ip[2]) < 0 or int(ip[2]) > 255: return False
    if int(ip[3]) < 0 or int(ip[3]) > 255: return False
    return True

def validate_cidr(cidr):
    '''Validate CIDR range from 8 to 30'''
    if int(cidr) < 8 or int(cidr) > 30: return False
    return True

def validate_mask(mask):
    mask_b = ip_to_bin(mask)
    Flag = False
    for item in mask_b[::-1]:
        if item == '0':
            if Flag == True: return False
        if item == '1':
            Flag = True
    return True
###########################################################


###########################################################
# Start: Conversion
###########################################################
def ip_to_bin(ip):
    '''Given a vaild dotted-decimal IP address, return the 32-bit binary string'''
    ip = ip.split('.')
    ip_b = ''
    for i in range(4):
        ip_b += str(bin(int(ip[i]))[2:].zfill(8))
    return ip_b

def bin_to_ip(b):
    '''Given a 32-bit binary string, return the dotted-decimal IP address'''
    octet1 = str(int(b[0:8], base = 2))
    octet2 = str(int(b[8:16], base = 2))
    octet3 = str(int(b[16:24], base = 2))
    octet4 = str(int(b[24:32], base = 2))
    return octet1 + '.' + octet2 + '.' + octet3 + '.' + octet4

def ip_to_int(ip):
    '''Given an IP address, return the integer equivilant'''
    return int(ip_to_bin(ip), 2)

def int_to_ip(i):
    '''Given an integer, return the IP equivilant'''
    return bin_to_ip('{:032b}'.format(i))

def cidr_to_mask(cidr):
    '''Given the cidr, return the mask'''
    return bin_to_ip('1' * int(cidr) + '0' * (32 - int(cidr)))

def mask_to_cider(mask):
    return str(ip_to_bin(mask).count('1'))
###########################################################


###########################################################
# Subnet Class
###########################################################
class Subnet:
    def __init__(self, ip, cidr, mask):
        self.ip = ip
        self.cidr = cidr
        self.mask = mask

    def display(self):
        lwidth = 30
        print()
        print('IP Address: '.rjust(lwidth), '{}/{} ({})'.format(self.ip, self.cidr, self.mask))
        print('Number of hosts: '.rjust(lwidth), '{}'.format(2 ** (32 - int(cidr))-2))
        print('Network address: '.rjust(lwidth), '{}'.format(self.get_network()))
        print('First host: '.rjust(lwidth), '{}'.format(self.get_first()))
        print('Last host: '.rjust(lwidth), '{}'.format(self.get_last()))
        print('Broadcast address: '.rjust(lwidth), '{}'.format(self.get_broadcast()))
        print()

    def get_network(self):
        return int_to_ip(ip_to_int(self.ip) & ip_to_int(self.mask))
    
    def get_broadcast(self):
        return int_to_ip(ip_to_int(self.get_network()) + 2 ** (32 - int(cidr))-1)

    def get_first(self):
        return int_to_ip(ip_to_int(self.get_network())+1)

    def get_last(self):
        return int_to_ip(ip_to_int(self.get_broadcast())-1)
###########################################################


###########################################################
# - codes
###########################################################
message = {}
message['v'] = "subnet, Version 2.0, 10/7/21"
message['h'] = 'Syntax: "xxx.xxx.xxx.xxx/xx" or "xxx.xxx.xxx.xxx xxx.xxx.xxx.xxx"'
###########################################################


###########################################################
# Program code
###########################################################
try:
    # Evaluate cli syntax and get entry from user
    if len(sys.argv[1:]) == 0:
        print('\nSyntax: "xxx.xxx.xxx.xxx/xx" or "xxx.xxx.xxx.xxx xxx.xxx.xxx.xxx"\n')
        entry = input('Enter the IP address and mask: ')
    elif len(sys.argv[1:]) == 1:
        entry = sys.argv[1]
        if re.match(r"^-.$",entry):
            msg = message.get(entry[1:])
            if msg:
                print('\n\t{}\n'.format(msg))
            else:
                print('Unknown request')
            sys.exit(0)
    elif len(sys.argv[1:]) == 2:
        entry = sys.argv[1] + ' ' + sys.argv[2]

    # Evaluate the entered format and decide how to parse
    if entry_format(entry) == 'cidr':
        entry = entry.split('/')
        if not validate_cidr(entry[1]): raise Exception('Invalid CIDR entry')
        cidr = entry[1]
        mask = cidr_to_mask(entry[1])
    elif entry_format(entry) == 'mask':
        entry = entry.split(' ')
        if not validate_mask(entry[1]): raise Exception('Invalid mask entry')
        mask = entry[1]
        cidr = mask_to_cider(entry[1])
    else:
        raise Exception('\nSyntax error\nExpected: "xxx.xxx.xxx.xxx/xx" or "xxx.xxx.xxx.xxx xxx.xxx.xxx.xxx"\n')
    
    if not validate_ip(entry[0]): raise Exception('Invalid IP entry')
    ip = entry[0]

except Exception as e:
    print(e)
    sys.exit(0)

thing = Subnet(ip, cidr, mask)
thing.display()
###########################################################