"""
simple code to show how to use the library

"""
from thorlabs_device import Thorlabs_device
import pprint

d1 = Thorlabs_device("40828799","BSC10x","17DRV014 Enc LNR 50mm",1)
pprint.pprint(d1.get_info())



