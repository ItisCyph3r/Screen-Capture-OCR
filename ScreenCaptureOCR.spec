# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('resources', 'resources')],
    hiddenimports=['PIL._tkinter_finder', 'win32clipboard', 'cv2', 'pytesseract', 'numpy', 'numpy.core._multiarray_umath', 'numpy.core.multiarray', 'numpy.core._dtype_ctypes'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'notebook', 'pandas', 'scipy', 'PyQt5', 'PySide2', 'IPython', 'sphinx', 'tensorflow', 'torch', 'sklearn', 'numpy.random._examples', 'numpy.fft.tests', 'numpy.linalg.tests', 'numpy.ma.tests', 'numpy.matrixlib.tests', 'numpy.polynomial.tests', 'numpy.random.tests'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ScreenCaptureOCR',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='src\\version_info.txt',
    uac_admin=True,
)
