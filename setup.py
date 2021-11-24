from setuptools import setup

setup(
   name='nrv',
   version='0.0.1',
   description='NeuRon Virtualizer',
   long_description = 'file: README.md',
   author='Florian Kolbl - Roland Giraud - Louis Regnacq - Thomas Couppey',
   packages=['nrv'],  #same as name
   include_package_data = True,
   url = 'https://github.com/fkolbl/NRV',
   classifiers =
    'Programming Language :: Python :: 3',
    'License :: CeCILL',
    'Operating System :: OS Independent',
    install_requires=['mph', 'numpy','scipy','faulthandler','math','matplotlib','pylab','numba','json','ezdxf','icecream'], #external packages as dependencies
    python_requires = >=3.6
)
