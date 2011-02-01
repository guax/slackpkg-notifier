#!/usr/bin/env python

""" slackpkg-notifier - update notification icon for slackware gnu/linux

This small and simple application aims to notificate the user when updates
happens on slackware's mirrors he's using with slackpkg.

"""

#   This code is strongly based upon wicd tray icon client so im keeping the
#   copyright notice and adding the note for my modifications.
#   I am not a python programmer. So don't blame me for my crap identation or
#   code here.
#
#   Huge cut in code and modifications by:
#   Copyright (C) 2009 - Henrique Grolli Bassotto
#
#   Original wicd tray source coded by:
#   Copyright (C) 2007 - 2008 Adam Blackburn
#   Copyright (C) 2007 - 2008 Dan O'Reilly
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License Version 2 as
#   published by the Free Software Foundation.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import gtk
import gobject
import getopt
import os
import time
from threading import Thread

# Internal specific imports
import wpath

ICON_AVAIL = True

gtk.gdk.threads_init()

if __name__ == '__main__':
    wpath.chdir(__file__)

'''
Function used to print text inside the thread. (this kludge fix a anoying bug
with locks in gobject, or something like that).
'''
def printInThread (texto):
    print texto

checker = None

'''
Class that triggers the periodic check for updates.
ps. I should use different files for different classes.
'''
class PeriodicChecker(Thread):
    def __init__(self,tray):
        Thread.__init__(self)
        self.tray = tray
    def run(self):
        self.tray.check()
        while 1:
            time.sleep(wpath.checker_time * 3600)
            gobject.idle_add(printInThread, "Starting scheduled checking.")
            self.tray.check()

'''
The big baby.
'''
class TrayIcon:
    """ Base Tray Icon class.
    
    Base Class for implementing a tray icon to display network status.
    
    """
    def __init__(self, use_tray):
        self.tr = self.StatusTrayIconGUI(use_tray)
        
    class TrayIconGUI:
        """ Base Tray Icon UI class.
        
        Implements methods and variables used by StatusIcon
        tray icons.

        """
        
        class Checker(Thread):
            def __init__(self,tray):
                Thread.__init__(self)
                self.tray = tray
                
            def run(self):
                # Lets determine the slackpkg results
                no_permission = "\nOnly root can install, upgrade, or remove packages.\nPlease log in as root or contact your system administrator.\n\n\n";
                no_answer = "\n";
                have_updates = "\nNews on ChangeLog.txt\n\n";
                no_updates = "\nNo news is good news\n\n";
                gobject.idle_add(printInThread, "Checking...")
                # You must have slackpkg 2.71 or above
                # Thanks PiterPunk to add the check function :*
                check_result = os.popen("/usr/sbin/slackpkg -checkgpg=off check-updates").read()
                if check_result == have_updates:
                    self.tray.need_update()
                    gobject.idle_add(printInThread, "Done. We got updates.")
                elif check_result == no_updates:
                    self.tray.no_update()
                    gobject.idle_add(printInThread, "Done. No updates.")
                elif check_result == no_permission:
                    self.tray.no_update()
                    gobject.idle_add(printInThread, "You don't have permission to run slackpkg =(")
                elif check_result == no_answer:
                    self.tray.no_update()
                    gobject.idle_add(printInThread, "Are we connected to internet?")
                else:
                    self.tray.no_update()
                    gobject.idle_add(printInThread, "Unexpected answer from slackpkg: " + check_result)
        
        def __init__(self, use_tray):
            menu = """
                    <ui>
                    <menubar name="Menubar">
                    <menu action="Menu">
                    <separator/>
                    <menuitem action="About"/>
                    <menuitem action="Quit"/>
                    </menu>
                    </menubar>
                    </ui>
            """
            actions = [
                    ('Menu',  None, 'Menu'),
                    ('About', gtk.STOCK_ABOUT, '_About...', None,
                     'About slackpkg-notifier', self.on_about),
                    ('Quit',gtk.STOCK_QUIT,'_Quit',None,'Quit slackpkg-notifier',
                     self.on_quit),
                    ]
            actg = gtk.ActionGroup('Actions')
            actg.add_actions(actions)
            self.manager = gtk.UIManager()
            self.manager.insert_action_group(actg, 0)
            self.manager.add_ui_from_string(menu)
            self.menu = (self.manager.get_widget('/Menubar/Menu/About').props.parent)
            self.gui_win = None
            self.current_icon_path = None
            self.use_tray = use_tray
        
        def need_update(self):
            self.current_icon_path = wpath.images
            gtk.StatusIcon.set_from_file(self, wpath.images + "icon.png")
            self.set_blinking(True)
            self.set_tooltip("You can update your system.")

        def no_update(self):
            self.current_icon_path = wpath.images
            gtk.StatusIcon.set_from_file(self, wpath.images + "icon.png")
            self.set_blinking(False)
            self.set_tooltip("No update.")

        def on_activate(self, data=None):
            self.check()
            
        def check(self):
            global checker
            self.set_blinking(False)
            self.current_icon_path = wpath.images
            gtk.StatusIcon.set_from_file(self, wpath.images + "checking.png")
            self.set_tooltip("Checking for updates.")
            checker = self.Checker(self)
            checker.start()

        def on_quit(self, widget=None):
            """ Closes the tray icon. """
            sys.exit(0)

        def on_about(self, data=None):
            """ Opens the About Dialog. """
            dialog = gtk.AboutDialog()
            dialog.set_name('Slackware Update Notifier')
            # VERSIONNUMBER
            dialog.set_version(wpath.version)
            dialog.set_comments('An icon that shows if you need to update. (slackpkg based)')
            dialog.set_website('http://www.guax.com.br/')
            dialog.run()
            dialog.destroy()

    if hasattr(gtk, "StatusIcon"):
        class StatusTrayIconGUI(gtk.StatusIcon, TrayIconGUI):
            """ Class for creating the wicd tray icon on gtk > 2.10.
            
            Uses gtk.StatusIcon to implement a tray icon.
            
            """
            def __init__(self, use_tray=True):
                TrayIcon.TrayIconGUI.__init__(self, use_tray)
                self.use_tray = use_tray
    
                gtk.StatusIcon.__init__(self)
    
                self.current_icon_path = ''
                self.set_visible(True)
                self.connect('activate', self.on_activate)
                self.connect('popup-menu', self.on_popup_menu)
                self.current_icon_path = wpath.images
                gtk.StatusIcon.set_from_file(self, wpath.images + "icon.png")
                self.set_tooltip("No updates")
    
            def on_popup_menu(self, status, button, timestamp):
                """ Opens the right click menu for the tray icon. """
                self.menu.popup(None, None, None, button, timestamp)

def usage():
    # VERSIONNUMBER
    """ Print usage information. """
    print """
slackpkg-notifier """ + wpath.version + """
An icon that shows if you need to update. (slackpkg based).

Arguments:
\t-h\t--help\t\tPrint this help information.
"""

def main(argv):
    """ The main frontend program.

    Keyword arguments:
    argv -- The arguments passed to the script.

    """
    use_tray = True
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['help'])
    except getopt.GetoptError:
        # Print help information and exit
        usage()
        sys.exit(2)

    for opt, a in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        else:
            usage()
            sys.exit(2)

    # Set up the tray icon GUI
    tray_icon = TrayIcon(use_tray)
    checker = PeriodicChecker(tray_icon.tr)
    checker.start()
    mainloop = gobject.MainLoop()
    mainloop.run()


if __name__ == '__main__':
    main(sys.argv)