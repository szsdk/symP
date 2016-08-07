#!/usr/bin/python3

from tkinter import *
from tkinter import ttk
from functools import partial
import itemsgenerate
import config
import logging
import subprocess
import shutil

FORMAT = '%(levelname)s: %(message)s'
logging.basicConfig(format=config.FORMAT,level=logging.DEBUG,
        datefmt=config.DATAFORMAT)

userprograms = itemsgenerate.UserPrograms()
userfiles= itemsgenerate.UserFiles()
recentlyfiles = itemsgenerate.RecentlyFiles()
userwebsites = itemsgenerate.UserWebsites()
filesdirectories = itemsgenerate.FilesDirectories()

def refresh_listbox(*args):
    cmd = command.get()
    lstdatas = set([])
    lstdatas |= userprograms(cmd, limit=0.49)
    #if cmd and ((not lstdatas) or (lstdatas and max([i.rating for i in lstdatas])<9)):
        #p = subprocess.Popen("type %s" % cmd, shell=True, stdout=subprocess.PIPE,
                #stderr=subprocess.STDOUT).stdout.readline().decode("utf-8")
        #if p[-1-len(cmd):-1]==cmd:
    if cmd and shutil.which(cmd):
        tryrun = itemsgenerate.Program(cmd, "Run: %s" % cmd)
        tryrun.info = 'new program'
        tryrun.rating = 1
        lstdatas.add(tryrun)

    lstdatas |= userfiles(cmd, limit=0.49)
    lstdatas |= recentlyfiles(cmd, limit=0.49)
    lstdatas |= userwebsites(cmd, limit=0.49)
    if cmd:
        lstdatas |= filesdirectories(cmd, limit=0.49)

    try:
        lstdatas.add(itemsgenerate.Calculator(cmd))
    except:
        pass
                
    llstdatas = list(lstdatas)
    llstdatas.sort(key=lambda x: x.rating, reverse=True)
    listbox.set_data(llstdatas)
    lenlbox = len(llstdatas)
    for i in range(len(listbox.data)):
        listbox.itemconfig(i,itemsgenerate.color_theme_bg(type(llstdatas[i]), i/lenlbox))

def complete_command(_):
    cmd = listbox.data[listbox.get(ACTIVE)]
    command.set(cmd.show_command())

def run(_):
    cmd = listbox.data[listbox.get(ACTIVE)]
    logging.info('run %s', cmd)

    if type(cmd)==itemsgenerate.Calculator:
        command.set(cmd.show_command())
        return

    root.withdraw()
    if type(cmd)==itemsgenerate.Program and cmd.info=="new program":
        logging.debug("try to add new program %s", cmd)
        cmd.show_string = cmd.command
        cmd.info = ''
        userprograms.append(cmd)
    cmd()
    command.set('')
    #cmds.refresh_originaldata_file()

class MyListBox(Listbox):
    def set_data(self, data):
        self.data=dict([(str(i), i) for i in data])
        self.delete(0,END)
        for i in data:
            self.insert(END, i)

    def goto_index(self, pos):
        self.selection_clear(ACTIVE)
        self.selection_set(pos)
        self.activate(pos)
        self.see(pos)

from Xlib.display import Display
from Xlib import X

import threading
import _thread

fun_key = {'ctrl':4,
           'shift':1,
           'alt': 8,
           'win':64}
def check_hotkey(ctl, key, aEvent):
    #logging.debug("check_hotkey ctl:%s key:% aEvent:%s", ctl, key, aEvent)
    try:
        if ctl:
            if aEvent.state != sum(map(lambda x: fun_key[x], ctl)):
                return False
        if key != aEvent.detail:
            return False
        return True
    except:
        return False

#def handle_event(aEvent):
    #keycode = aEvent.detail
    #print(keycode)
    #if aEvent.type == X.KeyPress:
        #if (aEvent.detail == 38)&(aEvent.state == 8):
            #print('---')
            #root.deiconify()

class KeyBind(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.signal = True
        self.windows_state = True

    def callback(self):
        self.root.quit()

    def run(self):
        disp = Display()
        self.root = disp.screen().root

        # we tell the X server we want to catch keyPress event
        self.root.change_attributes(event_mask = X.KeyPressMask)

        #for keycode in [38]:
            #self.root.grab_key(keycode, X.AnyModifier, 1,X.GrabModeAsync, X.GrabModeAsync)
        self.root.grab_key(38, X.Mod1Mask, 1,X.GrabModeAsync, X.GrabModeAsync)

        # Alt+a
        while self.signal:
            event = self.root.display.next_event()
            if (event.type == X.KeyPress) and check_hotkey(['alt'], 38, event):
                if root.winfo_viewable():
                    root.withdraw()
                    recentlyfiles.refresh_items()
                else:
                    refresh_listbox()
                    entry.focus_set()
                    command.set('')
                    root.deiconify()

                self.windows_state = not self.windows_state


default_width = 600
default_height = 400

root=Tk()
root.title('Nothing')
#======= Center the Window ========
# Apparently a common hack to get the window size. Temporarily hide the
# window to avoid update_idletasks() drawing the window in the wrong
# position.
root.withdraw()
root.update_idletasks()  # Update "requested size" from geometry manager

root.geometry("%dx%d" % (default_width,default_height))
x = (root.winfo_screenwidth() - default_width) / 2
y = (root.winfo_screenheight() - default_height) / 2
root.geometry("+%d+%d" % (x, y))

command=StringVar()
command.trace("w", refresh_listbox)

entry=Entry(root, font='Sans 16', textvariable=command,width=root.winfo_reqwidth())
listbox=MyListBox(root, font='Sans 14', width=root.winfo_reqwidth(), height=root.winfo_reqheight())
#listbox=MyListBox(root, font='Sans 14', width=root.winfo_reqwidth())

entry.bind('<Return>', run)
#entry.bind('<KeyRelease>', refresh_listbox)
entry.pack()
#entry.bind('<Tab>', lambda _: listbox.focus_set())
entry.focus_set()

logging.debug('start')

#cmds= itemsgenerate.CommandData()
#listbox.set_data(cmds.commanddata)
#listbox.bind('<Return>', partial(print_keyboard, widget=listbox))
#listbox.bind('<Return>', print_hello)
listbox.bind('j', lambda _: listbox.event_generate('<Down>'))
listbox.bind('k', lambda _: listbox.event_generate('<Up>'))
listbox.bind('d', lambda _: listbox.event_generate('<Next>'))
listbox.bind('u', lambda _: listbox.event_generate('<Prior>'))
listbox.bind('H', lambda _: listbox.goto_index(0))
listbox.bind('L', lambda _: listbox.goto_index('end'))
listbox.bind('<Tab>', complete_command)
listbox.bind('<Escape>', lambda _: entry.focus_set())
listbox.bind('<Return>', run)
listbox.pack()

def on_closing():
    kb.signal = False
    root.destroy()

root.deiconify()
#from system_hotkey import SystemHotkey
#hk = SystemHotkeys()
#hk.register(('control', 'shift', 'h'), callback=root.deiconify)
kb=KeyBind()
kb.start()
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
