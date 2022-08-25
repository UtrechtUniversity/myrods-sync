#!/usr/bin/python
# (c) 2021 Ton Smeele - Utrecht University
#
#  MyRodsConnection manages an authenticated 'session' with an iRODS zone
#
#  connect parameters: 
#    username : optional
#               if username is specified then irods environment file is
#                  updated to reflect this username
#               if username is absent, then username from irods environment file is used
#    password : optional
#               if password is specified, then .irodsA file is updated with it
#               if password is absent/empty, then .irodsA file content is used
#    env      : optional
#               if env is specified, then irods_environment.json file is updated
#               if env is absent, then irods_environment.json is used
#               NB: if username differs from the irods_environment.json then
#                   the file is updated to reflect the specified username
#
# 
import os
import json
import ssl
import irods
from irods import password_obfuscation
from irods.models import Resource
from irods.session import iRODSSession

IRODS_ENV_FILE = '~/.irods/irods_environment.json'
IRODS_TOKEN_FILE = '~/.irods/.irodsA'
DEBUG = False

class MyRodsConnection():

    def __init__(self):
        self.session = None
        self.irods_env = None
        self.password = None
        self.token = None
        # select and register location of irods environment file    
        if 'IRODS_ENVIRONMENT_FILE' in os.environ:
            self.irods_env_file = os.environ['IRODS_ENVIRONMENT_FILE']
        else:
            self.irods_env_file = os.path.expanduser(IRODS_ENV_FILE)

    def __del__(self):
        if self.session is not None:
            self.cleanup()


    def cleanup(self):
        if self.session is not None:
            self.session.cleanup()
            self.session = None



    def host(self):
        if self.session == None or not 'irods_host' in self.irods_env: 
            return
        return self.irods_env['irods_host']


    def connect(self, username=None, password=None, env=None):
        # add/make changes to iRODS environment if needed
        self.update_irods_environment_file(username, env)

        # faciliate users to inspect resulting environment
        self.irods_env = self.get_irods_environment()

        # connect with iRODS server
        # first we attempt to login using an existing stored token ('reconnect')

        if DEBUG: print('MyRods: reconnecting...:')
        self.session = self._connect(None)
        if self.session != None:
            if DEBUG: print('MyRods: reconnect successful')
            return self.session
        if password == None:
            if DEBUG: print('MyRods: reconnect failed and no pwd available')
            return None

        # if existing token login failed, we try to login using the specified password
        if DEBUG: print('MyRods: connect with password')
        self.token = None
        self.session = self._connect(password)
        if self.session == None:
            if DEBUG: print('MyRods: connect failed')
            return None
        
        if DEBUG: print('MyRods: authenticated')
        if self.token != None:
            # we save the received token so that subsequent icommands can re-use it 
            self.save_irods_token(self.token)

        return self.session


    def _connect(self, password):
        ssl_context = ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH,
                cafile=None, capath=None, cadata = None)
        ssl_settings = {'ssl_context' : ssl_context }
        try:
            if password != None:
                # connect with password specified
                session = iRODSSession(
                    password = password,
                    irods_env_file = self.irods_env_file,
                    **ssl_settings
                    )
                if session != None:
                    if session.pool.account.authentication_scheme == 'pam':
                        # extract negotiated token
                        self.token = session.pam_pw_negotiated[0]
                    else:
                        self.token = password
            else:
                # connect with stored token
                session = iRODSSession(
                    authentication_scheme = 'native',
                    irods_env_file = self.irods_env_file,
                    **ssl_settings
                    )
            if session == None:
                return None
            # test if we are authenticated (to rule out that we have an unauthenticated connection)
            # an unauthenticated connection will raise an exception on below query
            if DEBUG: print('MyRods: testing access')
            query = session.query(Resource)
        except:
            self.cleanup()   # cleanup unauthenticated connection
            return None
        return session




    # PRIVATE METHODS

    def update_irods_environment_file(self, username, env):
        stored = self.get_irods_environment()
        if env == None:
            env = {}
        if username != None:
            env['irods_user_name'] = username
        changed = False
        for key in env:
            if not (key in stored) or stored[key] != env[key]:
                stored[key] = env[key]
                changed = True
        if changed:
            self.save_irods_environment(stored)



    def get_irods_environment(self):
        try:
            with open(self.irods_env_file, 'rt') as f:
                data = json.load(f)
            return data
        except IOError:
            return {}


    def save_irods_environment(self,env):
        if DEBUG: print('MyRods: saving irods environment')
        if env == None:
            return False
        try:
            os.mkdir(os.path.expanduser('~/.irods'), mode=0o700)
        except:
            pass
        try:
            with open(self.irods_env_file, 'wt') as f:
                json.dump(env, f,indent=4)
            return True
        except IOError:
            return False


    def get_irods_token(self):
        try:
            with open (os.path.expanduser(IRODS_TOKEN_FILE), 'r') as f:
                data = f.read()
            return irods.password_obfuscation.decode(data)
        except IOError:
            return None


    def save_irods_token(self, token):
        if DEBUG: print('MyRods: saving token')
        data = irods.password_obfuscation.encode(token)
        try:
            with open (os.path.expanduser(IRODS_TOKEN_FILE), 'w') as f:
                f.write(data)
            return True
        except IOError:
            return False

