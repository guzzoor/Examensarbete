from tkinter import *

HEIGHT = 724
WIDTH = 1920



class my_button(Button):

    color = 'white'
    ip = ""

    def print_(self):
        print(self.ip)    

userinfo = {
    'name' : 'Jonathan',
    'address' : '13.37'
}
log = [['jonathan', 'login', '27/4-2020'], ['jonathan', 'rdp', '30/4-2020']]

hosts = ['192.168.0.104', '192.168.0.114', '192.168.0.113']

def connect(btn):
    print(btn['text'])


def loginfo(log):
    h = 0.1
    for r in log:
        l = Label(root, bg = 'blue', text = r[1] + ' : ' + r[2])
        l.place(relx=0.1, rely = h, relheight=0.1, relwidth=0.3)
        h = h + 0.1

def create_hosts_new(hosts):
    ypos = 0.1
    for h in hosts:
        btn = Button(root, text=h, font=40)
        btn["command"] = lambda btn=btn: connect(btn)
        btn.place(relx=0.6, rely = ypos, relheight=0.1, relwidth=0.3)
      
        ypos = ypos + 0.1

def create_hosts():
    
    button1 = Button(root, text="192.168.0.114", font=40, command=lambda: connect(button1['text']))
    button1.place(relx=0.6, rely = 0.1, relheight=0.1, relwidth=0.3)

    button2 = Button(root, text="192.168.0.104", font=40, command=lambda: connect(button2['text']))
    button2.place(relx=0.6, rely = 0.2,relheight=0.1, relwidth=0.3)

    button3 = Button(root, text="192.168.0.100", font=40, command=lambda: connect(button3['text']))
    button3.place(relx=0.6, rely = 0.3,relheight=0.1, relwidth=0.3)

    button4 = Button(root, text="Dummy host", font=40, command=lambda: connect(button4['text']))
    button4.place(relx=0.6, rely = 0.4,relheight=0.1, relwidth=0.3)

    button5 = Button(root, text="Dummy host", font=40, command=lambda: connect(button5['text']))
    button5.place(relx=0.6, rely = 0.5,relheight=0.1, relwidth=0.3)
    
    button6 = Button(root, text="Dummy host", font=40, command=lambda: connect(button6['text']))
    button6.place(relx=0.6, rely = 0.6,relheight=0.1, relwidth=0.3)

    button7 = Button(root, text="Dummy host", font=40, command=lambda: connect(button7['text']))
    button7.place(relx=0.6, rely = 0.7,relheight=0.1, relwidth=0.3)


def draw_graphics_pic(log, host, background_image):

    canvas = Canvas(root, height=HEIGHT, width=WIDTH)
    canvas.pack()

    background_label = Label(root, image=background_image)
    background_label.place(relwidth=1, relheight=1)


    create_hosts_new(host)
    loginfo(log)

    #userinfo = Label(root, bg='green', text=userinfo.get('name') + ' : ' + userinfo.get('address'))
    #userinfo.place(relx = 0.2, rely= 0, relwidth=0.6, relheight = 0.1)




# Graphics

if __name__ == "__main__":
    root = Tk()
    background_image = PhotoImage(file='Syntronictest.png')
    draw_graphics_pic(log, hosts, background_image)
    root.mainloop()

