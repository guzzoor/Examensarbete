
import tkinter as tk                # python 3
from tkinter import font  as tkfont # python 3
from tkinter import messagebox

from tkmacosx import Button as tkButton

from client import *

HEIGHT = 724
WIDTH = 1000

class custom_button(tkButton):
    def __init__(self, r, t, f, col, host):
        super(custom_button, self).__init__(r, text=t, font = f, bg=col, borderless=1)
        self.host = host


# ---------------------------- GUI App ------------------------------

class GuiApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        self.client = client('127.0.0.1', 1234)
        self.client.connect()

        tk.Tk.__init__(self)
        self.geometry('1000x800')
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        container = tk.Canvas(self, height=HEIGHT, width=WIDTH)
        container.pack()

        self.frames = {}
        for F in (LoginPage, MainPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self, client = self.client)
            self.frames[page_name] = frame

            frame.place(relx=0,rely=0)

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
        print('Starting fram {}'.format(page_name))
        frame.start()

# ---------------------------- Login page -----------------------------

class LoginPage(tk.Frame):
    root = None

    def __init__(self, parent, controller, client):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.client = client
        self.background_image = tk.PhotoImage(file='Syntronictest1.png')        

    def draw_graphics_pic(self, background_image):

        background_label = tk.Label(self.root, image=background_image)
        background_label.place(relwidth=1, relheight=1)

        self.login_frame = tk.Frame(self.root, bd=10)
        self.login_frame.place(relx=0.3, rely=0.2, relwidth=0.4, relheight=0.5)

        text_un = tk.Label(self.login_frame, text='Username')
        text_un.place(relx=0.3, rely=0.25)

        text_pw = tk.Label(self.login_frame, text='Password')
        text_pw.place(relx=0.3, rely=0.45)
        
        self.un_entry = tk.Entry(self.login_frame)
        self.pw_entry = tk.Entry(self.login_frame, show='*')
        self.un_entry.place(relx=0.3, rely=0.3, relwidth=0.4, relheight=0.1)
        self.pw_entry.place(relx=0.3, rely=0.5, relwidth=0.4, relheight=0.1)

        login_button = tkButton(self.login_frame, text='Login', bg='lightblue', command=self.login)
        login_button.place(relx = 0.3, rely = 0.9, relwidth = 0.4, relheight=0.1)


    def start(self):
        canvas = tk.Canvas(self.root, height=HEIGHT, width=WIDTH)
        canvas.pack()
        self.draw_graphics_pic(self.background_image)

    def login(self):
        print('log in button pressed')
        if self.client.login(self.un_entry.get(), self.pw_entry.get()):
            print('logging in')
            self.controller.show_frame("MainPage")
        else:
            print('Wrong input')
            messagebox.showinfo('ERROR', 'Wrong user input')


# ---------------------------- Main page -------------------------------

class MainPage(tk.Frame):

    root = None
    log_frame = None
    current_rdp_host = None

    def __init__(self, parent, controller, client):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.client = client
        self.background_image = tk.PhotoImage(file='Syntronictest1.png')        

    def quit_rdp(self):
        self.client.handle_quit_rdp(self.current_rdp_host)

    def logout(self):
        print('Logout pressed')
        self.controller.show_frame('LoginPage')

    def refresh(self):
        self.client.collect_info()
        self.hosts = self.client.hosts
        self.draw_graphics_pic(self.background_image)
        self.after(5000, self.refresh)

    def connect(self, btn):

        prev_host = self.current_rdp_host
        self.current_rdp_host = btn.host
        if not btn.host.is_used:
            self.client.handle_rdp(btn.host, prev_host)
        self.refresh()

    def print_user_info(self):
        userinfo = tk.Label(self.root, text='Signed in as user:\n  ' + self.client.username)
        userinfo.place(relx = 0.8, rely= 0.05, relwidth=0.15, relheight = 0.1)


    def print_log(self):
        log = self.client.loginfo
        log.reverse()
        label = tk.Label(self.log_frame, text='USER LOG', bg='lightblue')
        label.place(relx=0, rely=0, relwidth=1, relheight=0.1)
        ypos = 0.12
        for r in log:
            l = tk.Label(self.log_frame,  text = r[2] + ' \n ' + r[3])
            l.place(relx=0, rely = ypos, relheight=0.075, relwidth=0.9)
            ypos = ypos + 0.1

    def print_hosts(self):

        label = tk.Label(self.host_frame, text='ALL HOSTS', bg='lightblue')
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

        background_label = tk.Label(self.root, image=background_image)
        background_label.place(relwidth=1, relheight=1)

        self.log_frame = tk.Frame(self.root, bd=10)
        self.log_frame.place(relx=0.05, rely=0.2, relwidth=0.4, relheight=0.7)


        self.host_frame = tk.Frame(self.root, bd=10)
        self.host_frame.place(relx=0.55, rely=0.2, relwidth=0.4, relheight=0.7)

        self.print_hosts()
        self.print_user_info()

        refresh_button = tkButton(self.host_frame, text='Terminate RDP', bg='lightblue', command=self.quit_rdp)
        refresh_button.place(relx = 0.3, rely = 0.9, relwidth = 0.4, relheight=0.1)

        logout_buttom = tkButton(self.root, text='Logout', bg='lightblue', command=self.logout)
        logout_buttom.place(relx=0.4, rely=0.9,relwidth=0.2,relheight=0.07)

    def start(self):
        self.client.start_up()       
        self.hosts = self.client.hosts
        canvas = tk.Canvas(self.root, height=HEIGHT, width=WIDTH)
        canvas.pack()
        self.draw_graphics_pic(self.background_image)
        self.print_log()



# ----------------------------- Start ----------------------------

if __name__ == "__main__":

    app = GuiApp()
    app.mainloop()

