 #!/usr/bin/env python3

import socket
import threading
import sqlite3
from datetime import datetime
import sys
import os

# Bad import
from host import *

from db_handler import *

try:
    import cPickle as pickle
except:
    import pickle

BUFF_SIZE = 4096 # 4kb

class ClientThread:
    def __init__(self, connection, address, hosts):
        self.address = address
        self.current_user = ""
        self.connection = connection
        self.hosts = hosts
        self.db_handler = DatabaseHandler('database/server_db.db')

    #try:
        self.running()
    #except Exception as e:
        print('Exception happened')
    #finally:
        print('Closing connections to database...')
    
    def running(self):
        self.is_running = True
        while self.is_running:
            print('Waiting for input...')
            data = self.connection.recv(BUFF_SIZE)
            print('Recieved input')
          
            msg = pickle.loads(data)

            command = msg.get('command')

            if command == 'login':
                print('login requested by client {}'.format(self.address))
                self.handle_login(msg.get('un'), msg.get('pw'))

            elif command == 'quit':
                print('Client {} chose to terminate the connection.'.format(self.address))
                #self.db_handler('Terminated session')
                self.connection.sendall(str.encode('Server terminated your connection'))
                is_running = False

            elif command == 'start_up_client':
                print('collect requested by client {}'.format(self.address))
                msg = {
                    'hosts' : self.hosts,
                    'loginfo' : self.db_handler.get_user_log(self.current_user)
                }

                self.connection.sendall(pickle.dumps(msg, -1))

            elif command == 'start_up_admin':
                pass

            elif command == 'collect':
                print('collect requested by client {}'.format(self.address))
                msg = {
                    'hosts' : self.hosts
                }
                self.connection.sendall(pickle.dumps(msg, -1))

            elif command == 'collect_info_admin':
                print('collect requested by admin {}'.format(self.address))
                msg = {
                    'users' : self.db_handler.get_all_user()
                }
                self.connection.sendall(pickle.dumps(msg, -1))


            elif command == 'rdp':
                print('rdp requested by client {}'.format(self.address))
                self.handle_rdp(msg.get('choice'))

            elif command == 'q_rdp':
                print('quit rdp requested by client {}'.format(self.address))
                self.handle_quit_rdp(msg.get('host'))

            elif command == 'logout':
                print('logout requested by client {}'.format(self.address))

                self.db_handler.logout(self.current_user)

                for h  in msg.get('hosts'):
                    self.handle_quit_rdp(h)

            
    def handle_login(self, un, pw):
        
        if self.db_handler.login(un, pw):
            self.current_user = un
            self.db_handler.insert('login', self.current_user)
            self.connection.sendall(str.encode('auth'))
        else:
            print('not auth - Server')
            self.connection.sendall(str.encode('n_auth'))

    def print_msg_ssh_hosts(self, start_msg):
        msg = '{}\n'.format(start_msg)
        for h, i in enumerate(self.ssh_hosts, start = 1):
            msg = '{} {}. {}\n'.format(msg, i, h)
        return msg

    def handle_rdp(self, host):
        print('Client requested rdp-service')
        for h in self.hosts:
            if h.get('host').equals(host):
                h.get('host').is_used = True
                h.get('host').current_user = self.current_user
                h['current_user'] = self.current_user
            
        os.system('ssh-keygen -s cert/server_ca -I {} -n pi -V +5m -z 1 cert/id_rsa.pub'.format(self.current_user))

        fn = 'cert/id_rsa-cert.pub'
        s = os.path.getsize(fn)
        f = open(fn, 'rb')
        l = f.read(s)

        msg = {
            'cert' : l,
            'command' : str.encode('ssh -N -L {}:{}:3389 -p 2222 pi@88.129.80.84'.format(host.port, host.ip))
        }
        
        self.db_handler.insert('RDP-request to host: {}'.format(host.ip), self.current_user)
        self.connection.sendall(pickle.dumps(msg, -1))

    def handle_quit_rdp(self, host):
        for h in self.hosts:
            h = h.get('host')
            if h.equals(host):
                h.is_used = False
                h.current_user = None
                self.db_handler.insert('RDP termination for host {}'.format(host.name), self.current_user)

class Server:

    clients = []
    hosts = [
        {
            'host' : host('192.168.0.114', 5901, 'Syntronic-Windows'),
            'current_user' : None
        },
        {
            'host' : host('192.168.0.104', 5902, 'Jonathans-Pi'),
            'current_user' : None
        },
        {
            'host' : host('192.168.0.113', 5903, 'Claras-Mac'),
            'current_user' : None
        },
            {
            'host' : host('111.111.111', 3389, 'Dummy 1'),
            'current_user' : None
        },
            {
            'host' : host('222.222.222', 3389, 'Dummy 2'),
            'current_user' : None
        },
        {
            'host' : host('333.333.333', 3389, 'Dummy 3'),
            'current_user' : None
        },
    ]

    def __init__(self, ip, port):
        self.ip = ip
        self. port = port
    
    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip, self.port))
            print('Server started running. Listening on port %s' % (self.port))
            try:
                while True:
                    s.listen()
                    self.conn, self.addr = s.accept()
                    print('Accepted connection from {}'.format(self.addr))
                    t = threading.Thread(target = ClientThread, args = (self.conn, self.addr, self.hosts),)
                    self.clients.append(t)
                    t.daemon = True
                    t.start()
            except Exception as e:
                print('Exception occured ' + e)

            finally:
                print('Cleaning up...')

if __name__ == '__main__':
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = sys.argv[2]
        server = Server(ip, (int(port)))
        server.start_server()
    else:
        print('Provide ip and port number')
