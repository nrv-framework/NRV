import nrv

@nrv.singlecore
def test(a, b):
    nrv.MCH.say_hello()
    print('computing ', a, ' + ', b, ' = ',a+b)
    return None

if __name__ == "__main__":
    test(2, 3)