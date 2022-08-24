#!/usr/bin/python3
# (C) 2021 Ton Smeele - Utrecht University
# 
# Myrods-sync is a wrapper around irsync to provide a graphical user interface
# While we brand the application as YodaSync, it should work with any iRODS zone
#

PROGRAM_NAME = 'YodaSync'
PROGRAM_VERSION = '0.3'
CSS_FILE = 'myrods-sync.css'
LOGO_FILE = 'UU_logo_2021_EN_RGB_transparant.png'
ZONELIST_LOCATION = '~/git/myrods-sync/irods_zones_prd.json'
DEBUG = False

import gi
import os
from os.path import realpath, dirname
import sys
import getopt

# GUI related imports, first check if user interface is compatible
if not 'DISPLAY' in os.environ:
    print('Error: This program requires a graphical user interface')
    exit(1)
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from Application import *


def main(opts, args):
    program_dir = os.path.dirname(os.path.realpath(__file__))
    data = { 
          'program_name'     : PROGRAM_NAME,
          'program_version'  : PROGRAM_VERSION,
          'program_directory': program_dir,
          'css_path'         : program_dir + '/' + CSS_FILE,
          'logo_path'        : program_dir + '/' + LOGO_FILE,
          'zonelist_location': ZONELIST_LOCATION,
          'opts' : opts,
          'args' : args
          }
    if DEBUG:
        # just dump any exceptions on the console
        win = Application(data)
        win.connect("destroy", Gtk.main_quit)
        win.show_all()
        Gtk.main()
    else:
        try:
            win = Application(data)
            win.connect("destroy", Gtk.main_quit)
            win.show_all()
            Gtk.main()
        except:
            print('Error: Could not initiate GUI')
            exit(2)


def help():
    text = '''
    Usage: guisync [-hv]
    
    Options:
     -h  show this help
     -v  show program version
    '''
    print(text)


# main program
if __name__ == "__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hv')
    except:
        print('Error: Invalid program arguments specified. Use -h for help.')
        exit(1)

    quit = False
    for opt, arg in opts:
        opt = opt.lower()
        if opt == '-v':
            print(PROGRAM_NAME + ' release ' + PROGRAM_VERSION)
            quit = True
        if opt == '-h':
            help()
            quit = True
    if quit:
        exit(0)

    main(opts, args)

