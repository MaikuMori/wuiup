#!python
"""Updates WoW addons from http://www.wowinterface.com/ ."""
import os, cPickle, logging, zipfile, urllib2, sys, re, platform
from xml.dom import minidom
from StringIO import StringIO
from optparse import OptionParser

from updaters import import_updaters, find_updaters
from helper_functions import *

__author__ = "Miks Kalnins"
__copyright__ = "Copyright 2009, Miks Kalnins"
__license__ = "New BSD License"
__version__ = "0.3"
__maintainer__ = "Miks Kalnins"
__email__ = "mikskalnins@maikumori.com"
__status__ = "Production"

def main():
    """Execute main update code."""
    #Init logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S', filename='./wuiup.log', filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)
    #Get config and validate
    config = get_config()
    if config == False:
        configure()
        config = get_config()
    try:
        if ((not os.path.exists(config['wow_dir'])) or (not validate_user(config['wui_user']))):
            logging.error("ERROR: Configuration is not valid.")
            configure(True)
            config = get_config()
    except urllib2.URLError:
        logging.error("Couldn't connect to http://wowinterface.com, are you connected to the Internet?")
        exit()
    #Load old addon data
    if os.path.exists(os.path.join(config['wow_dir'], 'wuiup_data.pkl')):
        try:
            pickled_data = open(os.path.join(config['wow_dir'], 'wuiup_data.pkl'), 'rb')
            old_addons = cPickle.load(pickled_data)
            pickled_data.close()
        except EOFError:
            old_addons = {}
    else:
        logging.debug('First run, two data files will be created. To remove them run wuiup.py -r')
        old_addons =  {}
    logging.info('Checking for updates...')
    info = {"addons_installed" : 0, "addons_updated" : 0}
    try:
        #Get favorites
        #url = 'http://www.wowinterface.com/patcher/favs/%s/%s.xml' % (WUI_PASSWORD, WUI_USERNAME)
        url = 'http://www.wowinterface.com/patcher/favs/a/%s.xml' % config['wui_user'] #Passwordless way of doing it!
        dom = minidom.parse(urllib2.urlopen(url))
        favorited_addons = {}
        for node in dom.getElementsByTagName('Ui'):
            try:
                uid = int(node.getElementsByTagName('UID')[0].firstChild.nodeValue)
                version = str(node.getElementsByTagName('UIVersion')[0].firstChild.nodeValue)
                name = str(node.getElementsByTagName('UIName')[0].firstChild.nodeValue)
                if uid in old_addons:
                    failed = False
                    if version != old_addons[uid]:
                        logging.info('Updating: %s from version %s to %s' % (name,old_addons[uid],version))
                        has_hook = False
                        if os.path.isfile(''.join(['./hooks/',str(uid),'.py'])):
                            logging.info('Running hooks for %s' % name)
                            has_hook = True
                            try:
                                hook = __import__('hooks.'+str(uid), globals(), locals(), ['AddonHook'], -1)
                                hook = hook.AddonHook(uid,config['wow_dir'])
                            except Exception:
                                logging.warning('Failed to import hook.')
                            try:
                                hook.beforeUpdateHook()
                            except Exception:
                                logging.warning('Failed to run before update hook.')
                        if not update_addon(uid, config['wow_dir']):
                             failed = True
                        else:
                            info['addons_updated'] = info['addons_updated'] + 1
                        if has_hook:
                            try:
                                hook.afterUpdateHook()
                            except Exception:
                                logging.warning('Failed to run after update hook.')
                            finally:
                                del hook
                    if not failed:
                        favorited_addons[uid] = version
                    else:
                        favorited_addons[uid] = old_addons[uid]
                else:
                    logging.info('Installing new addon: %s' % name)
                    has_hook = False
                    if os.path.isfile(''.join(['./hooks/',str(uid),'.py'])):
                        logging.info('Running hooks for %s' % name)
                        has_hook = True
                        try:
                            hook = __import__('hooks.'+str(uid), globals(), locals(), ['AddonHook'], -1)
                            hook = hook.AddonHook(uid,config['wow_dir'])
                        except Exception:
                            logging.warning('Failed to import hook.')
                        try:
                            hook.beforeUpdateHook()
                        except Exception:
                            logging.warning('Failed to run before update hook.')
                    if update_addon(uid, config['wow_dir']):
                        favorited_addons[uid] = version
                        info['addons_installed'] = info['addons_installed'] + 1
                    if has_hook:
                        try:
                            hook.afterUpdateHook()
                        except Exception:
                            logging.warning('Failed to run after update hook.')
                        finally:
                            del hook
            except  (urllib2.URLError), error:
                logging.error('Failed to download addon info: %s' % error)
            except (TypeError), error:
                logging.error('Failed to update addon, could be corrupt XML: %s' % error)
            except zipfile.BadZipfile:
                logging.error('Zip file is corrupt.')
            except (Exception), error:
                logging.error('Uncaught exception: %s' % error)
        #Run custom updaters
        import_updaters('updaters/')
        custom_updaters = find_updaters()
        if len(custom_updaters) > 0:
            logging.info('Running custom updaters ...')
        for updater in custom_updaters:
            updater = updater(config['wow_dir'], logging)
            has_hook = False
            if os.path.isfile(''.join(['./hooks/',updater.id,'.py'])):
                logging.info('Running hooks for %s' % name)
                has_hook = True
                try:
                    hook = __import__('hooks.'+updater.id, globals(), locals(), ['AddonHook'], -1)
                    hook = hook.AddonHook(updater.id,config['wow_dir'])
                except Exception:
                    logging.warning('Failed to import hook.')
                try:
                    hook.beforeUpdateHook()
                except Exception:
                    logging.warning('Failed to run before update hook.')
            
            m = re.match(r'\<(.+?) ', str(updater)) #This should never fail, so no testing.
            updater_id = m.group(1)
            new_version = False            
            if old_addons.has_key(updater_id):
                try:
                    new_version = updater.update(old_addons[updater_id])
                except (Exception), error:
                    logging.error('Error while runing custom updaters update function: %s' % error)
                if new_version:
                    favorited_addons[updater_id] = new_version
                    if old_addons[updater_id] != new_version: info['addons_updated'] = info['addons_updated'] + 1
                else:
                    favorited_addons[updater_id] = old_addons[updater_id]
            else:
                try:
                    new_version = updater.update(None)
                except (Exception), error:
                    logging.error('Error while runing custom updaters update function: %s' % error)
                if new_version:
                    favorited_addons[updater_id] = new_version
                    info['addons_installed'] = info['addons_updated'] + 1
            if has_hook:
                try:
                    hook.afterUpdateHook()
                except Exception:
                    logging.warning('Failed to run after update hook.')
                finally:
                    del hook
        logging.info('Done, %s addons updated and %s new addons installed.' % (info['addons_updated'], info['addons_installed']))
    except (urllib2.URLError), error:
        logging.error('Failed to download favorites list: %s' %error)
    except KeyboardInterrupt:
        logging.info('Aborting..')
    except (Exception), error:
        logging.error('Uncaught fatal exception: %s' % error)
    finally:
        logging.getLogger('').removeHandler(console)
        #Save settings:
        pickled_data = open(os.path.join(config['wow_dir'], 'wuiup_data.pkl'), 'wb')
        cPickle.dump(favorited_addons, pickled_data)
        pickled_data.close()

