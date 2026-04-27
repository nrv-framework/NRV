"""
Everything about the configuration, gathers :in a singleton:
* Macine configuration,
* NRV parameters,
* ...
"""

from ._NRV_Singleton import NRV_singleton
from ._machine_config import MachineConfig
from ._parameters import nrv_parameters
from importlib.metadata import version, packages_distributions


LOGO = r"""
                      :                      
                   :  + ::                   
                ::    +    ::                
             ::       +     + ::             
          ::++++      +     +    ::          
       ::         +++:::+++        +::       
    ::              :-=-:      :::     :     
   :  ::::           :::       :::       :   
   :    +             +         +        :   
   : #####    ########### ####  +  ####  :   
   : ######   ###    ##### #### +  ####  :   
   : #######  ###     ####  ### + ####   :   
   : ######## ###  ######   ####+ ###    :   
   : ####  ######  ####      ########    :   
   : ####   #####   ####      ######     :   
   : ####    ####    ####     #####      :   
   :    +            ++         +        :   
    ::  +     :::     +         +      :     
       ::     ::     ++   :::   +   ::       
          ::   +     ++   :::   +::          
             ::+     ++    +  ::             
                ::   ++    ::                
                   : ++ ::                   
                      :                      
"""


class nrv_config(metaclass=NRV_singleton):
    """A unique class to handle all the configuration"""

    def __init__(self):
        """
        Initialize the global configuration wrapper.
        """
        self.machine_config = MachineConfig()
        self.framework_parameters = nrv_parameters()
        self.this_nrv = {
            "version": version("nrv-py"),
            "available_lib": []
        }
        distr = packages_distributions()
        for key in distr:
            self.this_nrv["available_lib"].append(key)

    def display_machine_config(self):
        """
        Print the current machine configuration.
        """
        print(self.machine_config)


# Declaring an instance of nrv_config anyway
CONFIG = nrv_config()

# info function


def info(logo=False, machine=False, dep=False):
    """
    A function to print information on NRV in the terminal, by default number
    of version and OS. This function is usefull for scripts that run on Bots.
    It should also be used to display configuration before filling an Issue.

    Parameters
    ----------
    logo    : Bool
        prints the ASCII art wonderfull logo of NRV if set to True.
        Default is False.
    machine : Bool
        prints the informations on the machine that currently runs.
    dep : Bool
        prints the list of available python packages.

    """
    line = "NRV version "+str(CONFIG.this_nrv["version"])+", running on "+str(CONFIG.machine_config.OS_name)
    print("*" * (len(line) + 4))
    print("* " + line + " *")
    print("*" * (len(line) + 4))
    if logo:
        print(LOGO)
    if machine:
        CONFIG.display_machine_config()
    if dep:
        print('\n This is the list of reachable librairies:')
        for lib in CONFIG.this_nrv["available_lib"]:
            print('\t - '+lib)
    return True
