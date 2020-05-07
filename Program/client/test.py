import subprocess
import os

import sys

import struct 

## Used to send packages over the internet
## Serialize objects
try:
    import cPickle as pickle
except:
    import pickle

from hashlib import md5

#subprocess.Popen('ssh -p 2222 pi@88.129.80.84', shell=True)
#subprocess.Popen('/Users/jonathan/Documents/plugg/exjobb/Examensarbete/windows.rdp', shell=True)
#os.system('open windows.rdp')
#os.system('ssh-keygen -s server_ca -I jonathan -n pi -V +1m -z 1 id_rsa.pub')
print(md5(str.encode('test')).hexdigest())

