
import tkinter as tk                
from tkinter import font  as tkfont 
from tkinter import messagebox

import socket

from tkmacosx import Button as tkButton

# Wildcard, bad import
from client import *

import os

# Constants
HEIGHT = 800
WIDTH = 1000


# Might be a bit uncessesary
class CustomButton(tkButton):
    ''' tKinterButton that also contains a host attribute. '''
    def __init__(self, r, t, f, col, host):
        super(CustomButton, self).__init__(r, text=t, font = f, bg=col, borderless=1)
        self.host = host

# ---------------------------- GUI App ------------------------------

class GuiApp(tk.Tk):
    ''' Main app for the GUI. Contains the other pages '''
    user = None

    def __init__(self, ip, port):

        self.socket = self.server_connect(ip, port)

        tk.Tk.__init__(self)
        self.geometry('{}x{}'.format(HEIGHT, WIDTH))
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        container = tk.Canvas(self, height=HEIGHT, width=WIDTH)
        container.pack()

        self.frames = {}
        for F in (LoginPage, MainPage, ConnectionPage, AdminPage, UserPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self, socket=self.socket)
            self.frames[page_name] = frame
            frame.place(relx=0,rely=0)

        self.show_frame("LoginPage")

    def show_frame(self, page_name, option=None):
        ''' When called upon it will change page

        Parameters:
        page_name (string): Page to be shown

        option: Various extra option for pages

        '''
        frame = self.frames[page_name]
        frame.tkraise()
        print('Starting fram {}'.format(page_name))
        if page_name == 'ConnectionPage':
            frame.start(option)
        else:
            frame.start()

    def server_connect(self, ip, port):
        ''' Connect to application to a server.

        Param:
        ip (string): IP-adress to connect to
        port (int): port to connect to

        Exception:
        BrokenPipeError: If the server is down

        Return:

        s (socket): Socket that will handle communication between client and server            

        '''

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            s.connect((ip, port))
        except BrokenPipeError:
            print('Server seems to be down...')
        return s

# ---------------------------- Login page -----------------------------

class LoginPage(tk.Frame):
    ''' Start page. Contains login functionality '''

    # Why do I need this?
    root = None

    def __init__(self, parent, controller, socket):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.socket = socket
        self.background_image = tk.PhotoImage(file='pic/Syntronictest1.png')        

    def draw_graphics(self, background_image):
        ''' Will drapw the graphics for the LoginPage 
        
        Param:
        background_image (image) : background image of the page

        '''

        background_label = tk.Label(self.root, image=background_image)
        background_label.place(relwidth=1, relheight=1)

        self.login_frame = tk.Frame(self.root, bd=10)
        self.login_frame.place(relx=0.3, rely=0.2, relwidth=0.4, relheight=0.5)
        self.login_frame.bind('<Return>', self.login) # does not work

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
        ''' Setup function for the current page '''
        canvas = tk.Canvas(self.root, height=HEIGHT, width=WIDTH)
        canvas.pack()
        self.draw_graphics(self.background_image)

    def login(self):
        ''' A function for login to the server '''

        un = self.un_entry.get()

        if(un == 'admin'):
            user = Admin(self.socket)
        else:
            user = Client(self.socket)

        if user.login(self.un_entry.get(), self.pw_entry.get()):
            self.controller.user = user
            if un == 'admin':
                self.controller.show_frame('AdminPage')
            else:
                self.controller.show_frame("MainPage")
        else:
            messagebox.showinfo('ERROR', 'Wrong user input')

# ---------------------------- Main page -------------------------------

