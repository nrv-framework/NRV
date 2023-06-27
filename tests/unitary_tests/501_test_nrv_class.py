''' 
test to import all NRV2 librairies
'''
import nrv
import dolfinx



class NRV_subclass1(nrv.NRV_class):
    def __init__(self):
        """
        """
        super().__init__()
        self.type = "NRV_subclass1"
        self.x=1
        self.NRV_subclass2 = NRV_subclass2()




class NRV_subclass2(nrv.NRV_class):
    def __init__(self):
        """
        """
        super().__init__()
        self.type = "NRV_subclass2"
        self.x=2


    def __hash__(self):
        return 0



a = NRV_subclass1()
print(a.save())
print(a.type=='saved')

try:
    c = nrv.NRV_class()
    print(c)
except Exception as error:
    print("--------- THE FOLLOWING ERROR OCCURED ----------")
    print(error)

