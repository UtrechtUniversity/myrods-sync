#!/usr/bin/python
# (C) 2022 Ton Smeele - Utrecht University
#
# customized Gtk ComboBox widget:
#   - with an entry and a model
#   - entry supports auto-completion based on model
#   - user provides model entries in a dict 
#        { display_label_string : data_string }
#   - set 'active' to one of the entry labels to add a default selection
#
# method get_text() returns the selected 'data', or the text entered
#        (returns empty string while data has not been selected/entered)

import gi
from gi.repository import Gtk

class EntryCombo(Gtk.ComboBox):
    def __init__(self, entries, active=None):
        super().__init__(has_entry=True)
        store = Gtk.ListStore(str,str)
        for key in entries:
            store.append( [entries[key], key] )
        self.set_model(store)
        self.set_entry_text_column(1)
        auto_complete = Gtk.EntryCompletion()
        auto_complete.set_model(store)
        auto_complete.set_text_column(1)
        entry = self.get_child()
        entry.set_completion(auto_complete)
        if active != None:
            for i, entry in enumerate(store):
                if entry[1] == active:
                    self.set_active(i)
    
    def get_text(self):
        it = self.get_active_iter()
        if it is None:
            return self.get_child().get_text()
        return self.get_model()[it][0]
