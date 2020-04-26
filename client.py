#!/usr/bin/env python3

import socket
import os
import subprocess
import signal
import sys
import time
import getpass

from hashlib import md5

#
## Used to send packages over the internet
#
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

    work_stations = []
    rdp_connections = []

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

            username = input('Enter username: ')
            passwd = getpass.getpass('Enter password: ')
            print('')

            msg = {
                'command' : 'login',
                'un' : username,
                'pw' : md5(str.encode(passwd)).hexdigest()
            }

            msg = pickle.dumps(msg, -1) 
            self.socket.sendall(msg)

            if self.socket.recv(1024).decode() == 'auth':
                self.is_login = True

        return self.is_login

    def client_loop(self):
        if self.is_connected and self.is_login:
            while self.is_running:


                self.collect_info()

                print('Options\nshow = show all available hosts\nrdp = setup rdp\nq_rdp = terminate all rdp connections\nquit = quit the program\n')
                message_to_server = input('Enter command: ')
                print()

                if message_to_server == 'show':
                    self.handle_show(message_to_server)

                if message_to_server == 'rdp':
                   self.handle_rdp() 
                
                if message_to_server == 'q_rdp':
                    self.handle_quit_rdp()

                if message_to_server == 'quit':
                    self.quit()
    
    def handle_rdp(self):
        self.handle_show('show')
        choice = input('Chose one of the following available work stations: ')
        ws = int(choice) - 1
        choice = self.hosts[ws]

        msg_to_server = {
            'command' : 'rdp',
            'choice' : choice
        }

        msg_to_server = pickle.dumps(msg_to_server, -1)
        self.socket.sendall(msg_to_server)
        data = self.socket.recv(1024)
        print_data = data.decode()
        self.rdp_connections.append(subprocess.Popen(print_data, stdout=subprocess.PIPE, shell = True, preexec_fn=os.setsid))
        
        # Will not have the time to create the tunnel else
        time.sleep(1)
        file_to_open = 'open {}.rdp'.format(self.hosts[ws].name)
        proc = os.system(file_to_open)
        print(proc)
        print('You can now use rdp')

    def handle_quit_rdp(self):
        msg = {
            'command' : 'q_rdp'
            }
        self.socket.sendall(pickle.dumps(msg, -1))
        data = self.socket.recv(1024)
        print_data = data.decode()

        for rdpc in self.rdp_connections:
            os.killpg(os.getpgid(rdpc.pid), signal.SIGTERM)  # Send the signal to all the process groups

        self.rdp_connections = []


    def handle_show(self, msg_to_server):
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
        msg = pickle.loads(self.socket.recv(4094))
        self.hosts = msg.get('hosts')
        self.loginfo = msg.get('loginfo')

    #
    ## Everyone something is updated the server will send a message to all client 
    ## so that they can update their info
    def update_info(self):
        pass

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

    def main(self):
        if(self.connect() and self.login()):
            print('You are now connected and logged in to the system.\n')
            self.collect_info()
            self.is_running = True
            self.client_loop()
        else:
            print('Could not connect and login.')

    
if __name__ == '__main__':

    # The script will vary depending on system
    print(sys.platform)

    if len(sys.argv) == 3:
        c = client(sys.argv[1], int(sys.argv[2]))
        c.main()
    else:
        print('Type ip and port')

    