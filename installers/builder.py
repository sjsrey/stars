import os
import sys
import getopt
import shutil

def mac():
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

def win():
    src = "pyinstaller-pyinstaller-cd90936"
    dst = "win"
    shutil.copytree(src,dst)
    # not sure cd works when chaining on windows
    cmd ="cd win; python pyinstaller.py --windowed --name=stars ../../stars/starsgui.py"
    os.system(cmd)
    targetPath = "win/stars/dist/stars.app/Contents/winOS/."
    cmds = ["cp ../../stars/stars/splash.gif",
	"cp -R ../../stars/stars/data",
	"cp ../../stars/stars/COPYING",
	"cp ../../stars/stars/credits.txt"]
    for cmd in cmds:
        cmd = cmd + " " + targetPath
        print cmd
        os.system(cmd)

dispatcher = {}
dispatcher['mac'] = mac
dispatcher['win'] = win

def main(argv):
    opts, args = getopt.getopt(argv,"ht:") 
    for o,a in opts:
	if o == '-h':
	    print 'useage: builder.py -t [mac|win]'
	    sys.exit(0)
	elif o == "-t":
	    target = a
	    print "target: ", target
	    if target in dispatcher:
		dispatcher[target]()
	    else:
		print 'useage: builder.py -t [mac|win]'
	else:
	    print 'useage: builder.py -t [mac|win]'

if __name__ == "__main__":
    main(sys.argv[1:])

