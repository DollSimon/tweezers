# -*- mode: python -*-

block_cipher = None


a = Analysis(['SegmentSelector.py'],
             pathex=['/Users/christophehrlich/Documents/Python/tweezers/SegmentSelector'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='SegmentSelector',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False,
          icon='SegmentSelector.ico')
app = BUNDLE(exe,
             name='SegmentSelector.app',
             icon='SegmentSelector.icns',
             bundle_identifier=None,
             info_plist={
                'NSHighResolutionCapable': 'True'
             })
