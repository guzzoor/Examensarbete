#!/usr/bin/env python3

import socket
import threading
import sqlite3
from datetime import datetime
import sys
import os

try:
    import cPickle as pickle
except:
    import pickle

from ssh import ssh

# pi-ip = 88.129.80.84


# Global - All active users
ACTIVE_USERS = []

#
## Could also just be saved as json or dictionary
#
class host:

    is_used = False

    def __init__(self, ip, rdp_port, name):
        self.ip = ip
        self.rdp_port = rdp_port
        self.name = name
        self.current_user = None
    
    def user_connect(self):
        pass

    def user_disconnect(self):
        pass

    def to_string(self):
        cu = 'Is available to use'
        if self.is_used:
            cu = 'Is not available to use' 
        return self.name + ': ' + self.ip + ' - ' + cu


class client_thread:
    def __init__(self, connection, address, hosts):
        self.address = address
        self.connection = connection
        self.hosts = hosts
        self.ssh = None
        self.conn = sqlite3.connect('test.db')
        print(str(datetime.now()))
        self.conn.commit()
        self.running()

    #
    ## Thread main loop
    #
    def running(self):
        is_running = True
        while is_running:

            data = self.connection.recv(4096)
            msg = pickle.loads(data)

            command = msg.get('command')

            print(command)

            if command == 'login':
                print('login requested by client {}'.format(self.address))
                self.handle_login(msg.get('un'), msg.get('pw'))

            elif command == 'quit':
                print('Client {} chose to terminate the connection.'.format(self.address))
                self.connection.sendall(str.encode('Server terminated your connection'))
                is_running = False

            elif command == 'collect':
                print('collect requested by client {}'.format(self.address))
                msg = {
                    'hosts' : self.hosts,
                    'loginfo' : 'Lorem Ipsum'
                }

                self.connection.sendall(pickle.dumps(msg, -1))

            elif command == 'rdp':
                print('rdp requested by client {}'.format(self.address))
                self.handle_rdp(msg.get('choice'))

            elif command == 'q_rdp':
                print('quit rdp requested by client {}'.format(self.address))
                self.connection.sendall(str.encode('The server has now terminated your connection to rdp.'))

    def handle_login(self, un, pw):
        
        a = self.conn.execute(
            '''
            SELECT * FROM userInfo WHERE un = (?) and pw = (?);
            ''',
            (un, pw)
        ).fetchall()

        if len(a) == 1:
            self.connection.sendall(str.encode('auth'))

    #
    ## Returns available ssh hosts as a string 
    #
    def print_msg_ssh_hosts(self, start_msg):
        msg = '{}\n'.format(start_msg)
        for h, i in enumerate(self.ssh_hosts, start = 1):
            msg = '{} {}. {}\n'.format(msg, i, h)
        return msg

    def handle_rdp(self, host):
        print('Client requested rdp-service')
        
        os.system('ssh-keygen -s server_ca -I jonathan -n pi -V +1m -z 1 id_rsa.pub')

        fn = 'id_rsa-cert.pub'
        s = os.path.getsize('id_rsa-cert.pub')
        f = open(fn, 'rb')
        l = f.read(2027)
        print(s)

        self.connection.sendall(l)

        self.connection.sendall(str.encode('ssh -N -L 5901:{}:3389 -p 2222 pi@88.129.80.84'.format(host.ip)))


#
## Server class 
#
class Server:

    clients = []

    w = host('192.168.0.114', 3389, 'Syntronic-Windows')
    p = host('192.168.0.104', 3389, 'Jonathans-Pi')

    hosts = [w, p]


    def __init__(self, ip, port):
        self.ip = ip
        self. port = port
    #
    ## Start server
    #
    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip, self.port))
            print('Server started running. Listening on port %s' % (self.port))
            while True:
                s.listen()
                self.conn, self.addr = s.accept()
                print('Accepted connection from {}'.format(self.addr))
                t = threading.Thread(target = client_thread, args = (self.conn, self.addr, self.hosts),)
                ACTIVE_USERS.append(t)
                self.clients.append(t)
                t.daemon = True
                t.start()
                


if __name__ == '__main__':
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = sys.argv[2]
        server = Server(ip, (int(port)))
        server.start_server()
    else:
        print('Provide ip and port number')
