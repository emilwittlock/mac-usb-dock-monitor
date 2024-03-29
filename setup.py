"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['index.py']
DATA_FILES = [('', ['config.ini'])]
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'duck.icns',
    'plist': {
        'CFBundleShortVersionString': '0.2.1',
        'LSUIElement': True,
    },
    'packages': ['rumps'],
}

setup(
    app=APP,
    name='Dock monitor',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'], install_requires=['rumps', 'configparser']
)
