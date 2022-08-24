#!/usr/bin/python
# (c) 2021 Ton Smeele - Utrecht University
#
# MainBox manages the content of the application window 
# 

import gi
from gi.repository import Gtk, GdkPixbuf, Gdk, Gio
import json
from IrodsChooserDialog import IrodsChooserDialog, IrodsChooserStore
from LogWindow import LogWindow
from IrodsLoginDialog import IrodsLoginDialog
from MyRodsConnection import MyRodsConnection
from Iselect import Iselect
from EntryDialog import EntryDialog

EMPTY_SELECTION = '-> Click to select '

# synctypes: 0 = upload (to iRODS)  1 = download (from iRODS)
SYNCTYPES = [
    '-> upload ->',                
    '<- download <-'          
    ]


class MainBox(Gtk.Box):
    def __init__(self, parentWindow, data):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(5)

        self.parent = parentWindow
        self.data = data

        # we attempt to reconnect to iRODS using 
        # a pre-configured environment + token  (if available)
        self.irods = MyRodsConnection()
        self.irods.connect() 

        # load irods zones list, used to select a known data grid
        self.select = Iselect(self.data['zonelist_location']) 

        # initialize all widgets
        self.setup()

    def setup(self):
        # top section: show logo and instructions
        header = Gtk.Box()
        logo = self.widget_logo()
        header.add(logo)
        label = Gtk.Label()
        label.set_markup('<i>Save valuable data to a Yoda server</i>')
        header.add(label)
        self.add(header)

        # center section: show data locations and run button
        grid = Gtk.Grid()
        self.h_grid = grid
        self.h_grid_rows = 0
        self.add_grid_header()
        self.add_grid_row()
        self.add(grid)


    def widget_logo(self):
        logo_path = self.data['logo_path']
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename= logo_path, width=200, height=200, 
            preserve_aspect_ratio=True)
        logo = Gtk.Image.new_from_pixbuf(pixbuf)
        return logo


    def widget_synctype_selector(self):
        combo = Gtk.ComboBoxText()
        for i in range(len(SYNCTYPES)):
            combo.insert(i, str(i), SYNCTYPES[i])
        combo.set_active(0)
        return combo


    def widget_clicklabel(self, location):
        button = Gtk.Button(label = EMPTY_SELECTION + location)
        return button


    def on_local_folder_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title = 'Select a directory to synchronize',
            parent = self.parent,
            action = Gtk.FileChooserAction.SELECT_FOLDER)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        current_label = widget.get_label()
        if not current_label.startswith(EMPTY_SELECTION):
            dialog.set_filename(current_label)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            widget.set_label(dialog.get_filename())
            widget.completed = True
        dialog.destroy()

    def on_irods_folder_clicked(self, widget):
        if not self.authenticated_after_optional_dialog():
            return
        self.select_collection_dialog(widget)


    def authenticated_after_optional_dialog(self):    
        need_configuration_from_user = (self.irods.session == None)
        title = 'login'
        while need_configuration_from_user:
            # need to ask user to (select an irods environment and) 
            # provide credentials
            choices = self.select.get_zones()
            dialog = IrodsLoginDialog(self.parent, title, choices)
            response = dialog.run()
            
            if response == Gtk.ResponseType.OK:
                (service,username,password) = dialog.get_results()
                self.irods.connect(username, password, 
                        env = self.select.get_irods_environment(service))

                if self.irods.session != None:
                    # authentication was successful
                    self.update_remote_host_label()
                    need_configuration_from_user = False
                else:
                    title = 'authentication failed, please retry'

            else:
                # give up, because user canceled dialog explicitly 
                # or closed the dialog
                need_configuration_from_user = False
            
            dialog.destroy()
        return self.irods.session != None


    def select_collection_dialog(self, widget):
        dataStore = IrodsChooserStore(self.irods.session)
        dataStore.load_iRODS_collections()
     
        dialog = IrodsChooserDialog(dataStore.get_store())
        done = False
        while not done:
            response = dialog.run()
            done = True
            irods_path = dialog.get_selection()
        
            if response == Gtk.ResponseType.OK:
                if irods_path is not None:
                    # show selected collection on button in main window
                    widget.set_label(irods_path)
                    widget.path_prefix = dataStore.get_path_prefix()
                    widget.completed = True
            
            if response == 500 and irods_path is not None: 
                # create button pressed and a collection is selected
                done = False
                create_dialog = EntryDialog(self.parent, 'Create', 'Enter name of sub-collection')
                create_response = create_dialog.run()
                if create_response == Gtk.ResponseType.OK:
                    subcoll = create_dialog.get_results()
                    parentcoll = dataStore.get_path_prefix() + irods_path
                    #print('parent coll: ' + parentcoll)
                    #print('sub coll name: ' + subcoll)
                    if subcoll != '':
                        try:
                            self.irods.session.collections.create(parentcoll + '/' + subcoll)
                            dialog.add_child(subcoll)
                        except:
                            # TODO: inform the user that create failed
                            pass
                create_dialog.destroy()

        dialog.destroy()



    def on_disconnect(self):
        self.irods.session = self.irods.session.cleanup()
        self.update_remote_host_label()


    def on_run_now_clicked(self, widget):
        # only act if both local and remote folders are known
        if widget.h_local_folder.completed and widget.h_remote_folder.completed:
            # print('local folder is :' + widget.h_local_folder.get_label())
            # print('remote folder is:' + widget.h_remote_folder.get_label())
            cmd = self.build_run_command(
                widget.h_local_folder.get_label(),
                widget.h_remote_folder.path_prefix + widget.h_remote_folder.get_label(),
                widget.h_sync_type.get_active()
                )
            log = LogWindow(cmd, 'Synchronization log')


    def update_remote_host_label(self):
        if self.irods.session != None:
            irods_host = self.irods.host()
            self.label_remote.set_markup('<b>Server at ' + irods_host + '</b>')
        else:
            self.label_remote.set_markup('<b>Not yet connected</b>')



    def add_grid_header(self):
        label_local = Gtk.Label()
        label_local.set_markup('<b>Workspace folder</b>')
        self.label_remote = Gtk.Label()
        self.update_remote_host_label()
        row = self.h_grid_rows
        self.h_grid.attach(label_local, 0, row, 1, 1)
        self.h_grid.attach(self.label_remote, 2, row, 1, 1)
        self.h_grid_rows = row + 1
 

    def add_grid_row(self):
        # create widgets for the 4 cells: local / sync / remote / run-now
        local_folder = self.widget_clicklabel('local folder')
        local_folder.completed = False
        local_folder.connect("clicked", self.on_local_folder_clicked)

        sync_type = self.widget_synctype_selector()

        remote_folder = self.widget_clicklabel('Yoda/iRODS folder')
        remote_folder.completed = False
        remote_folder.connect("clicked", self.on_irods_folder_clicked)

        run_now = Gtk.Button(label = 'Run!', border_width = 20)
        run_now.h_local_folder = local_folder
        run_now.h_remote_folder= remote_folder
        run_now.h_sync_type = sync_type
        run_now.connect("clicked", self.on_run_now_clicked)

        # place the created widgets in the grid cells of a new row
        row = self.h_grid_rows     # get current # of rows
        self.h_grid.attach(local_folder, 0, row, 1, 1)
        self.h_grid.attach(sync_type, 1, row, 1, 1)
        self.h_grid.attach(remote_folder, 2, row, 1, 1)
        self.h_grid.attach(run_now, 3, row, 1, 1)
        self.h_grid_rows = row + 1

     
    def build_run_command(self, local, remote, sync):
        done = ';echo "-- END OF LOG --"'
        cmd = 'irsync -r -v '
        if sync == 0:
            cmd = cmd + local + '  i:' + remote
        if sync == 1:
            cmd = cmd + 'i:' + remote + '  ' + local
        return cmd + ';echo "DONE!"'

