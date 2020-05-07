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