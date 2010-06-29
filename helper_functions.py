import os, sys, cPickle, urllib2
from xml.dom import minidom

def _rmgeneric(path, __func__):
    try:
        __func__(path)
    except OSError, (errno, strerror):
        print "Error removing %(path)s, %(error)s " % {'path' : path, 'error': strerror }

def wuiup_removedir(path):
    if not os.path.isdir(path):
        return
    for x in os.listdir(path):
        fullpath=os.path.join(path, x)
        if os.path.isfile(fullpath):
            _rmgeneric(fullpath, os.remove)
        elif os.path.isdir(fullpath):
            wuiup_removedir(fullpath)
    _rmgeneric(path, os.rmdir)

def wuiup_unzip(mZip, path):
    for f in mZip.namelist():
        if not f.endswith('/'):
            root, name = os.path.split(f)
            directory = os.path.normpath(os.path.join(path, root))
            if not os.path.isdir(directory):
                os.makedirs(directory)

            dest = os.path.join(directory, name)

            nf = file(dest, 'wb')
            nf.write(mZip.read(f))
            nf.close()

def validate_user(user): #To be moved to helper functions
    url = "http://www.wowinterface.com/patcher/favs//%s.xml" % user
    dom = minidom.parse(urllib2.urlopen(url))
    if dom.getElementsByTagName('error'):
        if int(dom.getElementsByTagName('id')[0].firstChild.nodeValue) == 103:
            return False
        else:
            print 'Please give this info to the addon author: <%d> - %s' % (int(dom.getElementsByTagName('id')[0].firstChild.nodeValue),
                str(dom.getElementsByTagName('message')[0].firstChild.nodeValue))
            return False
    else:
        return True

def get_config(): #To be moved to helper functions
    if os.path.exists(os.path.join('./', 'wuiup_config.pkl')):
        try:
            pickled_data = open(os.path.join('./', 'wuiup_config.pkl'), 'rb')
            config = cPickle.load(pickled_data)
            pickled_data.close()
            return config
        except EOFError:
            return False
    else:
		return False