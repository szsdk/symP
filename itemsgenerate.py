import os.path
import glob
import subprocess
import threading
import logging
import pickle
import json
import config

logging.basicConfig(format=config.FORMAT,level=logging.DEBUG,
        datefmt=config.DATAFORMAT)

class Program(object):
    def __init__(self, command, show_string=''):
        self.command = command
        if show_string:
            self.show_string = show_string
        else:
            self.show_string = command
        self.rating = 1
        self.info = ""

    def __str__(self):
        return self.show_string

    def __call__(self):
        subprocess.Popen(self.command, shell=True)

    def __eq__(self, other):
        if not isinstance(other, Program): return False
        return self.command == other.command

    def __hash__(self):
        return hash(self.command)

    def rate(self, cmd):
        if not cmd:
            self.rating = 1
        elif not '/' in cmd:
            self.rating = string_match(cmd, self.show_string)+0.1
        else:
            self.rating = string_match(cmd, self.show_string)
        return self.rating

    def show_command(self):
        return self.command

    def to_json(self):
        return ["Program",[self.command]]

def choose_program(file_name):
    if os.path.isdir(file_name):
        ext = "FOLDER"
    else:
        ext = os.path.splitext(os.path.basename(file_name))[1]
    if ext in config.program2file:
        return config.program2file[ext]
    #return 'gvim %s'

class File(object):
    def __init__(self, file_name, command=None, show_string=None, match_string=None):
        #if not os.path.isfile(file_name):
        if not glob.glob(file_name):
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

    def __eq__(self, other):
        if not isinstance(other, File): return False
        return (self.command == other.command) and (self.file_name == self.file_name)

    def __hash__(self):
        if self.command:
            return hash(self.command+self.file_name)
        return hash(self.file_name)
    #def to_json(self):
        #if self.show_string = self.file_name:
            #return '["File",["%s", "%s"]]' % (self.file_name, self.command)
        #else:
            #return '["File",["%s", "%s"]]' % (self.file_name, self.command)

    def show_command(self):
        return self.file_name

    def rate(self, cmd):
        if not cmd:
            self.rating = 1
        elif '/' in cmd:
            self.rating = string_match(cmd, self.match_string)+0.1
        else:
            self.rating = string_match(cmd, self.match_string)
        return self.rating

class Website(object):
    def __init__(self, url):
        self.url = url

    def __str__(self):
        if self.rating:
            return self.rating + self.url
        return self.url

    def __call__(self):
        subprocess.Popen(config.browser % self.url, shell=True)

    def __eq__(self, other):
        if not isinstance(other, Website): return False
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)

    def show_command(self):
        return str(self)

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
        self.answer = str(eval(cmd, Calculator._ns))
        self.show_string = "Calculator: %s" % self.answer
        self.rating = 1
    def __str__(self):
        return self.show_string

    def __call__(self):
        return self.answer

    def __eq__(self, other):
        return False

    def show_command(self):
        return self()

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
        self.items = set([])
    def __call__(self, cmd, limit = 0):
        return {i for i in self.items if i.rate(cmd)>limit}

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
        tmpa = set([])
        for i in p.stdout.readlines():
            fn = i.decode("utf-8")[:-1]
            if file_name_filter(fn):
                tmpa.add(File(fn, None))

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
            self.items.add(Program(*args))
    def append(self, cmd):
        config.userprogramsdata.append(cmd.to_json()[1])
        self.items.add(cmd)
        config.save_userfile()

class UserFiles(ListGroups):
    def __init__(self):
        super().__init__()
        for args in config.userfilesdata:
            self.items.add(File(*args))

class FilesDirectories(ListGroups):
    def match_filefolder(folder, ml):
        either =lambda c: '[%s%s]'%(c.lower(),c.upper()) if c.isalpha() else c
        searchitem = ml.pop(0)
        searchitem = ''.join(map(either,searchitem))
        if not searchitem:
            yield folder
            return
        if len(ml) == 0:
            for dotindex in range(len(searchitem)-1, -1, -1):
                if searchitem[dotindex] == '.': break
            if searchitem[dotindex] == '.':
                nam = searchitem[0:dotindex]
                ext = searchitem[dotindex:]
                for i in glob.glob("%s*%s*%s*" %(folder,nam,ext)):
                    yield i
            else:
                for i in glob.glob("%s*%s*" % (folder, searchitem)):
                    if not os.path.splitext(os.path.basename(i))[1]:
                        yield i
        else:
            li = glob.glob(folder + "/*" + searchitem + "*/")
            for i in li:
                yield from FilesDirectories.match_filefolder(i, ml.copy())

    def __init__(self):
        super().__init__()
        self.items = []

    def __call__(self, cmd, limit=0 ):
        self.items = set([])
        if cmd[0] == '/':
            searchresult = FilesDirectories.match_filefolder('/', cmd[1:].split('/'))
        else:
            logging.debug(cmd)
            searchresult = FilesDirectories.match_filefolder(
                    config.searchroot, cmd.split('/'))
        for filename in searchresult:
            self.items.add(File(filename))
        return {i for i in self.items if i.rate(cmd)>limit}

class UserWebsites(ListGroups):
    def __init__(self):
        super().__init__()
        for args in config.userwebsitesdata:
            self.items.add(Website(*args))
