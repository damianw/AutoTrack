#!/usr/bin/env python3

import re

def _chunks(l, n):
  for i in range(0, len(l), n):
      yield l[i:i+n]

def _lease(values):
  return {
    'hostname': values[0],
    'ip': values[1],
    'mac': values[2],
    'time': values[3],
    'conn_count': values[4]
  }

def _arp_entry(values):
  return {
    'hostname': values[0],
    'ip': values[1],
    'mac': values[2],
    'conn_count': values[3]
  }

def _parse_list(values_list, n):
  return _chunks([i.strip(" '") for i in values_list.split(',')], n)

def parse(response):
  r = dict(re.findall(r'\{([A-z_]+)::(.*?)\}', response))
  r['dhcp_leases'] = [_lease(values) for values in _parse_list(r['dhcp_leases'], 5)]
  r['arp_table'] = [_arp_entry(values) for values in _parse_list(r['arp_table'], 4)]
  r['ip'] = re.findall(r'((?:\d{1,3}\.){3}\d{1,3})', r['ipinfo'])[0]
  del r['ipinfo']
  return r