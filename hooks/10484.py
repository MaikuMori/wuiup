"""Post update hook for cargoShip"""
import os

from hooks import AddonHookAbstract

__author__ = "Miks Kalnins"
__copyright__ = "Copyright 2009, Miks Kalnins"
__license__ = "New BSD License"
__version__ = "1.1"
__maintainer__ = "Miks Kalnins"
__email__ = "mikskalnins@maikumori.com"
__status__ = "Production"

class AddonHook(AddonHookAbstract):
    def afterUpdateHook(self):
        #I'm using a custom layout somewhere else, so I don't need this one.
        #I know I could just copy the lib to my addon folder, but I actually can't =(.
        #This is probably useless hook for anyone else but me.
        replaces = {"layout.lua" : ""}
        file_location = os.path.join(self.wowdir,'cargoShip/cargoShip.toc')
        return self._replace_text(file_location,replaces)