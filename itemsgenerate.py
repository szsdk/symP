import os.path
import subprocess
import threading
import logging
import pickle
import json
import config

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT,level=logging.DEBUG)


class Program(object):
    def __init__(self, show_string, command=''):
        self.show_string=show_string
        if command:
            self.command=command
        else:
            self.command=show_string
        self.rating = 1
        self.info = ""

    def __str__(self):
        return self.show_string

    def __call__(self):
        subprocess.Popen(self.command, shell=True)

    def rate(self, cmd):
        if not cmd:
            self.rating = 1
        else:
            self.rating = string_match(cmd, self.show_string)
        return self.rating

    def to_json(self):
        return ["Program",[self.command]]

def choose_program(file_name):
    ext = os.path.splitext(os.path.basename(file_name))[1]
    if ext in config.program2file:
        return config.program2file[ext]
    #return 'gvim %s'

class File(object):
    def __init__(self, file_name, command=None, show_string=None, match_string=None):
        if not os.path.isfile(file_name):
            raise FileNotFoundError('%s does not exist' % file_name)
        self.file_name=file_name
        if show_string:
            self.show_string = show_string
        else:
            self.show_string = file_name

        if match_string:
            self.show_string = match_string
        else:
            self.match_string = self.show_string

        userpath = os.path.expanduser('~')
        if self.show_string[:len(userpath)] == userpath:
            self.show_string = '~'+self.show_string[len(userpath):]

        if command:
            self.command=command
        else:
            self.command=choose_program(file_name)

        self.rating = 1

    def __str__(self):
        if config.prettypath:
            path, filename = os.path.split(self.show_string)
            folders = path.split('/')
            newfn = '/' if [0]=='/' else ''
            for folder in folders:
                if folder:
                    if len(folder) <= config.prettypath+1:
                        newfn += folder + '/'
                    else:
                        newfn += folder[0:config.prettypath]+'*/'
            return newfn + filename
        else:
            return self.show_string

    def __call__(self):
        if self.command:
            subprocess.Popen(self.command % self.file_name, shell=True)
        else:
            fn = os.path.basename(self.file_name)
            logging.warning("There is no default program to open %s", fn)
            logging.info("Open %s with default editor %s", fn, config.default_editor)
            subprocess.Popen("%s %s" % (config.default_editor, self.file_name), shell=True)
    #def to_json(self):
        #if self.show_string = self.file_name:
            #return '["File",["%s", "%s"]]' % (self.file_name, self.command)
        #else:
            #return '["File",["%s", "%s"]]' % (self.file_name, self.command)

    def rate(self, cmd):
        if not cmd:
            self.rating = 1
        else:
            self.rating = string_match(cmd, self.match_string)
        return self.rating

class Website(object):
    def __init__(self, url):
        self.url = url

    def __str__(self):
        return self.url

    def __call__(self):
        subprocess.Popen(config.browser % self.url, shell=True)

    def rate(self, cmd):
        if not cmd:
            self.rating = 1
        else:
            self.rating = string_match(cmd, self.url)
        return self.rating

import math
class Calculator(object):
    _ns = vars(math).copy()
    _ns.update(vars())
    #_ns['__builtins__'] = None
    def __init__(self, cmd):
        self.match_string = str(eval(cmd, Calculator._ns))
        self.show_string = "Calculator: %s" % self.match_string
        self.rating = 1
    def __str__(self):
        return self.show_string

    def __call__(self):
        return self.match_string

    def rate(self, _):
        return self()

def string_match(cmd, s):
    a = cmd.lower()
    b = list(s.lower())
    ans = 0
    checkdouble = True
    for i in a:
        while len(b)>0:
            if i == b.pop(0): break
            checkdouble = False
        else:
            break
        ans += 1
        if checkdouble:
            ans += 1
        else:
            checkdouble = True
    if ans == len(a)*2:
        return 100
    else:
        return ans/len(a)/2

class ListGroups(object):
    def __init__(self):
        self.items = []
    def __call__(self, cmd, limit = 0):
        return [i for i in self.items if i.rate(cmd)>limit]

class RecentlyFiles(ListGroups):
    def __init__(self):
        super().__init__()
        self._originaldatathread = threading.Thread(target = self._get_recently_files)
        self.refresh_items()

    def _get_recently_files(self):
        def file_name_filter(fn):
            if fn[:6] == 'find: ': return False
            if fn[-1] == '~': return False
            return True

        logging.info("Start to get files modified recently")
        p = subprocess.Popen("find ~ -not -path '*/\.*' -type f -mtime -1", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        tmpa = []
        for i in p.stdout.readlines():
            fn = i.decode("utf-8")[:-1]
            if file_name_filter(fn):
                tmpa.append(File(fn, None))

        self.items = tmpa
        logging.info("Finish to get files modified recently")

    def refresh_items(self, force = False):
        logging.info('start to refresh the original data file')
        if not self._originaldatathread.isAlive():
            self._originaldatathread = threading.Thread(target = self._get_recently_files)
            self._originaldatathread.start()
        else:
            logging.info('the thread of refreshing the original data file is alive')

        if force:
            self._originaldatathread.join()
            self._originaldatathread = threading.Thread(target = self._get_recently_files)
            self._originaldatathread.start()
            self._originaldatathread.join()

# this is the llcs algorithm but too slow
#table = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
#for i, ca in enumerate(a, 1):
    #for j, cb in enumerate(b, 1):
        #table[i][j] = (
            #table[i - 1][j - 1] + 1 if ca == cb else
            #max(table[i][j - 1], table[i - 1][j]))
#return table[-1][-1]

class UserPrograms(ListGroups):
    def __init__(self):
        logging.debug('init user programs')
        super().__init__()
        for args in config.userprogramsdata:
            self.items.append(Program(*args))
    def append(self, cmd):
        config.userprogramsdata.append(cmd.to_json()[1])
        self.items.append(cmd)
        config.save_userfile()

class UserFiles(ListGroups):
    def __init__(self):
        super().__init__()
        for args in config.userfilesdata:
            self.items.append(File(*args))

class UserWebsites(ListGroups):
    def __init__(self):
        super().__init__()
        for args in config.userwebsitesdata:
            self.items.append(Website(*args))
