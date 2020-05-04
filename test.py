import subprocess
import os

from hashlib import md5

#subprocess.Popen('ssh -p 2222 pi@88.129.80.84', shell=True)
#subprocess.Popen('/Users/jonathan/Documents/plugg/exjobb/Examensarbete/windows.rdp', shell=True)
#os.system('open windows.rdp')
#os.system('ssh-keygen -s server_ca -I jonathan -n pi -V +1m -z 1 id_rsa.pub')
#print(md5(str.encode('test')).hexdigest())

os.system('ssh -p 2222 pi@88.129.80.84')
