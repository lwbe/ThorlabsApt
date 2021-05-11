"""
simple code to show how to use the library

"""
from thorlabs_device import Thorlabs_device
import pprint

d1 = Thorlabs_device("40828799","BSC10x","17DRV014 Enc LNR 50mm",1)
d1.configure()
pprint.pprint(d1.get_info())


d2 = Thorlabs_device("45839057","LTS300","LTS300 300mm Stage",1) 

d3 = Thorlabs_device("45897070","HS LTS300","HS LTS300 300mm Stage",1) 
