"""Prototype for Adddon Hooks"""
import os

__author__ = "Miks Kalnins"
__copyright__ = "Copyright 2009, Miks Kalnins"
__license__ = "New BSD License"
__version__ = "0.3a"
__maintainer__ = "Miks Kalnins"
__email__ = "mikskalnins@maikumori.com"
__status__ = "Production"

class AddonHookAbstract(object):

    def __init__(self, id, wowdir):
        """Initalizes addon hook.
            
        id: Wow Interface addon id.
            
        wow_dir: Wow interface directory.
        """
        self.uid = id
        self.wowdir = wowdir

    def beforeUpdateHook(self):
        """Method which will be execured before addon has been updated.

        Overwrite it in your hook if you to hook to before update "event".
        """
        return True

    def afterUpdateHook(self):
        """Method which will be execured after addon has been updated.

        Overwrite it in your hook if you to hook to after update "event".
        """
        return True

    def _replace_text(self, file_location, replaces):
        """Replaces text inside a lua file.

        file_location: Lua file location.

        replaces: List of text to replace using format {"Text to find" :
        "Text which will replace found text", "aaa" : "xxx", ...}.
        """
        output = []
        if os.path.isfile(file_location):
            with open(file_location,"rb") as f:
                for line in f:
                    for k,v in replaces.iteritems():
                        line = line.replace(k,v)
                    output.append(line)
            with open(file_location,"wb") as f:
                f.writelines(output)
            return True
        else:
            return False