
from tkinter import *
from tkinter import ttk
from tkmacosx import Button as tkButton


from client import *

HEIGHT = 724
WIDTH = 1000


class custom_button(tkButton):

    def __init__(self, r, t, f, col, host):
        super(custom_button, self).__init__(r, text=t, font = f, bg=col, borderless=1)
        self.host = host
    

    def click(self):
        print(self.option)
        return self.option


class GUI(object):

    root = None
    log_frame = None
    current_rdp_host = None

    def __init__(self):
        self.client = client('127.0.0.1', 1234)
        self.client.connect()
        self.client.login()
        self.client.collect_info()
        
        self.hosts = self.client.hosts
        self.root = Tk()
        self.background_image = PhotoImage(file='Syntronictest1.png')        

        self.start()

    def click(self):
        print('clicked')

    def quit_rdp(self):
        self.client.handle_quit_rdp(self.current_rdp_host)

    def refresh(self):
        self.client.collect_info()
        self.hosts = self.client.hosts
        self.draw_graphics_pic(self.background_image)
        self.root.after(5000, self.refresh)

    def connect(self, btn):

        prev_host = self.current_rdp_host
        self.current_rdp_host = btn.host
        if not btn.host.is_used:
            self.client.handle_rdp(btn.host, prev_host)
        self.refresh()

    def print_user_info(self):
        userinfo = Label(self.root, text='Signed in as user:\n  ' + self.client.username)
        userinfo.place(relx = 0.8, rely= 0.05, relwidth=0.15, relheight = 0.1)


    def print_log(self):
        log = self.client.loginfo
        label = Label(self.log_frame, text='USER LOG', bg='lightblue')
        label.place(relx=0, rely=0, relwidth=1, relheight=0.1)
        ypos = 0.12
        for r in log:
            l = Label(self.log_frame,  text = r[2] + ' \n ' + r[3])
            l.place(relx=0, rely = ypos, relheight=0.075, relwidth=0.9)
            ypos = ypos + 0.1

    def print_hosts(self):

        label = Label(self.host_frame, text='ALL HOSTS', bg='lightblue')
        label.place(relx=0, rely=0, relwidth=1, relheight=0.1)

        ypos = 0.12
        option = 0
        for h in self.hosts:
            col = 'lightgreen'
            if h.is_used:
                btn = custom_button(self.host_frame, h.to_string(), 40, 'red', h)   
            else:
                btn = custom_button(self.host_frame, h.to_string(), 40, 'lightgreen', h)   

            btn["command"] = lambda btn=btn: self.connect(btn)
            btn.place(relx=0, rely = ypos, relheight=0.1, relwidth=1)
            ypos = ypos + 0.1
            option = option + 1


    def draw_graphics_pic(self, background_image):



        background_label = Label(self.root, image=background_image)
        background_label.place(relwidth=1, relheight=1)

        self.log_frame = Frame(self.root, bd=10)
        self.log_frame.place(relx=0.05, rely=0.2, relwidth=0.4, relheight=0.7)


        self.host_frame = Frame(self.root, bd=10)
        self.host_frame.place(relx=0.55, rely=0.2, relwidth=0.4, relheight=0.7)

        self.print_hosts()
        self.print_log()
        self.print_user_info()

        refresh_button = tkButton(self.host_frame, text='Terminate RDP', bg='lightblue', command=self.quit_rdp)
        refresh_button.place(relx = 0.3, rely = 0.9, relwidth = 0.4, relheight=0.1)

        quit_button = tkButton(self.root, background='lightblue', text='Quit', command=self.click)
        quit_button.place(relx = 0.4, rely = 0.92, relwidth=0.2, relheight=0.05)


    def start(self):

        canvas = Canvas(self.root, height=HEIGHT, width=WIDTH)
        canvas.pack()
        #self.draw_graphics_pic(self.background_image)
        self.refresh()
        self.root.mainloop()
        #self.client.handle_quit_rdp()


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


