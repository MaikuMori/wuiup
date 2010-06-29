"""Custom updater for Auctioneer preview versions (http://auctioneeraddon.com/dl/#preview) """
import re, urllib2

from updaters import Updater
from helper_functions import *

__author__ = "Miks Kalnins"
__copyright__ = "Copyright 2009, Miks Kalnins"
__license__ = "New BSD License"
__version__ = "0.3"
__maintainer__ = "Miks Kalnins"
__email__ = "mikskalnins@maikumori.com"
__status__ = "Production"

class AuctioneerUpdater(Updater):
	
    def update(self,cv):
        self.current_version = cv
        if self._canUpdate():
            if self.logging:
                self.logging.info(self.current_version and "Updating: AuctioneerSuite Beta" or "Installing: AuctioneerSuite Beta")
            self._dl_del_unzip(self.file)
            return self.last_version
        return False
	
    def _canUpdate(self):
        #http://mirror.auctioneeraddon.com/dl/Packages5	 2/AuctioneerSuite-5.1.4006.zip
        #http://auctioneeraddon.com/dl/?dl=Packages52/AuctioneerSuite-5.1.4006.zip
        #<a href="?dl=Packages52/AuctioneerSuite-5.1.4006.zip">
        source = urllib2.urlopen('http://auctioneeraddon.com/dl/index.php')
        myregex = re.compile('id="preview".+?dl=(.+?/AuctioneerSuite-(.+?).zip)"', re.DOTALL)
        m = myregex.search(source.read())
        if m:
            #http://mirror.auctioneeraddon.com/dl/
            self.file = 'http://mirror.auctioneeraddon.com/dl/' + m.group(1)
            self.last_version = m.group(2)
            if self.last_version != self.current_version:
                return True
            else:
                return False
        else:
            if self.logging:
                self.logging.error("Regex didn't match, probably http://mirror.auctioneeraddon.com/dl/ has been changed.")
            return False