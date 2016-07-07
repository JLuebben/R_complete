# -*- mode: python -*-
a = Analysis(['rcomplete.py'],
             pathex=['D:\\R_complete'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='rcomplete_Win64.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
