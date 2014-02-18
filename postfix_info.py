#!/bin/env python

#### import collectd
import fileinput
import sys
import os,subprocess,re
import time
import socket
#### from socket import socket

hostname = socket.gethostbyaddr(socket.gethostname())[0]
metric_path = 'sfly.prod.host.infrastructure.%s' % hostname
info = {}
keys = ('sent', 'deferred', 'bounced')

def read_callback():
    """ returns tail /var/log/maillog"""

    last_min = None
    info['sent'] = 0
    info['deferred'] = 0
    info['bounced'] = 0
    info['total_delay'] = 0
    info['total_txns'] = 0

    try:
        data = subprocess.Popen(['/usr/bin/tail','-25000','/var/log/maillog'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]
    except:
        return None

    reg = re.compile('(?P<month>[a-zA-Z]{3}) (?P<day>[0-9]{2}) (?P<hr>[0-9][0-9]):(?P<min>[0-9][0-9]):(?P<sec>[0-9][0-9]) .*delay=(?P<send_delay>[^,]+),.*status=(?P<status>(sent|deferred|bounced))')
    for line in data.split('\n'):
        reg_match = reg.match(line)

        if reg_match:
            linebits = reg_match.groupdict()

            if linebits['min'] == last_min:
                if linebits['status'] == 'sent':
                    info['sent'] += 1
                if linebits['status'] == 'deferred':
                    info['deferred'] += 1
                if linebits['status'] == 'bounced':
                    info['bounced'] += 1
            else:
                info['total_txns'] = info['sent'] + info['deferred'] + info['bounced']
                info['sent'] = 0
                info['deferred'] = 0
                info['bounced'] = 0

            last_min = linebits['min']

    #### print "%s %s %s:%s sent: %s deferred: %s bounced: %s total txns: %s" % (linebits['month'],linebits['day'],linebits['hr'],linebits['min'], sent,deferred,bounced, total_txns)
    from socket import socket
    sock = socket()

    server = 'graphite-carbon1.internal.shutterfly.com'
    port = 2003
    try:
        sock.connect( (server,port) )
    except:
        print "unable to connect to %s port %s" % (server,port)

    now = time.time()
    lines = []
    for key in keys:
        prefix = '%s.postfix.%s' % (metric_path, key)
        lines.append( "%s %s %s" % (prefix, info[key], now ))
        message = '\n'.join(lines) + '\n' #all lines must end in a newline
        #### print "%s %s" % ( key,info[key])
        #### dispatch_value(key)
    print message
    sock.sendall(message)

def dispatch_value(key):
    val = collectd.Values(type='gauge')
    val.type_instance = key
    val.values = info[key]
    val.dispatch()

def summary():
    """ returns tail /var/log/maillog"""

    last_min = None
    info['sent'] = 0
    info['deferred'] = 0
    info['bounced'] = 0
    info['total_delay'] = 0
    info['total_txns'] = 0
    info['total_sent'] = 0
    info['total_deferred'] = 0
    info['total_bounced'] = 0

    reg = re.compile('(?P<month>[a-zA-Z]{3}) (?P<day>[0-9]{2}) (?P<hr>[0-9][0-9]):(?P<min>[0-9][0-9]):(?P<sec>[0-9][0-9]) .*delay=(?P<send_delay>[^,]+),.*status=(?P<status>(sent|deferred|bounced))')

    for line in fileinput.input('/var/log/maillog'):
        reg_match = reg.match(line)

        if reg_match:
            linebits = reg_match.groupdict()

            if linebits['min'] == last_min:
                if linebits['status'] == 'sent':
                    info['sent'] += 1
                if linebits['status'] == 'deferred':
                    info['deferred'] += 1
                if linebits['status'] == 'bounced':
                    info['bounced'] += 1
                 
            else:
                print "%s %s %s:%s sent: %s deferred: %s bounced: %s total txns: %s" % (linebits['month'],linebits['day'],linebits['hr'],linebits['min'], info['sent'],info['deferred'], info['bounced'], info['total_txns'])
                info['total_txns'] = info['sent'] + info['deferred'] + info['bounced']
                info['total_sent'] = info['total_sent'] + info['sent']
                info['total_deferred'] = info['total_deferred'] + info['deferred']
                info['total_bounced'] = info['total_bounced'] + info['bounced']
                info['sent'] = 0
                info['deferred'] = 0
                info['bounced'] = 0

            last_min = linebits['min']

    pct_sent = 0.0
    total = info['total_sent'] + info['total_deferred'] + info['total_bounced'] 
    pct_sent = ( info['total_sent'] / total )
    print "%f %f %.3f" % ( info['total_sent'], total, info['total_sent']/total  )
    #### for key in keys:
    ####    prefix = '%s%s' % (metric_path, key)
    ####    print "%s %s %s" % (prefix, info[key], time.time())
        #### print "%s %s" % ( key,info[key])
        #### dispatch_value(key)

while True:
    read_callback()
    time.sleep(10)

#### collectd.register_read(read_callback);

