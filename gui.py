from tkinter import *
from client import *

HEIGHT = 724
WIDTH = 1920


class custom_button(Button):

    def __init__(self, r, t, f, option, col):
        super(custom_button, self).__init__(r, text=t, font = f, bg=col)
        self.option = option
        self.color = 'blue'

    def click(self):
        print(self.option)
        return self.option


class GUI:

    root = None
    log_frame = None
    current_rdp_host = None

    def __init__(self):
        self.client = client('127.0.0.1', 1234)
        self.client.connect()
        self.client.login()

    def click(self):
        print('clicked')

    def refresh(self):
        self.client.collect_info()
        hosts = self.client.hosts
        gui.draw_graphics_pic(hosts, self.background_image)

    def connect(self, btn):
        if self.current_rdp_host != None:
            self.client.handle_quit_rdp_one(self.current_rdp_host)
        self.current_rdp_host = btn.option
        self.client.handle_rdp(btn.option)
        self.refresh()


    def print_log(self):
        log = self.client.loginfo
        h = 0
        for r in log:
            l = Label(self.log_frame,  text = r[1] + ' : ' + r[2])
            l.place(relx=0.1, rely = h, relheight=0.05, relwidth=0.8)
            h = h + 0.05

    def create_hosts_new(self, hosts):
        ypos = 0.1
        option = 0
        for h in hosts:
            btn = custom_button(self.host_frame, h.to_string(), 40, option, 'green')
            btn["command"] = lambda btn=btn: self.connect(btn)
            btn.place(relx=0.1, rely = ypos, relheight=0.1, relwidth=0.8)
            ypos = ypos + 0.1
            option = option + 1


    def draw_graphics_pic(self, host, background_image):

        canvas = Canvas(self.root, height=HEIGHT, width=WIDTH)
        canvas.pack()

        background_label = Label(self.root, image=background_image)
        background_label.place(relwidth=1, relheight=1)

        self.log_frame = Frame(self.root, bd=10)
        self.log_frame.place(relx=0.05, rely=0.1, relwidth=0.4, relheight=0.8)


        self.host_frame = Frame(self.root, bd=10)
        self.host_frame.place(relx=0.55, rely=0.1, relwidth=0.4, relheight=0.8)

        self.create_hosts_new(host)
        self.print_log()


        refresh_button = Button(self.host_frame, text='Refresh', command=self.refresh)
        refresh_button.place(relx = 0.6, rely = 0.8, relwidth = 0.3, relheight=0.05)

        quit_button = Button(self.root, text='Quit', command=self.click)
        quit_button.place(relx = 0.4, rely = 0.95, relwidth=0.2)

        userinfo = Label(self.root, text='Signed in as user : ' + self.client.username)
        userinfo.place(relx = 0.2, rely= 0, relwidth=0.6, relheight = 0.1)

    def main(self):

        self.client.collect_info()
        hosts = self.client.hosts
        self.root = Tk()
        self.background_image = PhotoImage(file='Syntronictest.png')
        self.draw_graphics_pic(hosts, self.background_image)
        self.root.update()
        self.root.mainloop()


        '''
        try:
            self.client.collect_info()
            hosts = self.client.hosts
            self.root = Tk()
            self.background_image = PhotoImage(file='Syntronictest.png')
            self.draw_graphics_pic(hosts, self.background_image)
            self.root.update()
            self.root.mainloop()
        except:
            print('Exception')
        
        finally:
            print('Finally')
            # Clean up
            self.client.handle_quit_rdp()
        '''

# Graphics

if __name__ == "__main__":

    gui = GUI()
    gui.main()

