# -*- mode: python -*-
a = Analysis(['/Users/serge/Documents/s/stars/git/stars/stars/starsgui.py'],
             pathex=['/Users/serge/Downloads/pyinstaller-pyinstaller-cd90936/stars'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='stars',
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='stars')
app = BUNDLE(coll,
             name='stars.app',
             icon=None)
