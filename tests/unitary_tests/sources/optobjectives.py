import numpy as np

def Id(*args: float)-> float:
    return args

def rosenbock(*x: float)-> float:
    '''
    Multi-dimensional Rosenbock function
    '''
    result = 0
    for i in range(1, len(x)):
        result += 100*(x[i] - x[i-1]**2)**2 + (1-x[i-1])**2
    return result

def rastrigin(*x: float)-> float:
    '''
    Multi-dimensional Rastrigin function
    '''
    A = 10.
    n = len(x)
    result = A*n
    for xi in x:
        result += xi**2 - A*np.cos(2*np.pi*xi)
    return result

def sphere(*x: float)-> float:
    '''
    Multi-dimensional Sphere function
    '''
    result = 0
    for xi in x:
        result += xi**2
    return result

def ackley(x: float, y: float)-> float:
    '''
    Bi-dimensional Ackley function
    '''
    return -20*np.exp(-0.2*np.sqrt(0.5*(x**2+y**2))) \
        - np.exp(0.5*(np.cos(2*np.pi*x)+np.cos(2*np.pi*y))) \
        + np.e + 20

def beale(x: float, y: float)-> float:
    '''
    Bi-dimensional Beale function
    '''
    return (1.5 - x + x*y)**2\
        + (2.25 - x + x*y**2)**2\
        + (2.625 - x + x*y**3)**2

def goldstein_price(x: float, y: float)-> float:
    '''
    Bi-dimensional Goldstein function
    '''
    return (1 + (x + y + 1)**2 * (19 - 14*x + 3*x**2 - 14*y + 6*x*y + 3*y**2))\
        * (30 + (2*x - 3*y)**2 *(18 - 32*x + 12*x**2 + 48*y - 36*x*y + 27*y**2))

def booth(x: float, y: float)-> float:
    '''
    Bi-dimensional Booth function
    '''
    return (x + 2*y - 7)**2 + (2*x + y - 5)**2

def bukin6(x: float, y: float)-> float:
    '''
    Bi-dimensional Booth function
    '''
    return 100*np.sqrt(np.abs(y - 0.01*x**2)) + 0.01*np.abs(x+10)

