# symP

It is an alternative for Listary in Linux.

## TO-LIST
1. more flexible vim-mode shortcuts

## Usage

### Shortcuts
* <kbd>ALT+a</kbd>: Pull down(up) the window
* <kbd>TAB</kbd>: Shift between Command Textbox and the Listbox
* <kbd>RETURN</kbd>: Run the selected item

#### Command Textbox
* <kbd>CTRL+a</kbd>: Move to the head of line
* <kbd>CTRL+e</kbd>: Move to the end of line
* <kbd>CTRL+A</kbd>: Select all

#### Listbox
* <kbd>j</kbd>: Down
* <kbd>k</kbd>: Up
* <kbd>d</kbd>: Pagedown
* <kbd>u</kbd>: Pageup
* <kbd>H</kbd>: Goto the first item on display
* <kbd>L</kbd>: Goto the last item on display
* <kbd>ESCAPE</kbd>: Focus the Command Textbox

### Command Type

SymP includes several types of commands as follow.
* **User program**
* **User files**
* **User websites**
* **Files and directories**
* **Files modified recently**
* **Calculator**
    Exmaple: `1+sin(pi/6)`, `sum(range(101))`

### Configure
The main default configure file is `~/.symp_config`. All configure files use the JSON format.

**autoupdateprograms** = False

 Whether update the `userprogramsdata` if run a new program

**userfilepath** = os.getenv('HOME')+"/.symp_userfile"

 The path stores the userfile

**defaulteditor** = "gvim"

 The default editor

**program2file** = {'.jpg':"eog '%s'",
                '.pdf':"evince '%s'",
                '.png':"eog '%s'",
                '.tex':"gvim %s",
                '.mp4':"smplayer %s"
                }

The programs used to open the corresponding formats of files

**searchengine** = {"name":"GOOGLE", "url": "http://www.google.com/search?hl=&q=%s&btnG=Google+Search&inurl=https"}

 The search engine

**browser** = "firefox '%s'"

 The command of browser used to open an URL

**searchroot** = os.path.expanduser("~/")

 The path used to search files and directoies

**prettypath** = 0

 prettypath controls names of folders displayed in the listbox.
 If prettypath == 0, show the original name
 If not, when the length of the folder name is morethan prettypath,
 replace characters beyond the first prettypath with '\*'
 For example, if prettypath == 3, then the `/usr/local/texlive/2015/release-texlive.txt` is shown as `/usr/loc*/tex*/2015/release-texlive.txt` .
