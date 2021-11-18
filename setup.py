from setuptools import setup
from glob import glob

data_files = []
directories = glob.glob('data/subfolder?/subfolder??/')
for directory in directories:
    files = glob.glob(directory+'*')
    print(files)
    data_files.append((directory, files))

setup(
   name='nrv',
   version='0.0.1',
   description='Neuron Virtualizer',
   author='Florian Kolbl - Roland Giraud - Louis Regnacq - Thomas Couppey',
   packages=['nrv'],  #same as name
    data_files = [('', ['nrv/log/NRV.log'])],


   #install_requires=['bar', 'greek'], #external packages as dependencies
   #scripts=[
#        'scripts/cool',
#            'scripts/skype',
#           ]
)
