#!/usr/bin/env python3

# All of this is fine
import socket
import os
import subprocess
import signal
import sys
import time

# Wildcard not good
from gui import *

# Dirty import
sys.path.insert(0, '/Users/jonathan/Documents/Examensarbete/Program/server')
from host import host

# For password encryption, just for prototyping
# Need something stronger
from hashlib import md5

## Used to send packages over the internet
## Serialize objects
from server import host
try:
    import cPickle as pickle
except:
    import pickle


BUFF_SIZE = 4096

##
## 
##
class Client:

    is_connected = False
    is_login = False
    is_running = False
    socket = None
    username = ""

    current_rdp_connection = []

    def __init__(self, socket):
        self.socket = socket
        print('initiating client...')

    def logout(self):

        hosts = []

        for p in self.current_rdp_connection:
            try:
                os.killpg(os.getpgid(p.get('process').pid), signal.SIGTERM)  # Send the signal to all the process groups
                hosts.append(p.get('host'))
            except ProcessLookupError as e:
                print(e)
            
        msg = {
            'command' : 'logout',
            'hosts' : hosts
        }

        self.socket.sendall(pickle.dumps(msg, -1))
        self.current_rdp_connection.clear()


    def login(self, un, pw):
        self.username = un

        msg = {
            'command' : 'login',
            'un' : self.username,
            'pw' : md5(str.encode(pw)).hexdigest()
        }

        msg = pickle.dumps(msg, -1) 

        try:
            self.socket.sendall(msg)
        except BrokenPipeError:
            print('Server seems to be down...')

        if self.socket.recv(1024).decode() == 'auth':
            self.is_login = True
        else:
            self.is_login = False
            print('Wrong user input - Client')

        return self.is_login

    def handle_rdp(self, host):
   
        msg_to_server = {
            'command' : 'rdp',
            'choice' : host
        }

        msg_to_server = pickle.dumps(msg_to_server, -1)
        self.socket.sendall(msg_to_server)

        # Should send the message size as meta data, not hard coded
        msg = pickle.loads(self.socket.recv(BUFF_SIZE))

        with open('id_rsa-cert.pub', 'wb') as f:
            file = msg.get('cert')
            f.write(file)
        f.close()

        os.system('mv id_rsa-cert.pub ~/.ssh')
        print_data = msg.get('command')
        
        self.current_rdp_connection.append({'process' : subprocess.Popen(print_data, stdout=subprocess.PIPE, shell = True, preexec_fn=os.setsid),
                                            'host' : host})
        
        # Will not have the time to create the tunnel else
        time.sleep(1)
        file_to_open = 'open rdpfiles/{}.rdp'.format(host.name)
        subprocess.Popen(file_to_open, shell = True)

    def handle_quit_rdp(self, host):

        msg = {
            'command' : 'q_rdp',
            'host' : host
        }
        self.socket.sendall(pickle.dumps(msg, -1))

        for i, p in enumerate(self.current_rdp_connection):
            if p.get('host').equals(host):
                try:
                    os.killpg(os.getpgid(p.get('process').pid), signal.SIGTERM)  # Send the signal to all the process groups
                    self.current_rdp_connection.pop(i)
                except ProcessLookupError:
                    print('Can not kill that process')
                break

    def start_up(self):
        
        msg = {
            'command' : 'start_up_client'
        }

        self.socket.sendall(pickle.dumps(msg, -1))
        msg = pickle.loads(self.socket.recv(BUFF_SIZE))
        self.hosts = msg.get('hosts')
        self.loginfo = msg.get('loginfo')


    def collect_info(self):

        msg = {
            'command' : 'collect'
        }

        self.socket.sendall(pickle.dumps(msg, -1))
        msg = pickle.loads(self.socket.recv(BUFF_SIZE))
        self.hosts = msg.get('hosts')

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


class Admin(Client):

    users = None

    def __init__(self, socket):
        super(Admin, self).__init__(socket=socket)
        print('initing admin...')

    def collect_info(self):
        msg = {
            'command' : 'collect_info_admin'
        }

        self.socket.sendall(pickle.dumps(msg, -1))
        msg = pickle.loads(self.socket.recv(BUFF_SIZE))
        self.users = msg.get('users')        


if __name__ == '__main__':

    # The script will vary depending on system
    print(sys.platform)

    if len(sys.argv) == 3:
        c = Client(sys.argv[1], int(sys.argv[2]))
        
    else:
        print('Type ip and port')

    