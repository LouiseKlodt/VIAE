# setup.py
from setuptools import setup, find_packages

setup(name='viae',
      version='1.0',
      author='Louise Klodt',
      url='http://www.github.com/louiseklodt',
      packages=find_packages(exclude=['test']),
)