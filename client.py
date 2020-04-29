#!/usr/bin/env python3

import socket
import os
import subprocess
import signal
import sys
import time
import getpass


from gui import *

# For password encryption, just for prototyping
# Need something stronger
from hashlib import md5

#
## Used to send packages over the internet
## Serialize objects
from server import host
try:
    import cPickle as pickle
except:
    import pickle

#
## 
#
class client:

    is_connected = False
    is_login = False
    is_running = False
    socket = None
    username = ""

    work_stations = []
    current_rdp_connection = None

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.connect((self.ip, self.port))
        self.is_connected = True

        return self.is_connected

    def login(self):
        if self.is_connected:
            
            print('Enter your login info...')

            self.username = input('Enter username: ')
            passwd = getpass.getpass('Enter password: ')
            print('')

            msg = {
                'command' : 'login',
                'un' : self.username,
                'pw' : md5(str.encode(passwd)).hexdigest()
            }

            msg = pickle.dumps(msg, -1) 
            self.socket.sendall(msg)

            if self.socket.recv(1024).decode() == 'auth':
                self.is_login = True

        return self.is_login

    def handle_rdp(self, host, prev_host):

        #self.handle_quit_rdp(prev_host)     
   
        msg_to_server = {
            'command' : 'rdp',
            'choice' : host,
        }

        msg_to_server = pickle.dumps(msg_to_server, -1)
        self.socket.sendall(msg_to_server)

        # Should send the message size as meta data, not hard coded
        msg = pickle.loads(self.socket.recv(4000))

        with open('id_rsa-cert.pub', 'wb') as f:
            file = msg.get('cert')
            f.write(file)
        f.close()

        os.system('mv id_rsa-cert.pub ~/.ssh')
        print_data = msg.get('command')
        
        self.current_rdp_connection = subprocess.Popen(print_data, stdout=subprocess.PIPE, shell = True, preexec_fn=os.setsid)
        
        # Will not have the time to create the tunnel else
        time.sleep(1)
        file_to_open = 'open {}.rdp'.format(host.name)
        subprocess.Popen(file_to_open, shell = True)
 
        #os.system(file_to_open)
        print('You can now use rdp')

    def handle_quit_rdp(self, prev_host):

        if self.current_rdp_connection != None:
            msg = {
                'command' : 'q_rdp',
                'host' : prev_host
            }
            self.socket.sendall(pickle.dumps(msg, -1))
            os.killpg(os.getpgid(self.current_rdp_connection.pid), signal.SIGTERM)  # Send the signal to all the process groups

    def handle_log(self):
        for l in self.loginfo:
            print(l[2] + ' : ' + l[3])
        print()


    def handle_show(self):
        for i, h in enumerate(self.hosts, start = 1):
            print('{}. {}'.format(i, h.to_string()))
        print()

    #
    ## On start this will collect all relevant info. Like workstations in the system and the current user log.
    #
    def collect_info(self):

        msg = {
            'command' : 'collect'
        }

        self.socket.sendall(pickle.dumps(msg, -1))
        msg = pickle.loads(self.socket.recv(8000))
        self.hosts = msg.get('hosts')
        self.loginfo = msg.get('loginfo')

    def quit(self):

        self.handle_quit_rdp()

        msg = {
            'command' : 'quit'
        }
        self.socket.sendall(pickle.dumps(msg, -1))
        msg = self.socket.recv(1024)
        print(msg.decode())
        self.is_running = False
        print('You terminated the connection.')

 
    
if __name__ == '__main__':

    # The script will vary depending on system
    print(sys.platform)

    if len(sys.argv) == 3:
        c = client(sys.argv[1], int(sys.argv[2]))
        
    else:
        print('Type ip and port')

    