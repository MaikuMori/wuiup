"""Builds a zip file for uploading to Wow Interface.
    Expects a version number"""

import sys, os, time, zipfile
from shutil import copytree, rmtree, ignore_patterns, copy
from re import search as re_search

def build(version):
    print "Building {0} ...".format(version)

    cur_dir = os.curdir + os.sep
    base_dir = cur_dir + "build"
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    build_dir = base_dir + os.sep + "wuiup-"+ version
    if os.path.exists(build_dir):
        loop = True
        while loop:
            a = raw_input("Build already exists. Rebuild? (y, n) [n]: ")
            if a == "" or a == "n":
                exit()
            elif a == "y":
               loop = False
               print "Rebuilding ..."
        rmtree(build_dir)
        #Windows thingy. The directory is still locked for small amount of
        #time if user has it open in explorer.
        time.sleep(0.1)

    #Copy everything need which doesn't require special care.
    copytree(os.curdir, build_dir,
            ignore=ignore_patterns(
                ".git", "build", "dist", "hooks", "updaters",
                ".ditz-config", ".gitignore", "build.py",
                "*.pyc", "*.log", "*.pkl"
            ))

    #Make hooks and updaters directories.
    build_hooks_dir = build_dir + os.sep + "hooks"
    os.mkdir(build_hooks_dir)
    build_updaters_dir = build_dir + os.sep + "updaters"
    os.mkdir(build_updaters_dir)

    #Copy __init__.py from hooks and updaters.
    copy(cur_dir + "hooks" + os.sep + "__init__.py", build_hooks_dir)
    copy(cur_dir + "updaters" + os.sep + "__init__.py", build_updaters_dir)

    #Copy custom updaters and hooks to disabled dir.
    build_hooks_disabled_dir = build_hooks_dir + os.sep + "disabled"
    copytree(os.curdir + os.sep + "hooks", build_hooks_disabled_dir,
            ignore=ignore_patterns("__init__.py","*.pyc"))
    build_updaters_disabled_dir = build_updaters_dir + os.sep + "disabled"
    copytree(os.curdir + os.sep + "updaters", build_updaters_disabled_dir,
            ignore=ignore_patterns("__init__.py","*.pyc"))

    #Add readme's to hooks and updaters directories.
    with open(build_hooks_dir + os.sep + "README.txt", 'w') as f:
        f.write("Move file from 'disabled' directory to this " +
                "directory (hooks) to enable hooks for that addon. \n\n" +
                "The first line in each file should describe wich " +
                "addon the hook is made for. Sorry for inconvenience.")
    with open(build_updaters_dir + os.sep + "README.txt", 'w') as f:
        f.write("Move file from 'disabled' directory to this "+
                "directory (updaters) to enable that custom updater.")

    #Make 'dist' folder if it doesn't exist.
    dist_dir = cur_dir + "dist"
    if not os.path.exists(dist_dir):
        os.mkdir(dist_dir)
    #Let's zip it up!
    print "Packaging..."
    zip = zip_it_up(build_dir,dist_dir, "wuiup")
    print "Done! Zip file for uploading can be located at: {0}".format(zip)

def zip_it_up(src_folder,dst_folder, base):

    def add_folder(zip_file, folder, base):
        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path):
                print "File added: {0}".format(full_path)
                arc_path = os.path.join(base, file)
                zip_file.write(full_path, arc_path)
            elif os.path.isdir(full_path):
                add_folder(zip_file, full_path, os.path.join(base, file))
                
    base_filename =  os.path.basename(src_folder)
    full_filename = dst_folder + os.sep + base_filename + ".zip"
    zip_file = zipfile.ZipFile(full_filename, 'w')
    add_folder(zip_file, src_folder, base)

    zip_file.close()
    
    return full_filename


def dispatch(argv):
    if len(argv) == 1:
        #And here comes the over-complicated test :D~~.
        if re_search("^\d+\.([1-9]|\d+[1-9])(.[1-9]|.\d+[1-9])?$", argv[0]):
            build(argv[0])
        else:
            #mayor_release.feature_release or
            #mayor_release.feature_release.bugfix_release
            print "The version number must be in format:"
            print "  (0-999+).(1-999+) or (0-999+).(1-999+).(1-999+)"
    else:
        print "You must provide version number."
        print "  For exmaple:\t python build.py 0.32"

if __name__ == "__main__":
    dispatch(sys.argv[1:])