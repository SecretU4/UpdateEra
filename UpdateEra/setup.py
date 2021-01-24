from distutils.core import setup
import py2exe

setup(
      options={"py2exe":{"optimize":1}},
      console=['UpdateEra.py']
      )