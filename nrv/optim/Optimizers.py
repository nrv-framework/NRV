from abc import ABCMeta, abstractmethod
import os
from typing import Any
import numpy as np
import matplotlib.pyplot as plt
from time import perf_counter, asctime, localtime
from multiprocessing import cpu_count
import traceback
import json
import sys
import pyswarms as ps
from pyswarms.backend.topology import Star, Ring


from ..backend.NRV_Class import NRV_class
from ..backend.parameters import parameters
from ..backend.log_interface import logging
from .optim_utils.optim_results import optim_results

dir_path = os.environ["NRVPATH"] + "/_misc"
dir_path + "/log/NRV.log"
# mymodule.py

class Optimizer(NRV_class, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, method=None):
        super().__init__()
        self._method = method
        self.swarm_optimizer = False
    
    def minimize(self, f, **kwargs):
        self.set_parameters(**kwargs)
        return optim_results(self.save(save=False))

    def __call__(self, f,**kwargs: Any) -> optim_results:
        return self.minimize(f,**kwargs)


class PSO_optimizer(Optimizer):
    def __init__(self, n_particles=5, dimensions=50, options=None, N_it=1, n_processes=None,
        bounds=(0, 0), init_pos=None, print_time=False, opt_type="global", static=False, ftol=None, 
        ftol_iter=1, bh_strategy="nearest", oh_strategy=None, save_results=False,
        saving_file="pso_results.json", comment=None):
        """
        Perform a Particle swarm optimization (PSO) on with a defined cost function using pyswarms
        library[1]

        Parameters
        ----------
        n_particles           	: int
            number of particle of the swarm, by default 5
        dimensions              : int
            number of dimensions of each particle
        options                 : dict
            hyperparameter of the PSO
        N_it                    : int
            number of iteration of the PSO
        n_processes             : int
            number of process used to parallelize cost calculation, by default None
        bounds                  : tupple
            bounds of the particle, if equal no bounds, by default (0, 0)
        init_pos                : array
            initial position of the particles if None random, by default None
        print_time              : bool
            if True, print the optimisation time, by default True
        opt_type                : str
            Neightboorhood type, by default 'global'
            type possibly:
                    'global'                : Global best PSO (star topology)
                    'local'                 : Local best PSO (ring topology)
        static      : bool
            if False and opt_type is local, update the neigthboorhood of each particle every iterations
        bh_strategy             : str
            out of bound position strategy for pyswarms optimizer [2]:
                    'nearest'               : Round the value to the nearest bound (default)
                    'periodic'              : set to the modulus of the value between the two bounds
                    'random'                : set to a random value
                    'shrink'                : reduce the velocity to finish land on the bound
                    'reflective'            : mirror the position form inside to ouside the bounds
                    'intermediate'          : set to intermediate value between previous pos and bound
        oh_strategy             : dict (like {'w':str, 'c1':str, 'c2':str})
            Dynamic options strategy for pyswarms optimizer [3], if None static options,
            by default None:
                    'exp_decay'             : Decreases the parameter exponentially between limits
                    'lin_variation'         : Decreases/increases the parameter linearly between limits
                    'nonlin_mod'            : Decreases/increases the parameter between limits
                                            according to a nonlinear modulation index
                    'rand'                  : takes a uniform random value between limits
        ftol                    : float
            relative error in objective_func(best_pos) acceptable for convergence, if None -np.inf
            default None
        ftol                    : int
            number of iterations over which the relative error in objective_func(best_pos) is
            acceptable for convergence, by default 1
        save_results            : bool
            save or not the output in a .json file, by default False
        saving_file             : str
            name of the file on wich the output should be saved, by default 'pso_results.json'

        Returns
        -------
        results     : dict
            contains all the parameters and outputs of the PSO

        Note
        ----
        links to pyswarms doc:
        [1] https://pyswarms.readthedocs.io/en/latest/index.html
        [2] https://pyswarms.readthedocs.io/en/latest/api/pyswarms.handlers.html
        """
        """import pyswarms as ps
        from pyswarms.utils.plotters import plot_cost_history
        from pyswarms.backend.topology import Star, Ring"""
        super().__init__("PSO")
        self.swarm_optimizer = True
        self.n_particles = n_particles
        self.dimensions = dimensions
        self.options = options
        self.N_it = N_it
        self.n_processes = n_processes
        self.bounds = bounds
        self.init_pos = init_pos
        self.print_time = print_time
        self.opt_type = opt_type
        self.static = static
        self.ftol = ftol
        self.ftol_iter = ftol_iter
        self.bh_strategy = bh_strategy
        self.oh_strategy = oh_strategy
        self.save_results = save_results
        self.saving_file = saving_file
        self.comment = comment

    def minimize(self, f_swarm, **kwargs):
        """
        Perform a Particle swarm optimization

        Parameters
        ----------
        cost_function_swarm     : func
            function taking in parameter a swarm (dim-dimensions array) and returning the cost for each
            particle (1-dimensionnal array)
        kwargs                  : dict
            containing parameters to change to class (PSO_optimizer.__init__)
        """
        results = super().minimize(f_swarm, **kwargs)


        verbose = parameters.get_nrv_verbosity() > 2
        # initial position
        if not np.iterable(self.init_pos):
            self.init_pos = None

        # create pyswarms bounds
        if np.size(self.bounds)>2:
            psbounds = self.bounds
        elif self.bounds[0] == self.bounds[1]:
            psbounds = None
        else:
            max_bound = max(self.bounds) * np.ones(self.dimensions)
            min_bound = min(self.bounds) * np.ones(self.dimensions)
            psbounds = (min_bound, max_bound)

        if self.opt_type.lower()=="local":
            if not self.options or len(self.options) <5:
                self.options = {'c1': 0.5, 'c2': 0.5, 'w':0.5, 'k' : 5, 'p' : 2}
            topology = Ring(static=self.static)

        # Check number of pcu
        else:
            if not self.options:
                self.options = {'c1': 0.5, 'c2': 0.5, 'w':0.5}
            topology = Star()

        if self.n_processes != None and self.n_processes > cpu_count()-1:
            answer = input("Number of process higher than number of cpu\n"+
                "continue with one process (Y/n)\n")
            if answer == "Y":
                self.n_processes = None
            else:
                print("Terminated")
                return(False)

        # Initialize results directory

        results['date'] = asctime(localtime())
        if self.opt_type.lower()!='global':
            results['optimization_parameters']['static']=self.static

        if self.comment is not None: 
            results['comment'] = self.comment

        results['status'] = "Processing"

        if self.save_results:
            with open(self.saving_file, 'w') as outfile:
                json.dump(results, outfile)

        if self.ftol is None:
            self.ftol = -np.inf
            self.ftol_iter = 1

        try:
            # Call instance of PSO
            optimizer = ps.single.general_optimizer.GeneralOptimizerPSO(n_particles=self.n_particles,
                dimensions=self.dimensions, options=self.options, oh_strategy=self.oh_strategy, bounds=psbounds, ftol=self.ftol,
                ftol_iter=self.ftol_iter, init_pos=self.init_pos, bh_strategy=self.bh_strategy, topology=topology)

            # Perform optimization
            t0 = perf_counter()
            cost, pos = optimizer.optimize(f_swarm, iters=self.N_it, n_processes=self.n_processes,
                verbose=verbose)
            t_opt = perf_counter()-t0

            pos_history = np.array(optimizer.pos_history)
            self.N_it = np.shape(pos_history[:,0,:])[0]

            if self.print_time:
                print('the cumputing time for ', self.N_it, ' iterations and ', self.n_particles,
                    ' particles is : ',t_opt,'s')

            # Save results
            results['optimization_parameters']['N_it'] = self.N_it
            results['status'] = "Completed"
            results['best_position'] = pos.tolist()
            results['sulution'] = results['best_position']
            results['best_cost'] = cost

            results['optimization_time'] = t_opt
            results['cost'] = optimizer.cost_history
            results['neighbor_bestc'] = optimizer.mean_neighbor_history
            results['personal_bestc'] = optimizer.mean_pbest_history

            velocity_history = np.array(optimizer.velocity_history)
            pos_history = np.array(optimizer.pos_history)
            for i in range(self.n_particles):
                results['position'+str(i+1)] = pos_history[:,i,:].tolist()
                results['velocity'+str(i+1)] = velocity_history[:,i,:].tolist()
            if self.save_results:
                with open(self.saving_file, 'w') as outfile:
                    json.dump(results, outfile)
        except KeyboardInterrupt:
            results['status'] = "Interrupted"
            if self.save_results:
                with open(self.saving_file, 'w') as outfile:
                    json.dump(results, outfile)
            raise KeyboardInterrupt
            sys.exit(1)
        except:
            results['status'] = "Failed"
            results['Error_from_prompt'] = traceback.format_exc()
            print(results['Error_from_prompt'])
            if self.save_results:
                with open(self.saving_file, 'w') as outfile:
                    json.dump(results, outfile)

        return results