def update_addon(uid,wow_dir):
    """Downloads latest version of addon and extract it into wow directory.
    
    uid: Wow interface addon addon id
    wow_dir: Wow addon directory"""
    url = 'http://www.wowinterface.com/patcher/info-%d.xml' % uid
    dom = minidom.parse(urllib2.urlopen(url))
    
    if dom.getElementsByTagName('error'):
        if int(dom.getElementsByTagName('id')[0].firstChild.nodeValue) == 403:
            print 'The file is still being checked by mods, update will be downloaded next time you run this script.' #This function shouldn't print.
            return False
        else:
            print 'Please give this info to the addon author: <%d> - %s' % (int(dom.getElementsByTagName('id')[0].firstChild.nodeValue),
             str(dom.getElementsByTagName('message')[0].firstChild.nodeValue))
            return False
    file_location = str(dom.getElementsByTagName('UIFileURL')[0].firstChild.nodeValue)
    size = int(dom.getElementsByTagName('UISize')[0].firstChild.nodeValue)
    if size > 1048576: #If size is lager then 1mb
        print 'Downloading big file, this may take more then few seconds' #This function shouldn't print. This is just a workaround. Again.
    f = urllib2.urlopen(file_location)
    data = StringIO(f.read())
    f.close()
    data = zipfile.ZipFile(data)
    addon_dirs = []
    for f in data.namelist():
        dir = str(f.split('/',1)[0])
        if not (dir in addon_dirs):
            addon_dirs.append(dir)
            wuiup_removedir(os.path.join(wow_dir, dir))
    wuiup_unzip(data,wow_dir)
    data.close()
    return True

