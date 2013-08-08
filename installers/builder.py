import os

if not os.path.exists("mac"):
    os.makedirs("mac")

cmd ="cd mac;tar xzvf ../pyinstaller-pyinstaller-v2.0-518-gcd90936.tar.gz "
os.system(cmd)

