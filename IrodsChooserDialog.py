#!/usr/bin/python
# (c) 2021 Ton Smeele - Utrecht University
#
# class IrodsChooserDialog:
# a treeview dialog in which an iRODS object can be selected
#
# class IrodsChooserStore:
# builds an in-memory store of iRODS collection information 
# used as input for the treeview dialog

import gi
from gi.repository import Gtk


class IrodsChooserDialog(Gtk.Dialog):
    def __init__(self, store):
        super().__init__()
        self.props.title = 'Select a collection to synchronize'

        # initialize the treeview with the provided store data
        self.h_store = store
        treeview = Gtk.TreeView(model = store)
        self.h_treeview = treeview
        renderer = Gtk.CellRendererText()
        self.column = Gtk.TreeViewColumn('Collection', renderer,text=0)
        treeview.append_column(self.column)

        # and show result
        self.add_button('Create', 500)
        self.add_buttons(
             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK)
        box = self.get_content_area()
        box.add(treeview)
        self.show_all()

    # returns the iRODS collection path selected by the user (or None)
    def get_selection(self):
        treeselection = self.h_treeview.get_selection()
        model, treeiter = treeselection.get_selected()
        if treeiter is not None:
            path = model.get_path(treeiter)
            pathname = ''
            node = []
            for level in range(len(path)):
                # retrieve name of path component and add this to pathname
                node.append(path[level])
                node_iter = self.h_store.get_iter(node)
                name = self.h_store.get_value(node_iter,0)
                pathname = pathname + '/' + name
            return pathname
        return None

    def add_child(self, name):
        treeselection = self.h_treeview.get_selection()
        model, treeiter = treeselection.get_selected()
        if treeiter is None:
            return False
        child = self.h_store.append(treeiter, [name])
        path = model.get_path(child)
        self.h_treeview.expand_to_path(path)
        self.h_treeview.set_cursor(path)

    def do_get_preferred_width(self):
        return 350,400


class IrodsChooserStore():
    def __init__(self, irods_session):
        self.h_store = Gtk.TreeStore(str)
        self.irods = irods_session

    # returns a handle to the in-memory store (for provisioning a treeview)
    def get_store(self):
        return self.h_store

    # loads iRODS collection names hierarchy into the in-memory store 
    def load_iRODS_collections(self):
        # we start at /zone/home
        self.root = '/' + self.irods.zone + '/home'
        self.load_an_iRODS_subcollection(None, self.root)

    def load_an_iRODS_subcollection(self, parent_obj, parent_path):  
        for coll_path, coll_name in self.subcollections(parent_path):
            child_obj = self.h_store.append(parent_obj, [coll_name])
            # also load subtree of child
            self.load_an_iRODS_subcollection(child_obj, coll_path) 
   
    def get_path_prefix(self):
        # returns <zone_name>/home can be used as prefix to irods pathnames
        return self.root


    # (only for debug purposes)
    # ability to manually populate store with arbitrary label, returns handle to loaded label
    def add_name(self, parent_obj, name):
        return self.h_store.append(parent_obj, [name])


    # generator
    def subcollections(self, path):
        try:
            coll = self.irods.collections.get(path)
        except:
            # collection does not exist or is inaccessible
            # just pretend no children
            raise StopIteration
        for subcoll in coll.subcollections:
            yield subcoll.path, subcoll.name

