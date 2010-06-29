"""Prototype for Custom Updaters"""
import os, sys, urllib2, zipfile
from StringIO import StringIO

from helper_functions import *

__author__ = "Miks Kalnins"
__copyright__ = "Copyright 2009, Miks Kalnins"
__license__ = "New BSD License"
__version__ = "0.3"
__maintainer__ = "Miks Kalnins"
__email__ = "mikskalnins@maikumori.com"
__status__ = "Production"

class Updater(object):
	
	def __init__(self, wowdir, logger = None):
		"""Initalizes custom updater.
		
		id: Unique id, same as updaters file name.
		wow_dir: Wow interface directory.
		storage: Addon storage
		"""
		self.id = self.__class__.__name__
		self.wow_dir = wowdir
		self.logging = logger
		
	def update(self, current_version):
		"""Main update function
		
		current_version: Current version number on HDD. None if no info.
		"""
		print "update: You are supposed to overwrite this method"
		return False
	
	def _dl_del_unzip(self, file_location):
		f = urllib2.urlopen(file_location)
		data = StringIO(f.read())
		f.close()
		data = zipfile.ZipFile(data)
		addon_dirs = []
		for f in data.namelist():
			dir = str(f.split('/',1)[0]) 
			if not (dir in addon_dirs):
				addon_dirs.append(dir)
				wuiup_removedir(os.path.join(self.wow_dir, dir))
		wuiup_unzip(data,self.wow_dir)
		data.close()
	def getFilename(self):
		"""Returns file name of updater, used as unique ID"""
		return
	

		
def import_updaters(dir):
	""" Imports custom updaters
	
	dir: Custom updater directory.""" 
	if os.path.isdir(dir):
		sys.path.append(dir)
	for f in os.listdir(os.path.abspath(dir)):
		module_name, ext = os.path.splitext(f)
		if ext == '.py' and (module_name != "__init__"):
			try:
				__import__(module_name, None, None, [''])
			except (Exception), error:
				print "Error while importing custom updater:", str(error)
			
def find_updaters():
	return Updater.__subclasses__()