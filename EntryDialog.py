#!/usr/bin/python
# (C) 2022 Ton Smeele - Utrecht University
#
# A Gtk dialog box that provides user with a prompt and text entry field  
# 
# method get_results() return the entered string

import gi
from gi.repository import Gtk


class EntryDialog(Gtk.Dialog):
    def __init__(self, parent, title, prompt):
        Gtk.Dialog.__init__(self, title, parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK))
     
        box = self.get_content_area()
        label = Gtk.Label()
        label.set_text(prompt + ' ')
        box.add(label)
        self.entry = Gtk.Entry()
        box.add(self.entry)
        self.show_all()


    def get_results(self):
        return self.entry.get_text()
