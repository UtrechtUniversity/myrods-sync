#!/usr/bin/python
# (c) 2021 Ton Smeele - Utrecht University
#
# Application manages the application window 
# 

import gi
from gi.repository import Gtk, GdkPixbuf, Gdk, Gio, GLib
from MainBox import MainBox


MENU_XML = """
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <menu id="main-menu">
    <submenu>
      <attribute name="label" translatable="yes">Server</attribute>
      <item>
        <attribute name="action">win.disconnect</attribute>
        <attribute name="label" translatable="yes">Disconnect</attribute>
      </item>
    </submenu>
  </menu>
</interface>
"""

class Application(Gtk.ApplicationWindow):
    def __init__(self, data):
        Gtk.ApplicationWindow.__init__(self)
        self.set_title(data['program_name'])

        # apply css style to our windows
        # see: https://docs.gtk.org/gtk3/css-overview.html
        css_provider = Gtk.CssProvider()
        css_path = data['css_path']
        css_provider.load_from_path(css_path)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),
             css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # define menu actions
        a_disconnect = Gio.SimpleAction.new("disconnect", None)
        a_disconnect.connect("activate", self.on_disconnect)
        self.add_action(a_disconnect)

        # build menu bar
        builder = Gtk.Builder.new_from_string(MENU_XML, -1)
        menumodel = builder.get_object("main-menu")
        menu = Gtk.MenuBar.new_from_model(menumodel)
        menubar = Gtk.Box(hexpand=True)
        menubar.pack_start(menu, True, True, 0)
        menubar.set_name('top-menu')

        # show menu and other window content
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.add(menubar)
        self.mainbox = MainBox(self, data)
        self.mainbox.set_name('main-content')

        box.add( self.mainbox )
        self.add(box)


    def on_disconnect(self, action, value):
        self.mainbox.on_disconnect()
