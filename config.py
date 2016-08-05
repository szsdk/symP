import json
import logging

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT,level=logging.DEBUG)

with open('config', 'r') as configfile:
    config = json.load(configfile)

autoupdateprograms = False
userfilepath = "~"
default_editor = "vim"
program2file = {'.jpg':"eog '%s'",
                '.pdf':"evince '%s'",
                '.png':"eog '%s'",
                '.tex':"gvim %s"
                }

for var, val in config.items():
    if var in locals():
        locals()[var] = val
    else:
        logging.error("There is no varible '%s' can be defined. IGNORE IT!", var)

with open(userfilepath, 'r') as userfilefile:
    userfile = json.load(userfilefile)

userprogramsdata = []
userfilesdata = []
for var, val in userfile.items():
    if var in locals():
        locals()[var] = val
    else:
        logging.error("There is no varible '%s' can be defined. IGNORE IT!", var)

def save_userfile():
    with open(userfilepath, 'w') as userfilefile:
        json.dump({'userprogramsdata':userprogramsdata,
            'userfilesdata':userfilesdata}, userfilefile,
            indent=2)
