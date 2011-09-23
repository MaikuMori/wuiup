"""Prototype for Custom Updaters"""
import os, sys, re, urllib2, zipfile
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
	
class CurseAddon(object):
    """Mixin for addons hosted on wowace.com curseforge.com
      
    Overwrite addon_id with addon name as it appears in the wowace.com url.
    For example for http://www.wowace.com/addons/recount/files/, the correct
    sting is 'recount'.
    """
    addon_id = False
    addon_type = False
    addon_name = False
    
    url = {
        "WOWACE" : {
            "base"      : "http://www.wowace.com",
            "static"    : "http://www.wowace.com",
            "file_list" : "http://www.wowace.com/addons/%s/files/"
        },
        "CURSEFORGE" : {
            "base"      : "http://wow.curseforge.com",
            "static"    : "http://www.curseforge.com",
            "file_list" : "http://wow.curseforge.com/addons/%s/files/"
        }
    }
    
    def update(self,cv):
        if not self.addon_id:
            print "CurseAddon: specify addon_id (it's the id from wowace url)"
            return False
        if not self.addon_type in ["WOWACE", "CURSEFORGE"]:
            print "CurseAddon: specify addon_type (WOWACE OF CURSEFORGE)"
            return False
        if not self.addon_name:
            print "CurseAddon: specify addon_name"
            return False
            
        self.current_version = cv
        if self._canUpdate():
            if self.logging:
                self.logging.info(self.current_version and 
                    'Updating: %s from version %s to %s' % (self.addon_name,
                                                            self.current_version,
                                                            self.last_version) or
                    'Installing: %s' % self.addon_name)
            self._dl_del_unzip(self.file)
            return self.last_version
        return False
        
    def _canUpdate(self):
        addon_list_page = urllib2.urlopen(self.url[self.addon_type]["file_list"] % self.addon_id)
        #<a href="/addons/recount/files/1478-v4-2-0e-release/">v4.2.0e release</a>
        m = re.search(r'href="(/addons/' + self.addon_id + '/files/([a-zA-Z0-9-]+?)/)">(.+?)<', addon_list_page.read())
        if m:
            self.last_version = m.group(3)
            if self.last_version != self.current_version:
                download_page = urllib2.urlopen(self.url[self.addon_type]["base"] + m.group(1))
                #<a href="http://static.wowace.com/content/files/529/668/Recount-v4.2.0e_release.zip">
                #<a href="http://www.curseforge.com/media/files/527/306/TradeSkillMaster-v0.2.4Beta.zip">
                #<a href="http://www.curseforge.com/media/files/530/116/TradeSkillMaster_Crafting-r438.zip">
                m = re.search(r'href="(' + self.url[self.addon_type]["static"] + '/media/files/(.+?).zip)"', download_page.read())
                if m:
                    self.file = m.group(1)
                    return True
                else:
                    if self.logging:
                        self.logging.error("CurseAddon: Regex didn't match, probably download page has been changed. (%s)", self.addon_name)
                    return False
            else:
                return False
        else:
            if self.logging:
                self.logging.error("CurseAddon: Regex didn't match, probably file list page has been changed. (%s)", self.addon_name)
            return False
	
		
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