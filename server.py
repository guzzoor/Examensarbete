#!/usr/bin/env python3

import socket
import threading
import sqlite3
from datetime import datetime

try:
    import cPickle as pickle
except:
    import pickle

from ssh import ssh

# pi-ip = 88.129.80.84

#
##  
#
class host:

    def __init__(self, ip, ssh_port, rdp_port, name):
        self.ip = ip
        self.ssh_port = ssh_port
        self.rdp_port = rdp_port
        self.name = name

        self.in_use = False
        self.current_user = None
    
    def user_connect(self):
        pass

    def user_disconnect(self):
        pass

    def to_string(self):
        return self.name + ': ' + self.ip 


class client_thread:
    def __init__(self, connection, address, hosts):
        self.address = address
        self.connection = connection
        self.hosts = hosts
        self.ssh = None
        self.conn = sqlite3.connect('test.db')
        print(str(datetime.now()))
        self.conn.execute(
            ''' INSERT INTO userlog (userInfo, loginTime) VALUES(?, ?)''',
            (str(self.address), str(datetime.now()))
        )
        self.conn.commit()
        self.running()

    #
    ## Thread main loop
    #
    def running(self):
        is_running = True
        while is_running:
            data = self.connection.recv(1024)
            msg = data.decode()

            if msg == 'login':
                print(f'login requested by client {self.address}')
                self.handle_login()

            elif msg == 'quit':
                print(f'Client {self.address} chose to terminate the connection.')
                is_running = False

            elif msg == 'show':
                print(f'show requested by client {self.address}')
                msg = pickle.dumps(self.hosts, -1)
                self.connection.sendall(msg)

            elif msg == 'ssh':
                print(f'ssh requested by client {self.address}')
                self.handle_ssh()
            
            elif msg == 'scp':
                print(f'scp requested by client {self.address}')
                self.handle_scp()

            elif msg == 'rdp':
                print(f'rdp requested by client {self.address}')
                self.handle_rdp()

            elif msg == 'q_rdp':
                print(f'quit rdp requested by client {self.address}')
                self.connection.sendall(str.encode('The server has now terminated your connection to rdp.'))

    def handle_login(self):
        data = self.connection.recv(1024)
        dec_msg = pickle.loads(data)
        if dec_msg.get('un') == 'j' and dec_msg.get('pw') == '1':
            self.connection.sendall(str.encode('auth'))

    #
    ## Returns available ssh hosts as a string 
    #
    def print_msg_ssh_hosts(self, start_msg):
        msg = f'{start_msg}\n'
        for h, i in enumerate(self.ssh_hosts, start = 1):
            msg = f'{msg}{h}. {i}\n'
        return msg

    #
    ## ssh handler
    #  Setup ssh connection
    def handle_ssh(self):
        print('Client requested ssh-service')
        self.connection.sendall(str.encode('ssh -N -L 5905:192.168.0.104:22 -p 3022 clarastockhaus@88.129.80.84'))


    #
    ## A method for transfering files between computers
    #
    def handle_scp(self):
        pass


    def handle_rdp(self):
        print('Client requested rdp-service')
        self.connection.sendall(str.encode('ssh -N -L 5901:192.168.0.114:3389 -p 2222 pi@88.129.80.84'))


#
## Server class 
#
class Server:

    clients = []

    w = host('192.168.0.114', 22, 3389, 'Syntronic-Windows')
    p = host('192.168.0.103', 22, 3399, 'Jonathans-Pi')

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
            print(f'Server started running. Listening on port {self.port}')
            while True:
                s.listen()
                self.conn, self.addr = s.accept()
                print(f'Accepted connection from {self.addr}')
                self.conn.sendall(str.encode('connected'))
                t = threading.Thread(target = client_thread, args = (self.conn, self.addr, self.hosts),)
                self.clients.append(t)
                t.start()


if __name__ == '__main__':
    server = Server('127.0.0.1', 65432)
    server.start_server()
