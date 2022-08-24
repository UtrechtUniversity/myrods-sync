# myrods-sync
Myrods-sync is a graphical desktop application to help you synchronize
the content of a local data folder with a collection on an iRODS data grid.

The application wraps an existing iRODS client commandline tool 
(irsync) to make its function available in a graphical user interface.  
A folder can be uploaded to iRODS, or downloaded to the workstation.

An existing configured connection to an iRODS grid is detected and reused.
If a configured connection is missing, a dialog is initiated in which 
the user selects a configuration from a list of known iRODS zones. 
Further, the user is requested to provide credentials to login.

## Installation
Prerequisite: 
Linux workstation with a graphical desktop environment and Python3+.

Install the following dependencies: (see links for installation instructions)
- [iRODS icommand client tools](https://github.com/irods/irods_client_icommands)
- [Python iRODS client](https://github.com/irods/python-irodsclient)








 

 




