from setuptools import setup
from glob import glob

setup(
   name='nrv',
   version='0.0.1',
   description='Neuron Virtualizer',
   author='Florian Kolbl - Roland Giraud - Louis Regnacq - Thomas Couppey',
   packages=['nrv'],  #same as name
    data_files = [('nrv', glob('nrv/**/*', recursive=True))], # includes sub-folders - recursive


   #install_requires=['bar', 'greek'], #external packages as dependencies
   #scripts=[
#        'scripts/cool',
#            'scripts/skype',
#           ]
)
