from setuptools import setup
import glob

data_files = []
directories = glob.glob('nrv/')
for directory in directories:
    files = glob.glob(directory+'*')
    data_files.append((directory, files))


setup(
   name='nrv',
   version='0.0.1',
   description='Neuron Virtualizer',
   author='Florian Kolbl - Roland Giraud - Louis Regnacq - Thomas Couppey',
   packages=['nrv'],  #same as name
   data_files = data_files,
    #data_files = [('nrv', glob('nrv/**/*', recursive=True))], # includes sub-folders - recursive


   #install_requires=['bar', 'greek'], #external packages as dependencies
   #scripts=[
#        'scripts/cool',
#            'scripts/skype',
#           ]
)
