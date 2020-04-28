
from tkinter import *

from tkmacosx import Button as tkButton


from client import *

HEIGHT = 724
WIDTH = 1000


class custom_button(tkButton):

    def __init__(self, r, t, f, option, col):
        super(custom_button, self).__init__(r, text=t, font = f, bg=col, borderless=1)
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
        gui.draw_graphics_pic(self.background_image)

    def connect(self, btn):
        if self.current_rdp_host != None:
            self.client.handle_quit_rdp_one(self.current_rdp_host)
        self.current_rdp_host = btn.option
        self.client.handle_rdp(btn.option)
        self.refresh()

    def print_user_info(self):
        userinfo = Label(self.root, text='Signed in as user : ' + self.client.username)
        userinfo.place(relx = 0.8, rely= 0.05, relwidth=0.15, relheight = 0.1)


    def print_log(self):
        log = self.client.loginfo
        label = Label(self.log_frame, text='USER LOG', bg='lightblue')
        label.place(relx=0, rely=0, relwidth=1, relheight=0.1)
        ypos = 0.12
        for r in log:
            l = Label(self.log_frame,  text = r[2] + ' : ' + r[3])
            l.place(relx=0.1, rely = ypos, relheight=0.05, relwidth=0.8)
            ypos = ypos + 0.05

    def print_hosts(self):

        label = Label(self.host_frame, text='ALL HOSTS', bg='lightblue')
        label.place(relx=0, rely=0, relwidth=1, relheight=0.1)

        ypos = 0.12
        option = 0
        for h in self.hosts:
            btn = custom_button(self.host_frame, h.to_string(), 40, option, 'lightgreen')
            btn["command"] = lambda btn=btn: self.connect(btn)
            btn.place(relx=0, rely = ypos, relheight=0.1, relwidth=1)
            ypos = ypos + 0.1
            option = option + 1


    def draw_graphics_pic(self, background_image):

        canvas = Canvas(self.root, height=HEIGHT, width=WIDTH)
        canvas.pack()

        background_label = Label(self.root, image=background_image)
        background_label.place(relwidth=1, relheight=1)

        self.log_frame = Frame(self.root, bd=10)
        self.log_frame.place(relx=0.05, rely=0.2, relwidth=0.4, relheight=0.7)


        self.host_frame = Frame(self.root, bd=10)
        self.host_frame.place(relx=0.55, rely=0.2, relwidth=0.4, relheight=0.7)

        self.print_hosts()
        self.print_log()
        self.print_user_info()

        refresh_button = tkButton(self.host_frame, text='Refresh', command=self.refresh, bg='lightblue')
        refresh_button.place(relx = 0.3, rely = 0.9, relwidth = 0.4, relheight=0.1)

        quit_button = tkButton(self.root, background='white', text='Quit', command=self.click)
        quit_button.place(relx = 0.4, rely = 0.95, relwidth=0.2)


    def main(self):

        self.client.collect_info()
        self.hosts = self.client.hosts
        self.root = Tk()
        self.background_image = PhotoImage(file='Syntronictest1.png')
        self.draw_graphics_pic(self.background_image)
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

