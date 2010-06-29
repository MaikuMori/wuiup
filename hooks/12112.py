"""Post update hook for oUF Freeb"""
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
        #                    what                      with
        replaces = {'local castBars = true' : 'local castBars = false',
                    'local height, width = 27, 270' : 'local height, width = 20, 140',
                    'player:SetPoint("CENTER", UIParent, -325, -175)' : 'player:SetPoint("CENTER", UIParent, -230, -200)',
                    'target:SetPoint("CENTER", UIParent, 325, -175)' : 'target:SetPoint("CENTER", UIParent, 230, -200)',
                    'tot:SetPoint("CENTER", UIParent, 0, -175)' : 'tot:SetPoint("BOTTOM", UIParent, 0, 50)'}
        file_location = os.path.join(self.wowdir,'oUF_Freeb/oUF_Freeb.lua')
        return self._replace_text(file_location,replaces)