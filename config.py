import json
import logging
import os

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
DATAFORMAT = '%H:%M:%S'
logging.basicConfig(format=FORMAT,level=logging.DEBUG, datefmt=DATAFORMAT)

with open(os.path.expanduser('~/.symp_config'), 'r') as configfile:
    config = json.load(configfile)

autoupdateprograms = False
# Whether update the `userprogramsdata` if run a new program
userfilepath = os.getenv('HOME')+"/.symp_userfile"
# The path stores the userfile
defaulteditor = "gvim"
# The default editor
program2file = {'.jpg':"eog '%s'",
                '.pdf':"evince '%s'",
                '.png':"eog '%s'",
                '.tex':"gvim %s",
                '.mp4':"smplayer %s"
                }
# The programs used to open the corresponding formats of files
searchengine = {"name":"GOOGLE", "url": "http://www.google.com/search?hl=&q=%s&btnG=Google+Search&inurl=https"}
# The search engine
browser = "firefox '%s'"
# The command of browser used to open an URL
searchroot = os.path.expanduser("~/")
# The path used to search files and directoies
prettypath = 0
# prettypath controls names of folders displayed in the listbox.
# If prettypath == 0, show the original name
# If not, when the length of the folder name is morethan prettypath,
# replace characters beyond the first prettypath with '*'
# For example, if prettypath == 3, then the
# /usr/local/texlive/2015/release-texlive.txt is shown as
# /usr/loc*/tex*/2015/release-texlive.txt.

for var, val in config.items():
    if var in locals():
        locals()[var] = val
    else:
        logging.error("There is no varible '%s' can be defined. IGNORE IT!", var)

with open(os.path.expanduser(userfilepath), 'r') as userfilefile:
    userfile = json.load(userfilefile)

userprogramsdata = []
userfilesdata = []
userwebsitesdata = []
for var, val in userfile.items():
    if var in locals():
        locals()[var] = val
    else:
        logging.error("There is no varible '%s' can be defined. IGNORE IT!", var)

def save_userfile():
    with open(os.path.expanduser(userfilepath), 'w') as userfilefile:
        json.dump({'userprogramsdata':userprogramsdata,
            'userfilesdata':userfilesdata, 'userwebsitesdata':userwebsitesdata},
            userfilefile, indent=2)
