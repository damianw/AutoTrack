#!/usr/bin/env python3

import ddwrt
import dataset
import requests
from tools import *
from time import sleep
from itertools import *
from functools import *
from datetime import datetime
from pprint import pprint as pp
from threading import Thread, Event
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify

import config

app = Flask(__name__)
app.config.from_object(config)

db = dataset.connect('sqlite:///autotrack.db')
people = db['people']
people_t = people.table
devices = db['devices']
devices_t = devices.table
history = db['history']
history_t = history.table

def _get_status():
  return ddwrt.parse(requests.get(config.URL, auth=(config.DD_USERNAME, config.DD_PASSWORD)).text)

@app.route('/api/v1.0/people', methods=['GET'])
def get_people():
  return jsonify({'people': list(people.all())})

@app.route('/api/v1.0/devices', methods=['GET'])
def get_devices():
  return jsonify({'devices': list(devices.all())})

def _get_people_home(devs):
  for d in devs:
    p = people.find_one(id=d['people_id'])
    if not p: continue
    if p['home_when_{}'.format(d['device_type'])]: yield p

def _get_active_devices():
  active_macs = [entry['mac'].upper() for entry in _get_status()['arp_table']]
  return db.query(devices_t.select().where(devices_t.c.mac.in_(active_macs)))

@app.route('/api/v1.0/people/home', methods=['GET'])
def get_people_home():
  devs = list(_get_active_devices())
  ppl = unique_everseen(_get_people_home(devs), lambda p: p['id'])
  result = {'people': [dict(p, devices=list(filter(lambda dev: dev['people_id'] == p['id'], devs))) for p in ppl]}
  return jsonify(result)

@app.route('/api/v1.0/devices/home', methods=['GET'])
def get_devices_home():
  macs = [entry['mac'].upper() for entry in _get_status()['arp_table']]
  devs = db.query(devices_t.select().where(devices_t.c.mac.in_(macs)))
  return jsonify({'devices': list(devs)})

@app.route('/api/v1.0/status', methods=['GET'])
def get_status():
  return jsonify(_get_status())

@app.route('/api/v1.0/status/arp', methods=['GET'])
def get_arp_table():
  return jsonify({'arp_table': _get_status()['arp_table']})

class HistoryWorker(Thread):

  def __init__(self, event):
    Thread.__init__(self)
    self.event = event

  def run(self):
    while not event.isSet():
      devs = _get_active_devices()
      time = datetime.now()
      history.insert_many({'devices_id': d['id'], 'timestamp': time} for d in devs)
      sleep(5)

if __name__ == '__main__':
  event = Event()
  worker = HistoryWorker(event)
  try:
    worker.start()
    app.run(debug=True)
  except:
    event.set()
