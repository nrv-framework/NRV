#! to remove

from ...backend._NRV_Class import NRV_class
from copy import deepcopy
import numpy as np


class protocol(NRV_class):
    """
    Caution not fully implemented..
    First version of a eit protocol class
    """

    def __init__(self, p=None):
        """
        Initialize an EIT protocol container.

        Parameters
        ----------
        p : protocol | None, optional
            Existing protocol to copy.
        """
        super().__init__()
        self._injection = []
        self._recording = []
        self.pos = 0
        if isinstance(p, protocol):
            self._injection = deepcopy(p._injection)
            self._recording = deepcopy(p._recording)

    @property
    def rec_mat(self):
        """
        Recording pairs grouped by injection pattern.

        Returns
        -------
        np.ndarray
            Matrix whose rows correspond to recording pairs associated with each
            injection pattern.
        """
        m_mat = [[]]
        for i in range(len(self) - 1):
            m_mat[-1] += [self._recording[i]]
            if self._injection[i] != self._injection[i + 1]:
                m_mat += [[]]
        m_mat[-1] += [list(self._recording[-1])]
        return np.array(m_mat)

    @property
    def inj_mat(self):
        """
        Unique injection pairs present in the protocol.

        Returns
        -------
        np.ndarray
            Array of injection electrode pairs.
        """
        e_mat = [self._injection[0]]
        for i in range(len(self) - 1):
            if self._injection[i] != self._injection[i + 1]:
                e_mat += [self._injection[i + 1]]
        return np.array(e_mat)

    def change_electrode_id(self, oldid: int, newid: int):
        """
        Replace one electrode identifier everywhere in the protocol.

        Parameters
        ----------
        oldid : int
            Electrode identifier to replace.
        newid : int
            Replacement identifier.
        """
        for i, e in enumerate(self._injection):
            e1, e2 = e
            if oldid == e[0]:
                e1 = newid
            if oldid == e[1]:
                e2 = newid
            self._injection[i] = e1, e2
        for i, e in enumerate(self._recording):
            e1, e2 = e
            if oldid == e[0]:
                e1 = newid
            if oldid == e[1]:
                e2 = newid
            self._recording[i] = e1, e2

    def add_injection(self, inj=None):
        """
        Append one injection pair to the protocol.

        Parameters
        ----------
        inj : tuple[int, int] | None, optional
            Injection pair to append. If omitted, repeat the previous one.
        """
        if inj is not None:
            self._injection += [inj]
        else:
            self._injection += [self._injection[-1]]

    def add_recording(self, rec=None):
        """
        Append one recording pair to the protocol.

        Parameters
        ----------
        rec : tuple[int, int] | None, optional
            Recording pair to append. If omitted, repeat the previous one.
        """
        if rec is not None:
            self._recording += [rec]
        else:
            self._recording += [self._recording[-1]]

    def add_patern(self, inj=None, rec=None):
        """
        Append one injection/recording pattern to the protocol.

        Parameters
        ----------
        inj : tuple[int, int] | None, optional
            Injection pair to append.
        rec : tuple[int, int] | None, optional
            Recording pair to append.
        """
        if len(self) == 0 and (inj is None or rec is None):
            raise IndexError("empty ") from None
        else:
            self.add_injection(inj)
            self.add_recording(rec)

    def clear(self):
        """
        Remove all stored protocol patterns.
        """
        self._injection = []
        self._recording = []

    def push(self, inj=None, rec=None):
        """
        Stack-style alias of :meth:`add_patern`.
        """
        self.add_patern(inj=inj, rec=rec)

    def pop(self):
        """
        Remove and return the last protocol pattern.

        Returns
        -------
        tuple
            Last injection pair and recording pair.
        """
        try:
            return self._injection.pop(), self._recording.pop()
        except IndexError:
            raise IndexError("pop from an empty stack") from None

    def __getitem__(self, index):
        """
        Return one stored injection/recording pattern.

        Parameters
        ----------
        index : int
            Pattern index.

        Returns
        -------
        tuple
            Injection pair and recording pair.
        """
        return (self._injection[index], self._recording[index])

    def __len__(self):
        """
        Number of stored protocol patterns.

        Returns
        -------
        int
            Number of injection/recording pairs.
        """
        return len(self._injection)

    def add_n(self, n: int):
        """
        Shift all electrode identifiers by a constant offset.

        Parameters
        ----------
        n : int
            Offset added to every electrode identifier.
        """
        if n + np.min(self) < 0:
            print("Warning: protocol cannot have negative id of electrode")
            print(f"Warning: protocol cannot have negative id of electrode")
            n = np.min(self)

        self._injection = [(n + i, n + j) for i, j in self._injection]
        self._recording = [(n + i, n + j) for i, j in self._recording]

    def mul_n(self, n: int):
        """
        Multiply all electrode identifiers by a constant factor.

        Parameters
        ----------
        n : int
            Multiplicative factor.
        """
        self._injection = [(n * i, n * j) for i, j in self._injection]
        self._recording = [(n * i, n * j) for i, j in self._recording]

    def __sub__(self, n: int):
        """ """
        p = protocol(self)
        p.add_n(-n)
        return p

    def __rsub__(self, n: int):
        """
        Right-handed subtraction alias using protocol shifting.
        """
        return self.__add__(-n)

    def __add__(self, n: int):
        """ """
        p = protocol(self)
        p.add_n(n)
        return p

    def __radd__(self, n: int):
        """
        Right-handed addition alias using protocol shifting.
        """
        return self.__add__(n)

    def __mul__(self, n: int):
        """ """
        p = protocol(self)
        p.mul_n(n)
        return p

    def __rmul__(self, n: int):
        """
        Right-handed multiplication alias.
        """
        return self.__add__(n)


class pyeit_protocol(protocol):
    """
    Convenience protocol builder matching the standard PyEIT acquisition scheme.
    """

    def __init__(self, n_elec=8, inj_offset=1, start_elec=0):
        """
        Build a protocol compatible with the default PyEIT drive/measure ordering.

        Parameters
        ----------
        n_elec : int, optional
            Number of electrodes.
        inj_offset : int, optional
            Offset between the positive and negative injection electrodes.
        start_elec : int, optional
            First electrode used to build the protocol.
        """
        super().__init__()
        self.n_elec = n_elec
        self.inj_offset = inj_offset
        self.start_elec = start_elec
        self.__generate_protocol()

    def __generate_protocol(self):
        """
        Generate the full list of PyEIT-compatible injection and recording pairs.
        """
        self.clear()
        for i_inj in range(self.n_elec):
            inj_pat = (
                (self.start_elec + i_inj) % self.n_elec,
                (self.start_elec + i_inj + self.inj_offset) % self.n_elec,
            )
            inj_pat = inj_pat[0], inj_pat[1]
            for i_rec in range(self.n_elec):
                e = (self.start_elec + i_rec + 1) % self.n_elec
                e_ = (self.start_elec + i_rec) % self.n_elec
                if not e in inj_pat and not e_ in inj_pat:
                    rec_pat = e, e_
                    if not (rec_pat[0] in inj_pat or rec_pat[1] in inj_pat):
                        self.add_patern(inj_pat, rec_pat)
        self = self.add_n(1)

    def set_parameters(self, **kwds):
        """
        Update protocol-generation parameters and rebuild the protocol.

        Parameters
        ----------
        **kwds : dict
            Subset of instance attributes to update before regeneration.
        """
        for key in kwds:
            if key in self.__dict__:
                self.__dict__[key] = kwds[key]
        self.__generate_protocol()
