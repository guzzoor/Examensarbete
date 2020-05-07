#!/usr/bin/env python3

import sys
import time
import select
from os import path

import paramiko
from scp import SCPClient

class ssh:
    def __init__(self, host, port = 22, username = None, password = None):
        self.host = host
        self.ssh = None
        self.port = port
        self.username = username
        self.password = password

    #
    # Try to connect to the host.
    # Retry a few times if it fails.
    #
    def connect(self):

        i = 1

        while True:
            print('Trying to connect to %s' % (self.host)) 
            try:
                self.ssh = paramiko.SSHClient()
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh.connect(self.host, port = self.port, username = self.username, password = self.password)
                print('Connected to %s' & (self.host))
                break
            except paramiko.AuthenticationException:
                print('Authentication failed when connecting to %s' % (self.host))
                sys.exit(1)
            except:
                print ('Could not SSH to %s, waiting for it to start %s' % (self.host))
                i += 1
                time.sleep(2)

            # If we could not connect within time limit
            if i == 30:
                print('Could not connect to %s. Giving up %s' % (self.host))
                sys.exit(1)

    #
    ## ssh commands
    #
    def command(self, command):
        # Send the command (non-blocking)
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return stdout.readlines()

    def scp_upload(self, filename):
        # SCPCLient takes a paramiko transport as an argument
        scp = SCPClient(self.ssh.get_transport())
        scp.put(filename, filename)
        scp.close()


    def scp_download(self, filename):
        # SCPCLient takes a paramiko transport as an argument
        scp = SCPClient(self.ssh.get_transport())
        scp.get(filename)
        scp.close()


        #
        # Disconnect from the host
        #
    def quit(self):    
        print("Command done, closing SSH connection")
        ssh.close()

