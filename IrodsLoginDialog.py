#!/usr/bin/python
# (C) 2022 Ton Smeele - Utrecht University
#
# A Gtk dialog box in which the user can select a service and enter credentials
# 
# The dialog box requires a dict parameter 'services' which specifies content 
# for the services combobox.  { displayed_label : data }
#
# method get_results() return the tuple  (service, username, password)
# where service is the data field of the dict services, or any text entered in this widget

import gi
from gi.repository import Gtk
from EntryCombo import EntryCombo


class IrodsLoginDialog(Gtk.Dialog):
    def __init__(self, parent, title, services, active=None):
        Gtk.Dialog.__init__(self, title, parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.setup(services, active)


    def setup(self, services, active):
        self.username = ''
        self.password = ''
        box = self.get_content_area()
        grid = Gtk.Grid()

        label_service = self.make_label('Service name/url ')
        label_user = self.make_label('Username ')
        label_password = self.make_label('(access) Password ')

        self.combo_service = EntryCombo(services, active)
        self.entry_user = Gtk.Entry()
        self.entry_user.set_placeholder_text('yourname@uu.nl')
        self.entry_password = Gtk.Entry()
        self.entry_password.set_visibility(False)

        # grid  widget, columnleft, rowtop, widthCols, heightCols
        col = 0
        grid.attach(label_service, col, 0, 1, 1)
        grid.attach(label_user, col, 1, 1, 1)
        grid.attach(label_password, col, 2, 1, 1)
        col = 1
        grid.attach(self.combo_service, col, 0, 1, 1)
        grid.attach(self.entry_user, col, 1, 1, 1)
        grid.attach(self.entry_password, col, 2, 1, 1)

        box.add(grid)
        self.set_response_sensitive(Gtk.ResponseType.OK,False)
        self.combo_service.connect('changed', self.on_changed)
        self.entry_user.connect('changed', self.on_changed)
        self.show_all()

    def make_label(self,text):
        label = Gtk.Label()
        label.set_halign(Gtk.Align.END)
        label.set_text(text)
        return label

    def on_changed(self, widget):
        state = False
        service = self.combo_service.get_text()
        username = self.entry_user.get_text()
        if service != '' and username != '':
            state = True
        self.set_response_sensitive(Gtk.ResponseType.OK, state)

    def get_results(self):
        return self.combo_service.get_text(), self.entry_user.get_text(), self.entry_password.get_text()

     

