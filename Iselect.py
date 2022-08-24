#!/usr/bin/python
# (c) 2022 Ton Smeele - Utrecht University
#
# Iselect manages a dict of iRODS zone configurations
#
# input file IRODSZONESFILE
# format must be: 
#   { "zone1": { "description" : "This is zone 1",
#                "config" : { ... }
#              },
#     "zone2": { ... }
#   }
# where the "config" json object will be used as outputfile content
#

import os
import json
import re
import urllib.request


# the default locations for zone config information
# IRODSZONESFILE1 is tried first, the second file is used as fallback

IRODS_ZONES_FILE1 = '/etc/irods_zones.json'
IRODS_ZONES_FILE2 = 'https://yoda.uu.nl/facts/irods_zones.json'


class Iselect():

    def __init__(self, location=None):
        self.zones = None
        if location != None:
            self.zones = self.configure(location)
        if self.zones == None:
            self.zones = self.configure(IRODS_ZONES_FILE1)
        if self.zones == None:
            self.zones = self.configure(IRODS_ZONES_FILE2)

    def get_zones(self):
        return { z + ' - ' + self.zones[z]['description'] : z  for z in self.zones}


    def get_irods_environment(self, key):
        if not key in self.zones:
            return None
        return self.zones[key]['config']


    def configure(self, location):
        if self.is_uri(location):
            return self.read_url(location)
        else:
            return self.read_file(os.path.expanduser(location))


    def is_uri(self, text):
        regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, text) is not None


    def read_url(self, url):
        try:
            with urllib.request.urlopen(url) as f:
                data = f.read().decode('utf-8')
            return json.loads(data)
        except IOError:
            return None


    def read_file(self, path):
        try:
            with open(path, 'rt') as f:
                data = json.load(f)
            return data
        except IOError:
            return None

