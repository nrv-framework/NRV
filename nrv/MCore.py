"""
NRV-Multi-Core/Parallel computing handling
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import numpy as np

try:
    import mpi4py.MPI as mpi
    comm = mpi.COMM_WORLD
    MCore_Flag = True
except ImportError:
    MCore_Flag = False

class Mcore_handler():
    """
    Class to handle parallel processing (cores, no threads) in NRV2
    """
    def __init__(self, Flag):
        """
        Instantiation of Mcore

        Parameters
        ----------
        Flag    : bool
            should be true if mpi4py is installed, to be handled by user !
        """
        super(Mcore_handler, self).__init__()
        self.Flag = Flag
        if self.Flag:
            self.rank = comm.rank
            self.size = comm.size
        else:
            self.rank = 0
            self.size = 1

    def is_alone(self):
        """
        Check if the process is runing alone or if other instances have been launched.

        Returns
        -------
        alone   : bool
            True if the programm is the only instance launched, else False
        """
        return self.size == 1

    def is_master(self):
        """
        Check if the process is master or not whe parallel computing

        Returns
        -------
        master  : bool
            True if multiple instances are launched and the current process is the master (rank 0)
        """
        return not self.is_alone() and self.rank == 0

    def do_master_only_work(self):
        """
        Check if the process is alone or it is the master to perform non splitable job

        Returns
        -------
        only    : bool
            True if the process is alone or if it is the master, else False
        """
        return self.is_alone() or self.is_master()

    def say_hello(self):
        """
        Display a sentence from each process on prompt. For debug only
        """
        if self.is_alone():
            print('Hi, I am the only core launched')
        elif self.is_master():
            print('Hi, I am the master core')
        else:
            print('Hi, I am a slave core, my ID is '+str(self.rank))

    def split_job_from_arrays(self, len_arrays):
        """
        Split an array for parallel independant computing, by sharing independant sub-spaces \
        of array index

        Parameters
        ----------
        len_arrays  : int
            length of the array containing the full job to perform in parallel

        Returns
        -------
        mask    : np.array
            subspace of the array indexes, specific to each instantiation of the programm
        """
        if self.is_alone():
            mask = np.arange(len_arrays)
        else:
            if self.is_master():
                all_indexes = np.arange(len_arrays)
                mask_chunks = np.array_split(all_indexes, self.size, axis=0)
            else:
                mask_chunks = None
            mask = comm.scatter(mask_chunks, root=0)
        return mask

    def split_job_from_arrays_to_slaves(self, len_arrays):
        """
        Split an array for parallel independant computing, by sharing independant sub-spaces \
        of array index, the master gets a table of all jobs to do initialized to False

        Parameters
        ----------
        len_arrays  : int
            length of the array containing the full job to perform in parallel

        Returns
        -------
        mask    : np.array
            subspace of the array indexes, specific to each instantiation of the programm
        """
        if self.is_master():
            all_indexes = np.arange(len_arrays)
            jobs_to_do = np.asarray(np.full(len(all_indexes),False))
            chunks = np.array_split(all_indexes, self.size-1, axis=0)
            chunks.insert(0,jobs_to_do)
        else:
            chunks = None
        chunk = comm.scatter(chunks, root=0)
        return chunk

    def master_broadcasts_array_to_all(self, var):
        """
        Broadcast an array to all instances of the process (share jobs performed by the master only)

        Parameters
        ----------
        var : np.array
            variable to broadcast, from the master only, esle None

        Returns
        -------
        data    : np.array
            variable broadcasted in all instances
        """
        if self.is_alone():
            data = var
        else:
            if self.rank == 0:
                data = var
            else:
                data = None
            data = comm.bcast(data, root=0)
        return data

    def gather_jobs_as_array(self, partial_result):
        """
        Gather the jobs performed by all instances to the master

        Parameters
        ----------
        partial_result  : np.array
            individual result from an instance

        Returns
        -------
        result  : np.array
            global array if master or alone, else None
        """
        if self.is_alone():
            final_result = partial_result
        else:
            results = comm.gather(partial_result, root=0)
            if self.is_master():
                final_result = np.concatenate(tuple(results))#,axis = 1)
            else:
                final_result = None
        return final_result

    def send_data_to_master(self, data):
        """
        Send a dictionary of data directly to the master.

        Parameters
        ----------
        data : dict
            data to send
        """
        comm.send(data, dest=0)

    def recieve_data_from_slave(self):
        """
        Recieve data from anay source

        Returns:
        --------
        data
        """
        data = comm.recv(source=mpi.ANY_SOURCE)
        return data

    def send_back_array_to_dest(self, data, destination):
        """
        Send a numpy array to a slave

        Parameters
        ----------
        data        : np.array
            data to send
        destination : int
            ID of the process to send the data
        """
        comm.send(data, dest=destination)

    def recieve_potential_array_from_master(self):
        """
        Recieve potenatial data from the master as a numpy array

        Parameters
        ----------
        N_points : int
            number of point of the x-coordinate vector
        N_elec   : int
            number of electrode in the simulation
        """
        data = comm.recv(source=0)
        return data

    def send_synchronization_flag(self):
        """
        Blocking collective communication to force all process to synchronize to a specific line of code

        Returns
        -------
        bool
            a flag set to True
        """
        if self.rank == 0:
            Validation_Flag = True
        else:
            Validation_Flag = None
        Validation_Flag = comm.bcast(Validation_Flag, root=0)
        return Validation_Flag

# public interface
MCH = Mcore_handler(MCore_Flag)
