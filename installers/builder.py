"""
Builder of binaries for windows and mac os x (aqua and x11)

Usage
=====

python builder.py -t [mac|macx11|win]



Requirements
============

pyinstaller


pyinstaller-pyinstaller-v2.05-518-gcd90936.tar.gz is required for the mac
builds and should reside in the same directory as this script.

for windows the same version of the installer needs to be unzipped in this
directory such that the source for that package resides in a subdirectory
of the current folder


pyinstaller is not part of the source code for stars


Notes
=====
Location of binaries for the Mac is 
    mac/stars/dist/stars.app
The stars.app folder can be compressed or dragged to a new location. Opening
stars.app will run the program

Location of Windows binary is
    win/stars/dist/stars/stars.exe
To relocate this, create a shortcut and move the shortcut to a desired
location.

"""
import os
import sys
import getopt
import shutil


__author__ = "Sergio Rey <sjsrey@gmail.com>"

def mac():
    """
    Builds a binary assuming enthought python 7.3 is installed
    """
    if not os.path.exists("mac"):
	os.makedirs("mac")

	cmd ="cd mac;tar xzvf ../pyinstaller-pyinstaller-v2.0-518-gcd90936.tar.gz "
	os.system(cmd)
	cmd ="cd mac;cp -R  pyinstaller-pyinstaller-cd90936/* ."
	os.system(cmd)
	cmd ="cd mac; /Library/Frameworks/Python.framework/Versions/7.3/bin/python pyinstaller.py --windowed --name=stars ../../stars/starsgui.py"
	os.system(cmd)

	targetPath = "mac/stars/dist/stars.app/Contents/MacOS/."
	cmds = ["cp ../../stars/stars/splash.gif",
		"cp -R ../../stars/stars/data",
		"cp ../../stars/stars/COPYING",
		"cp ../../stars/stars/credits.txt"]

	for cmd in cmds:
	    cmd = cmd + " " + targetPath
	    print cmd
	    os.system(cmd)
    # icon
    cmd = "cp ../../stars/stars/stars.icns"
    cmd +=" mac/stars/dist/stars.app/Contents/Resources/icon-windowed.icns"
    print cmd
    os.system(cmd)

def macx11():

    """
    Builds a binary using anaconda which does not include aqua so x11 gui toolkit is used
    """
    if not os.path.exists("mac"):
	os.makedirs("mac")

	cmd ="cd mac;tar xzvf ../pyinstaller-pyinstaller-v2.0-518-gcd90936.tar.gz "
	os.system(cmd)
	cmd ="cd mac;cp -R  pyinstaller-pyinstaller-cd90936/* ."
	os.system(cmd)
	cmd ="cd mac; python pyinstaller.py --windowed --name=stars ../../stars/starsgui.py"
	os.system(cmd)

	targetPath = "mac/stars/dist/stars.app/Contents/MacOS/."
	cmds = ["cp ../../stars/stars/splash.gif",
		"cp -R ../../stars/stars/data",
		"cp ../../stars/stars/COPYING",
		"cp ../../stars/stars/credits.txt"]

	for cmd in cmds:
	    cmd = cmd + " " + targetPath
	    print cmd
	    os.system(cmd)
    # icon
    cmd = "cp ../../stars/stars/stars.icns"
    cmd +=" mac/stars/dist/stars.app/Contents/Resources/icon-windowed.icns"
    print cmd
    os.system(cmd)

def win():
    import subprocess
    src = "pyinstaller-pyinstaller-cd90936"
    dst = "win"
    shutil.copytree(src,dst)
    cmd = "python pyinstaller.py --windowed --name=stars"
    cmd +=" --icon=../../stars/stars.ico ../../stars/starsgui.py"
    res = subprocess.Popen(cmd, cwd="win/")
    res.wait()
    targetPath = "win/stars/dist/stars/."
    cmds = ["cp ../../stars/stars/splash.gif",
	"cp -R ../../stars/stars/data",
    "cp ../../stars/stars/COPYING",
	"cp ../../stars/stars/credits.txt"]
    for cmd in cmds:
        cmd = cmd + " " + targetPath
        print cmd
        r = subprocess.Popen(cmd)
        r.wait()

dispatcher = {}
dispatcher['mac'] = mac
dispatcher['macx11'] = macx11
dispatcher['win'] = win

def main(argv):
    def usage():
        print 'usage: builder.py -t [mac|macx11|win]'
    opts, args = getopt.getopt(argv,"ht:") 
    if opts != []:
        for o,a in opts:
            if o == '-h':
                usage()
                sys.exit(0)
            elif o == "-t":
                target = a
                if target in dispatcher:
                    dispatcher[target]()
                else:
                    usage()
            else:
                usage()
    else:
       usage()
if __name__ == "__main__":
    main(sys.argv[1:])

