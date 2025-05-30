===============
FEM simulations
===============

In NRV, FEM model are described in :class:`~nrv.fmod.extracellular.FEM_stimulation` object. The object defines the shape of the nerve, the number of fascicles and their shapes, etc. 
If ``model_fname`` in the :class:`~nrv.fmod.extracellular.FEM_stimulation` initialization parameter set to None, NRV will use Fenicsx to solve the FEM. Else, and if ``comsol`` is also True, Comsol will be used 

.. Warning:: 
    Use FEM multiprocessing with caution. We recommend keeping Ncore to None for now.


If you want to use Comsol, you must provide a parametric comsol ``mph`` file. We currently provide three comsol template files:

- ``Nerve_1_Fascicle_1_CUFF.mph`` which describes a monofascicular nerve wrapped with a monopolar cuff electrode
- ``Nerve_1_Fascicle_1_LIFE.mph`` which describes a monofascicular nerve wrapped with a monopolar LIFE
- ``Nerve_1_Fascicle_2_LIFE.mph`` which describes a monofascicular nerve wrapped with two monopolar LIFEs

.. Warning:: 
    Use of Comsol for FEM is not recommended. Support of this feature might be removed is future release.



Nerve and fascicle are parameterized, and their geometrical properties can be modified with the :meth:`~nrv.fmod.extracellular.FEM_stimulation.reshape_nerve` and 
:meth:`~nrv.fmod.extracellular.FEM_stimulation.reshape_fascicle` methods, respectively. The :meth:`~nrv.fmod.extracellular.FEM_stimulation.reshape_outerBox` can be used to set the 
size of the outer box.

.. Note:: 
    To add fascicle to the nerve, simply call the :meth:`~nrv.fmod.extracellular.FEM_stimulation.reshape_fascicle` method
    with a new ``ÌD``:

    .. code:: python3
    
        my_FEM.reshape_fascicle(fascicle_d1, fascicle_y1, fascicle_z1, ID = 0) #create a new fascicle with ID 0
        my_FEM.reshape_fascicle(fascicle_d2, fascicle_y2, fascicle_z2, ID = 1) #create a new fascicle with ID 1
        my_FEM.reshape_fascicle(fascicle_d3, fascicle_y1, fascicle_z1, ID = 0) #change diameter of fascicle 0
        


Any :class:`~nrv.fmod.electrodes.electrode` object can be added with the :meth:`~nrv.fmod.extracellular.FEM_stimulation.add_electrode` method. This method serves also the purpose to link a :class:`~nrv.fmod.stimulus.stimulus` object to the model.

.. Warning:: 
    If the :class:`~nrv.fmod.extracellular.FEM_stimulation` is based on a comsol template, only the number of fascicle and the electrode model specified in the template can be parameterized.



Usage with a simulable object
=============================

Any :class:`~nrv.fmod.extracellular.FEM_stimulation` object can be attached to any :class:`~nrv.backend.NRV_Simulable.NRV_simulable` object using the ``attach_extracellular_stimulation`` method.

.. note::
    although technically possible, we do not recommand attaching :class:`~nrv.fmod.extracellular.FEM_stimulation` to a :class:`~nrv.nmod.fascicles.fascicle`. 
    Instead, use a monofascicular :class:`~nrv.nmod.nerve.nerve` object.

The following code snippet shows how to attach a :class:`~nrv.fmod.extracellular.FEM_stimulation` to an :class:`~nrv.nmod.axons.axon`:

::

    my_FEM = nrv.FEM_stimulation()                                          #create an FEM model with default Parameters
    my_FEM.reshape_nerve(nerve_d, nerve_l)                                  #set the diameter and length of the nerve
    my_FEM.reshape_outerBox(outer_d)                                        #set the diameter of the outer box
    my_FEM.reshape_fascicle(fascicle_d1, fascicle_y1, fascicle_z1, ID = 0)  #create a new fascicle with ID 0
    my_FEM.reshape_fascicle(fascicle_d2, fascicle_y2, fascicle_z2, ID = 1)  #create a new fascicle with ID 1
    my_FEM.add_electrode(my_electrode, my_stimulus)                         #add an electrode
    my_axon.attach_extracellular_stimulation(my_FEM)                        #attach the FEM model to the axon
    my_result = my_axon(t_sim)                                              #simulate the axon with the FEM model                       

The following code snippet shows how to attach a :class:`~nrv.fmod.extracellular.FEM_stimulation` to a :class:`~nrv.nmod.nerve.nerve`:

::

    my_FEM = nrv.FEM_stimulation()                                          #create an FEM model with default Parameters
    my_FEM.add_electrode(my_electrode, my_stimulus)                         #add an electrode
    my_nerve.attach_extracellular_stimulation(my_FEM)                       #attach the FEM model to the nerve
    my_result = my_nerve(t_sim)                                             #simulate the axon with the FEM model  

.. note::
    When attaching a :class:`~nrv.fmod.extracellular.FEM_stimulation` to a :class:`~nrv.nmod.nerve.nerve`, the geometrical parameters 
    of the nerve (its diameter, number of fascicles, etc) are overwritten with properties specified of the :class:`~nrv.nmod.nerve.nerve` object.
    This ensures consistency between the geometrical properties of the FEM model and of the neural model.