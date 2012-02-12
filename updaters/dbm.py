"""Custom updater for Deadly Boss Mods alpha versions."""
import re, urllib2
import httplib

from updaters import Updater
from helper_functions import *

__author__ = "Miks Kalnins"
__copyright__ = "Copyright 2009, Miks Kalnins"
__license__ = "New BSD License"
__version__ = "0.1"
__maintainer__ = "Miks Kalnins"
__email__ = "mikskalnins@maikumori.com"
__status__ = "Production"

class DeadlyBossModsUpdater(Updater):
	
    def update(self,cv):
        self.current_version = cv
        if self._canUpdate():
            if self.logging:
                self.logging.info(self.current_version and "Updating: Deadly Boss Mods Alpha" or "Installing: Deadly Boss Mods Alpha")
            self._dl_del_unzip(self.file)
            return self.last_version
        return False
	
    def _canUpdate(self):
        # source = urllib2.urlopen('http://www.ninjapull.de/index.php?option=com_content&view=article&id=100&Itemid=121&lang=en')
        # myregex = re.compile('>([0-9]+?\.[0-9]+?\.[0-9]+?-alpha)<')
        # m = myregex.search(source.read())
        # if m:
            # self.file = 'http://www.ninjapull.de/dbm/download.php?id=6'
            # self.last_version = m.group(1)
            # if self.last_version != self.current_version:
                # return True
            # else:
                # return False
        # else:
            # if self.logging:
                # self.logging.error("Regex didn't match, probably download URL has changed. (Deadly Boss Mods)")
            # return False
            
            
        conn = httplib.HTTPConnection("85.114.128.119")
        conn.request("HEAD", "/dbm/download.php?id=6")
        resp = conn.getresponse()
        #'attachment; filename="DBM-svn-4.10.0-r6576-alpha.zip"'
        #                       ^                        ^
        #                      22                       -5
        self.last_version = resp.getheader("content-disposition")[22:-5]
        if self.last_version != self.current_version:
            self.file = 'http://www.ninjapull.de/dbm/download.php?id=6'
            return True
        else:
            return False
