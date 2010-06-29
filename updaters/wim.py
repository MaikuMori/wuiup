"""Custom updater for WIM (winaddon.com) """
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

class WimUpdater(Updater):

	def update(self,cv):
		self.current_version = cv
		if self._canUpdate():
			if self.logging:
				self.logging.info(self.current_version and "Updating: WIM" or "Installing: WIM")
			self._dl_del_unzip(self.file)
			return self.last_version
		return False

	def _canUpdate(self):
		source = urllib2.urlopen('http://www.wimaddon.com/DownloadWIM.html')
		m = re.search(r'href="(downloads/WIM-(.+?).zip)"', source.read())
		if m:
			self.file = 'http://www.wimaddon.com/' + m.group(1)
			self.last_version = m.group(2)
			if self.last_version != self.current_version:
				return True
			else:
				return False
		else:
			if self.logging:
				self.logging.error("Regex didn't match, probably wimaddon.com has been changed.")
			return False