 #!/usr/bin/env python3

import socket
import threading
import sqlite3
from datetime import datetime
import sys
import os

##
## cPickle is faster
##
try:
    import cPickle as pickle
except:
    import pickle

##
## Host/workstation that you can connect to. A user should see of another user is currently using it
## and who that person is 
class host:

    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name
        self.current_user = None
        self.is_used = False

    def to_string(self):
        cu = 'Is available to use'
        if self.is_used:
            cu = 'Is not available to use\nIs used by user: {}'.format(self.current_user)
        return self.name + ': ' + self.ip + ' - ' + cu

    def equals(self, host):
        return self.name == host.name

## 
## So that the server can handle several clients at the same time
##
class client_thread:
    def __init__(self, connection, address, hosts):
        self.address = address
        self.current_user = ""
        self.connection = connection
        self.hosts = hosts
        self.db_conn = sqlite3.connect('server_db.db')

        try:
            self.running()
        except Exception as e:
            print('Exception happened')
        finally:
            print('Closing connections to database...')
            self.db_conn.close()
    
    # Thread main loop
    def running(self):
        self.is_running = True
        while self.is_running:
            print('Waiting for input...')
            data = self.connection.recv(4096)
            print('Recieved input')
          
            msg = pickle.loads(data)

            command = msg.get('command')

            if command == 'login':
                print('login requested by client {}'.format(self.address))
                self.handle_login(msg.get('un'), msg.get('pw'))

            elif command == 'quit':
                print('Client {} chose to terminate the connection.'.format(self.address))
                self.db_handler('Terminated session')
                self.connection.sendall(str.encode('Server terminated your connection'))
                is_running = False

            elif command == 'start_up':
                print('collect requested by client {}'.format(self.address))
                msg = {
                    'hosts' : self.hosts,
                    'loginfo' : self.get_user_data_from_db()
                }

                self.connection.sendall(pickle.dumps(msg, -1))

            elif command == 'collect':
                print('collect requested by client {}'.format(self.address))
                msg = {
                    'hosts' : self.hosts
                }

                self.connection.sendall(pickle.dumps(msg, -1))

            elif command == 'rdp':
                print('rdp requested by client {}'.format(self.address))
                self.handle_rdp(msg.get('choice'))

            elif command == 'q_rdp':
                print('quit rdp requested by client {}'.format(self.address))
                self.handle_quit_rdp(msg.get('host'))

            elif command == 'logout':
                print('lgout requested by client {}'.format(self.address))

                for h  in msg.get('hosts'):
                    self.handle_quit_rdp(h)

            
    def handle_login(self, un, pw):
        
        a = self.db_conn.execute(
            '''
            SELECT * FROM userInfo WHERE un = (?) and pw = (?);
            ''',
            (un, pw)
        ).fetchall()

        # Should be better ways to se if matched
        if len(a) == 1:
            self.current_user = un
            self.db_handler('login')
            self.connection.sendall(str.encode('auth'))
        else:
            print('not auth - Server')
            self.connection.sendall(str.encode('n_auth'))

    # Returns available ssh hosts as a string 
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
            
        os.system('ssh-keygen -s server_ca -I jonathan -n pi -V +5m -z 1 id_rsa.pub')

        fn = 'id_rsa-cert.pub'
        s = os.path.getsize('id_rsa-cert.pub')
        f = open(fn, 'rb')
        l = f.read(s)

        msg = {
            'cert' : l,
            'command' : str.encode('ssh -N -L {}:{}:3389 -p 2222 pi@88.129.80.84'.format(host.port, host.ip))
        }
        
        self.db_handler('RDP-request to host: {}'.format(host.ip))

        self.connection.sendall(pickle.dumps(msg, -1))

    def handle_quit_rdp(self, host):
        for h in self.hosts:
            h = h.get('host')
            if h.equals(host):
                h.is_used = False
                h.current_user = None
                self.db_handler('RDP termination for host {}'.format(host.name))


    def db_handler(self, action):
        self.db_conn.execute(
            '''
            INSERT INTO userlog (username, useraction, loginTime)
                        VALUES (?, ?, ?)
            ''',
            (self.current_user, action, datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        )
        self.db_conn.commit()

    def get_user_data_from_db(self):
        data = self.db_conn.execute(
            '''
            SELECT * FROM userlog WHERE username = (?)
            ''',
            (self.current_user,)
        ).fetchall()        

        return data


# Server class 
class Server:

    clients = []

    w = host('192.168.0.114', 5901, 'Syntronic-Windows')
    p = host('192.168.0.104', 5902, 'Jonathans-Pi')
    m = host('192.168.0.113', 5903, 'Claras-Mac')
    dummy1 = host('111.111.111', 3389, 'Dummy 1')
    dummy2 = host('222.222.222', 3389, 'Dummy 2')
    dummy3 = host('333.333.333', 3389, 'Dummy 3')


    hosts = [
        {
            'host' : w,
            'current_user' : None
        },
        {
            'host' : p,
            'current_user' : None
        },
        {
            'host' : m,
            'current_user' : None
        },
            {
            'host' : dummy1,
            'current_user' : None
        },
            {
            'host' : dummy2,
            'current_user' : None
        },
        {
            'host' : dummy3,
            'current_user' : None
        },
    ]


    def __init__(self, ip, port):
        self.ip = ip
        self. port = port
    
    # Start server
    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip, self.port))
            print('Server started running. Listening on port %s' % (self.port))
            try:
                while True:
                    s.listen()
                    self.conn, self.addr = s.accept()
                    print('Accepted connection from {}'.format(self.addr))
                    t = threading.Thread(target = client_thread, args = (self.conn, self.addr, self.hosts),)
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