class MainPage(tk.Frame):
    ''' '''

    root = None
    log_frame = None
    current_rdp_host = None

    def __init__(self, parent, controller, socket):
        ''' '''
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.background_image = tk.PhotoImage(file='pic/Syntronictest1.png')        

    def quit_rdp(self):
        ''' '''
        self.controller.user.handle_quit_rdp(self.current_rdp_host)

    def logout(self):
        ''' '''
        print('Logout pressed')
        self.controller.user.logout()
        self.controller.show_frame('LoginPage')
        self.after_cancel(self.current_job)


    def refresh(self):
        ''' '''
        self.controller.user.collect_info()
        self.hosts = self.controller.user.hosts
        self.draw_graphics(self.background_image)
        
        self.current_job = self.after(5000, self.refresh)

    def connect(self, btn):
        ''' '''
        prev_host = self.current_rdp_host
        self.current_rdp_host = btn.host
        if not btn.host.is_used:
            self.client.handle_rdp(btn.host, prev_host)

    def show_host(self, btn):
        ''' '''
        self.after_cancel(self.current_job)
        self.controller.show_frame('ConnectionPage', btn.host)

    def print_user_info(self):
        ''' '''
        userinfo = tk.Label(self.root, text='Signed in as user:\n  ' + self.controller.user.username)
        userinfo.place(relx = 0.8, rely= 0.05, relwidth=0.15, relheight = 0.1)

    def print_log(self):
        ''' '''
        log = self.controller.user.loginfo
        log.reverse()
        label = tk.Label(self.log_frame, text='USER LOG', bg='lightblue')
        label.place(relx=0, rely=0, relwidth=1, relheight=0.1)
        ypos = 0.12
        for r in log:
            l = tk.Label(self.log_frame,  text = r[2] + ' \n ' + r[3])
            l.place(relx=0, rely = ypos, relheight=0.075, relwidth=0.9)
            ypos = ypos + 0.1

    def print_hosts(self):
        ''' '''
        label = tk.Label(self.host_frame, text='ALL HOSTS', bg='lightblue')
        label.place(relx=0, rely=0, relwidth=1, relheight=0.1)

        ypos = 0.12
        option = 0
        for h in self.hosts:
            h = h.get('host')
            col = 'lightgreen'
            if h.is_used:
                btn = CustomButton(self.host_frame, h.to_string(), 40, 'red', h)   
            else:
                btn = CustomButton(self.host_frame, h.to_string(), 40, 'lightgreen', h)   

            btn["command"] = lambda btn=btn: self.show_host(btn)
            btn.place(relx=0, rely = ypos, relheight=0.1, relwidth=1)
            ypos = ypos + 0.1
            option = option + 1

    def draw_graphics(self, background_image):
        ''' '''
        background_label = tk.Label(self.root, image=background_image)
        background_label.place(relwidth=1, relheight=1)

        self.host_frame = tk.Frame(self.root, bd=10)
        self.host_frame.place(relx=0.3, rely=0.2, relwidth=0.6, relheight=0.7)

        self.print_hosts()
        self.print_user_info()

        logout_buttom = tkButton(self.root, text='Logout', bg='lightblue', command=self.logout)
        logout_buttom.place(relx=0.75, rely=0.85,relwidth=0.15,relheight=0.07)

    def start(self):
        ''' Setup function for the current page '''
        self.controller.user.start_up()       
        self.hosts = self.controller.user.hosts
        canvas = tk.Canvas(self.root, height=HEIGHT, width=WIDTH)
        canvas.pack()
        self.refresh()


# --------------------------- Admin page -------------------------
class AdminPage(tk.Frame):
    ''' '''
    root = None
    log_frame = None
    current_rdp_host = None

    def __init__(self, parent, controller, socket):
        ''' '''
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.background_image = tk.PhotoImage(file='pic/Syntronictest1.png')        

    def logout(self):
        ''' '''
        print('Logout pressed')
        self.controller.user.logout()
        self.controller.show_frame('LoginPage')
        self.after_cancel(self.current_job)

    def refresh(self):
        ''' '''
        self.controller.user.collect_info()
        self.draw_graphics(self.background_image)
        self.current_job = self.after(5000, self.refresh)


    def print_user_info(self):
        ''' '''
        userinfo = tk.Label(self.root, text='Signed in as user:\n  ' + self.controller.user.username)
        userinfo.place(relx = 0.8, rely= 0.05, relwidth=0.15, relheight = 0.1)

    def print_users(self):
        ''' '''
        label = tk.Label(self.host_frame, text='ALL USERS', bg='lightblue')
        label.place(relx=0, rely=0, relwidth=1, relheight=0.1)

        ypos = 0.12
        option = 0
        for u in self.controller.user.users:
            col = 'lightgreen'
            if u[1]:
                btn = CustomButton(self.host_frame, u[0], 40, 'red', u)   
            else:
                btn = CustomButton(self.host_frame, u[0], 40, 'lightgreen', u)   

            btn["command"] = lambda btn=btn: self.show_user(btn.host)
            btn.place(relx=0, rely = ypos, relheight=0.1, relwidth=1)
            ypos = ypos + 0.1
            option = option + 1

    def show_user(self, host):
        self.after_cancel(self.current_job)
        self.controller.show_frame('UserPage', host)


    def draw_graphics(self, background_image):
        ''' '''
        background_label = tk.Label(self.root, image=background_image)
        background_label.place(relwidth=1, relheight=1)

        self.host_frame = tk.Frame(self.root, bd=10)
        self.host_frame.place(relx=0.3, rely=0.2, relwidth=0.6, relheight=0.7)

        self.print_users()
        self.print_user_info()

        logout_buttom = tkButton(self.root, text='Logout', bg='lightblue', command=self.logout)
        logout_buttom.place(relx=0.75, rely=0.85,relwidth=0.15,relheight=0.07)

    def start(self):
        ''' Setup function for the current page '''     
        canvas = tk.Canvas(self.root, height=HEIGHT, width=WIDTH)
        canvas.pack()
        self.refresh()

