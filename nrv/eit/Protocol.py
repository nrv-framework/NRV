from ..backend._NRV_Class import NRV_class
from copy import deepcopy
import numpy as np


class protocol(NRV_class):
    """
    Caution not fully implemented..
    First version of a eit protocol class
    """

    def __init__(self, p=None):
        super().__init__()
        self._injection = []
        self._recording = []
        self.pos = 0
        if isinstance(p, protocol):
            self._injection = deepcopy(p._injection)
            self._recording = deepcopy(p._recording)

    @property
    def rec_mat(self):
        m_mat = [[]]
        for i in range(len(self) - 1):
            m_mat[-1] += [self._recording[i]]
            if self._injection[i] != self._injection[i + 1]:
                m_mat += [[]]
        m_mat[-1] += [list(self._recording[-1])]
        return np.array(m_mat)

    @property
    def inj_mat(self):
        e_mat = [self._injection[0]]
        for i in range(len(self) - 1):
            if self._injection[i] != self._injection[i + 1]:
                e_mat += [self._injection[i + 1]]
        return np.array(e_mat)

    def change_electrode_id(self, oldid: int, newid: int):
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
        if inj is not None:
            self._injection += [inj]
        else:
            self._injection += [self._injection[-1]]

    def add_recording(self, rec=None):
        if rec is not None:
            self._recording += [rec]
        else:
            self._recording += [self._recording[-1]]

    def add_patern(self, inj=None, rec=None):
        if len(self) == 0 and (inj is None or rec is None):
            raise IndexError("empty ") from None
        else:
            self.add_injection(inj)
            self.add_recording(rec)

    def clear(self):
        self._injection = []
        self._recording = []

    def push(self, inj=None, rec=None):
        self.add_patern(inj=inj, rec=rec)

    def pop(self):
        try:
            return self._injection.pop(), self._recording.pop()
        except IndexError:
            raise IndexError("pop from an empty stack") from None

    def __getitem__(self, index):
        return (self._injection[index], self._recording[index])

    def __len__(self):
        return len(self._injection)

    def add_n(self, n: int):
        if n + np.min(self) < 0:
            print("Warning: protocol cannot have negative id of electrode")
            print(f"Warning: protocol cannot have negative id of electrode")
            n = np.min(self)

        self._injection = [(n + i, n + j) for i, j in self._injection]
        self._recording = [(n + i, n + j) for i, j in self._recording]

    def mul_n(self, n: int):
        self._injection = [(n * i, n * j) for i, j in self._injection]
        self._recording = [(n * i, n * j) for i, j in self._recording]

    def __sub__(self, n: int):
        """ """
        p = protocol(self)
        p.add_n(-n)
        return p

    def __rsub__(self, n: int):
        return self.__add__(-n)

    def __add__(self, n: int):
        """ """
        p = protocol(self)
        p.add_n(n)
        return p

    def __radd__(self, n: int):
        return self.__add__(n)

    def __mul__(self, n: int):
        """ """
        p = protocol(self)
        p.mul_n(n)
        return p

    def __rmul__(self, n: int):
        return self.__add__(n)


class pyeit_protocol(protocol):
    def __init__(self, n_elec=8, inj_offset=1, start_elec=0):
        super().__init__()
        self.n_elec = n_elec
        self.inj_offset = inj_offset
        self.start_elec = start_elec
        self.__generate_protocol()

    def __generate_protocol(self):
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
        for key in kwds:
            if key in self.__dict__:
                self.__dict__[key] = kwds[key]
        self.__generate_protocol()
