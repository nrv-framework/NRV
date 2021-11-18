from setuptools import setup

setup(
   name='nrv',
   version='0.0.1',
   description='Neuron Virtualizer',
   author='Florian Kolbl - Roland Giraud - Louis Regnacq - Thomas Couppey',
   packages=['nrv'],  #same as name
   setup_requires=['log'],
   include_package_data=True,
   #install_requires=['bar', 'greek'], #external packages as dependencies
   #scripts=[
#        'scripts/cool',
#            'scripts/skype',
#           ]
)