# ------------------------ Connection frame ------------------------

class ConnectionPage(tk.Frame):
    ''' '''
    root = None
    host = None

    def __init__(self, parent, controller, socket):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.background_image = tk.PhotoImage(file='pic/Syntronictest1.png')        

    def draw_host_info(self):
        ''' '''
        if self.host.current_user == self.controller.user.username:
            col = 'red'
            text='Disconnect from RDP'
            command = lambda : self.disconnect()

        elif self.host.is_used:
            col = 'red'
            text='Join RDP'
            command = lambda : self.join()
        else:
            col='lightgreen'
            command = lambda : self.connect()
            text = 'Connect to RDP'


        label = tk.Label(self.frame, text=self.host.to_string(), bg=col)
        label.place(relx=0, rely=0, relwidth=1, relheight=0.2)  
        
        connect_button = tkButton(self.frame, text=text, bg='lightblue', command=command)
        connect_button.place(relx = 0.1, rely = 0.22, relwidth = 0.4, relheight=0.1)        

        connect_button = tkButton(self.frame, text='SSH-connection', bg='lightblue', command=command)
        connect_button.place(relx = 0.5, rely = 0.22, relwidth = 0.4, relheight=0.1)     

    def draw_graphics(self):
        ''' '''
        background_label = tk.Label(self.root, image=self.background_image)
        background_label.place(relwidth=1, relheight=1)

        self.frame = tk.Frame(self.root, bd=10)
        self.frame.place(relx=0.1, rely=0.05, relwidth=0.8, relheight=0.8)

        self.draw_host_info()             

        back_button = tkButton(self.frame, text='Back', bg='lightblue', command=self.back)
        back_button.place(relx = 0.3, rely = 0.8, relwidth = 0.4, relheight=0.1)

    def back(self):
        ''' '''
        self.controller.show_frame('MainPage')

    def connect(self):
        ''' '''
        if not self.host.is_used:
            self.controller.user.handle_rdp(self.host)
            self.back()

        else: 
            messagebox.showinfo('ERROR', 'Station is already in use by\nuser {}'.format(self.host.current_user))

    def disconnect(self):
        ''' '''
        self.controller.user.handle_quit_rdp(self.host)
        self.back()

    def join(self):
        ''' '''
        print("join")

    def start(self, host):
        ''' Setup function for the current page '''
        self.host = host
        canvas = tk.Canvas(self.root, height=HEIGHT, width=WIDTH)
        canvas.pack()
        self.draw_graphics()

# ----------------------------- User page ----------------------------
class UserPage(tk.Frame):
    ''' '''
    root = None

    def __init__(self, parent, controller, socket):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.background_image = tk.PhotoImage(file='pic/Syntronictest1.png')        

    def draw_graphics(self):
        ''' '''
        background_label = tk.Label(self.root, image=self.background_image)
        background_label.place(relwidth=1, relheight=1)

        self.frame = tk.Frame(self.root, bd=10)
        self.frame.place(relx=0.1, rely=0.05, relwidth=0.8, relheight=0.8)

        self.draw_host_info()             

        back_button = tkButton(self.frame, text='Back', bg='lightblue', command=self.back)
        back_button.place(relx = 0.3, rely = 0.8, relwidth = 0.4, relheight=0.1)

    def back(self):
        ''' '''
        self.controller.show_frame('MainPage')
   
    def start(self, host):
        ''' Setup function for the current page '''
        canvas = tk.Canvas(self.root, height=HEIGHT, width=WIDTH)
        canvas.pack()
        self.draw_graphics()



# ----------------------------- Start ----------------------------


if __name__ == "__main__":
    try: 
        app = GuiApp('127.0.0.1' , 1234)
        app.mainloop()
    except Exception as e:
        print(e)
        print('Exception happened')
    finally:
        print('Finally happened')
        app.user.logout() # Should be some form of clean up function
        

