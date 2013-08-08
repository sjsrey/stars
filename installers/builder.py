import os

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