def configure(reconfigure = False):
    """Creates and populates config file"""
    config = {}
    if reconfigure:
        print "*** Reconfiguring Wuiup ***"
    else:
        print "*** This is probably the first run. Wuiup needs you to enter some data ***"
    #Wow directory
    clientOS = platform.system()
    if clientOS == "Windows":
        winreg = __import__('_winreg')
        try:
            aKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Blizzard Entertainment\\World of Warcraft") 
            config['wow_dir'] = winreg.QueryValueEx(aKey, "InstallPath")[0] + "Interface\Addons"
        except (WindowsError),error:
            config['wow_dir'] = "not_found"
    elif clientOS == "Darwin":
        config['wow_dir'] = os.path.expanduser('~/Applications/World of Warcraft/Interface/Addons')
        if not os.path.exists(config['wow_dir']):
            config['wow_dir'] = '/Applications/World of Warcraft/Interface/Addons'
    else:
        #Trying to make a lucky guess to detect wow directory on linux 
        config['wow_dir'] = "/usr/local/games/World of Warcraft/Interface/Addons"
    first_time = True
    if os.path.exists(config['wow_dir']):
        print "Wuiup found World of Warcraft addon directory:"
        print "--> %s" % config['wow_dir']
    else:
        while ((not os.path.exists(config['wow_dir'])) and (config['wow_dir'] != "")):
            if first_time:
                print "World of Warcraft doesn't appear to be installed on this computer."
                print "You may still enter location of World of Warcraft addon directory manualy:"
                first_time = False
            else:
                print "Couln't find addon directory, you may try again or press enter to cancel:"
            config['wow_dir'] = raw_input("--> ")
            
    #Username
    print "Enter your Wow Interface (http://www.wowinterface.com) username:"
    config['wui_user'] = raw_input("--> ")
    try:
        while not validate_user(config['wui_user']) and config['wui_user'] !="":
            print "Username you entered isn't valid, try again or simply press enter to cancel:"
            config['wui_user'] = raw_input("--> ")
    except urllib2.URLError:
        logging.error("Couldn't connect to http://wowinterface.com, are you connected to the Internet?")
        exit()
    if config['wui_user'] == "":
        return False
    #Save config
    config['wow_dir'] = os.path.normpath(config['wow_dir'])
    pickled_data = open(os.path.join("./", 'wuiup_config.pkl'), 'wb')
    cPickle.dump(config, pickled_data)
    pickled_data.close()    
    
def remove():
    """Removes Wuiup configuration and data files"""
    config = get_config()
    if config:
        files = ["wuiup_config.pkl",
                 "wuiup.log",
                 config['wow_dir']+"\wuiup_data.pkl"]
        for file in files:
            os.remove(os.path.normpath(file))
        print "Wuiup configuration and data files has been removed"
    else:
        print "Abortig, theres no configuration file to start with."

def dispatch():
    """Handles comandline parameters and dispatches according commands"""
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage)
    parser.set_defaults(command="update")
    parser.add_option("-u", "--update", action="store_const", dest="command", const="update", 
                    help="updates all addons (default action)")
    parser.add_option("-c", "--configure", action="store_const", dest="command", const="configure", 
                    help="force reconfiguration")                
    parser.add_option("-r", "--remove", action="store_const", dest="command", const="remove", 
                    help="deletes all configuration files and logs")
    (options, args) = parser.parse_args()
    if options.command == "update":
        main()
    elif options.command == "configure":
        configure(True)
    elif options.command == "remove":
        remove()
    
if __name__ == "__main__":	   #in case I want to rewirte it using a class to store common tasks
    dispatch()
