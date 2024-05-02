Stimuli
=======

Electrical stimulation is completely described using electrodes that can
deliver *stimuli*, which is the object of present chapter.

Electrical stimuli are electrical signals, mostly current quantities,
that are applied in the extracellular (marginaly to the intracellular)
to trigger cell reactions. In NRV, a special class has been designed to
handle stimuli.

A stimulus is described as an asynchronous signal: there is no need for
a regular clock to describe the stimulus changes in time. As a
consequence, the stimulus is based on two lists: - a first list called
‘s’ contains the signal values, - a second list called ‘t’ contains the
time stamps for the different values.

The class constructor takes no positional arguments, however there is
one optional argument: - s_init: the initial value of the stimulus at
time t=0.

At the instantiation, a stimulus only gets its initial value at time
t=0, and lists ‘s’ and ‘t’ have a length of 1. Here is a minimal example
of instatiation of a stimulus:

.. code:: python

    import nrv
    
    stim1 = nrv.stimulus()
    print(len(stim1.s))
    print(len(stim1.t))
