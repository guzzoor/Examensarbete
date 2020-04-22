#!/usr/bin/env python3

import socket
import os
import subprocess
import signal
from server import host
try:
    import cPickle as pickle
except:
    import pickle


HOST = '88.129.80.84'  # The server's hostname or IP address
PORT = 65432        # The port used by the server


class client:

    is_connected = False
    is_login = False
    s = None

    work_stations = []

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.s.connect((HOST, PORT))
        msg = self.s.recv(1024).decode()
        if msg == 'connected':
            self.is_connected = True

        return self.is_connected

    def login(self):
        if self.is_connected:
            
            self.s.sendall(str.encode('login'))

            print('Enter your login info...')

            username = input('Enter username: ')
            passwd = input('Enter password: ')

            print('')

            login_info = {
                'un': username,
                'pw': passwd
            }

            msg = pickle.dumps(login_info, -1) 
            self.s.sendall(msg)

            if self.s.recv(1024).decode() == 'auth':
                self.is_login = True

        return self.is_login

    def client_loop(self):
        if self.is_connected and self.is_login:
            is_running = True
            while is_running:
                print('Options\nshow = show all available hosts\nrdp = setup rdp\nquit = quit the program\n')
                message_to_server = input('Enter command: ')
                print()
                self.s.sendall(str.encode(message_to_server))

                if message_to_server == 'show':
                    self.handle_show(message_to_server)

                if message_to_server == 'rdp':
                    self.handle_show('show')
                    self.s.sendall(str.encode(message_to_server))
                    data = self.s.recv(1024)
                    print_data = data.decode()
                    p_rdp = subprocess.Popen(print_data, stdout=subprocess.PIPE, shell = True, preexec_fn=os.setsid)
                    os.system('open windows.rdp')
                    print('You can now use rdp')
                
                if message_to_server == 'q_rdp':
                    self.s.sendall(str.encode(message_to_server))
                    data = self.s.recv(1024)
                    print_data = data.decode() 
                    os.killpg(os.getpgid(p_rdp.pid), signal.SIGTERM)  # Send the signal to all the process groups

                if message_to_server == 'quit':
                    self.s.sendall(str.encode(message_to_server))
                    is_running = False
                    self.s.sendall(str.encode('quit'))
                    print('You terminated the connection.')
    
    def handle_show(self, msg_to_server):
        self.s.sendall(str.encode(msg_to_server))
        data = self.s.recv(4096)
        data = pickle.loads(data)
        for h in data:
            print(h.to_string())
        print()

    #
    ## On start this will collect all relevant info. Like workstations in the system and the current user log.
    #
    def collect_info(self):
        self.s.sendall('collect')
        msg = pickle.loads(self.s.recv(4094))
        print(msg)

    #
    ## Everyone something is updated the server will send a message to all client 
    ## so that they can update their info
    def update_info(self):
        pass


    def main(self):
        if(self.connect() and self.login()):
            print('You are now connected and logged in to the system.\n')
            self.collect_info()
            self.client_loop()
        else:
            print('Could not connect and login.')

    
if __name__ == '__main__':
    c = client()
    c.main()

    