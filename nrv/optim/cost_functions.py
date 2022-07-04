import numpy as np

class CostFunction(object):
    '''
    CostFunction, a class for functions to be optimized in the context of electrical stimulation
    '''
    def __init__(self, generator, simulator, residual, kwargs_gen={},
    kwargs_s={}, kwargs_r={}, filter=None, saver=None,
    fname='cost_saver.csv'):
        self.filter, self.saver = None, None
        self.fname = fname
        ## functions
        # filtering function if applicable
        if filter is not None:
            if callable(filter):
                self.filter=filter
            else:
                raise Exception('Filter should be callable')
        # waveform generator
        if callable(generator):
            self.generator=generator
        else:
            raise Exception('Generator should be callable')
        # simulation
        if callable(simulator):
            self.simulator=simulator
        else:
            raise Exception('Simulator should be callable')
        # residual
        if callable(residual):
            self.residual=residual
        else:
            raise Exception('Residual should be callable')
        # saving function if applicable
        if filter is not None:
            if callable(filter):
                self.saver=saver
            else:
                raise Exception('Saver should be callable')
        # kwargs
        self.kwargs_gen=kwargs_gen
        self.kwargs_s=kwargs_s
        self.kwargs_r=kwargs_r

    def eval(self, X):
        '''
        evaluate the cost function at a position X

        Parameters:
        -----------
        X : array-like
            Input vector, should be at least iterable, idealy np.array
        '''
        cost = np.inf
        # if a filter is defined, apply it to the input vector before waveform generation
        if self.filter is not None:
            try:
                X = self.filter(X)
            except:
                raise Exception('Fail to filter input vector with '+self.filter.__name__)
        # generate the waveform
        try:
            waveform = self.generator(X)
        except:
            raise Exception('Fail to generate the waveform with '+self.generator.__name__)
        # compute the cost
        try:
            cost = self.residual(waveform)
        except:
            raise Exception('Fail to compute the cost with '+self.residual.__name__)
        # save the input vector and cost if requested
        if self.saver is not None:
            try:
                data = {'position':position, 'waveform':waveform, 'results':results, 'cost':cost}
                self.saver(data, file_name=file_name)
            except:
                raise Exception('Fail to save with '+self.saver.__name__)
        # return the cost
        return cost

    def get_fun(self):
        return self.eval


