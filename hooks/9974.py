"""Post update hook for oUF Caellian"""
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
        replaces = {"targetY = -158" : "targetY = -40",
            "playerY = -158" : "playerY = -40",
            "partyY = -15" : "partyY = -60",
            "noPlayerAuras = false" : "noPlayerAuras = true",
            "raidY = -15" : "raidY = -60"}
        file_location = os.path.join(self.wowdir,'oUF_Caellian/oUF_cConfig.lua')
        return self._replace_text(file_location,replaces)