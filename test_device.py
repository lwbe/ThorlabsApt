"""
simple code to show how to use the library

"""
from thorlabs_device import Thorlabs_device
from thorlabs_apt_comm import Thorlabs_apt_communication
import serial
import os,sys

serial_device = serial.Serial(port,baudrate=baudrate,timeout=timeout)

tac = Thorlabs_apt_communication()
thor_dev = {}


def send_command(serial_device,tac,data=None):
    #write the message to send according to the apt protocol, data
    pass
    

def read_response(serial_device,tac):
    # read the header

    # read the rest if any

    return None


def info(t_id):
    d = thor_dev[i_d]
    send_command(d['serial_device'],"MGMSG_HW_REQ_INFO",d['header_params'])
    return read_response(d['serial_device'])



td= Thorlabs_device("LTS300",None,"45839057")
thor_dev['lts300'] = {
    'serial_device' : td.find_dev(),
    'header_params' : td.get_header(),
    'conversion' : td.conversion(),
}

td= Thorlabs_device("BSC10x","DRV014","40828799")
thor_dev['bsc10x_drv014'] = {
    'serial_device' : td.find_dev(),
    'header_params' : td.get_header(),
    'conversion' : td.conversion(),
}

print info('lts300')
print info('bsc10x_drv014')

home('lts300')
home('bsc10x_drv014')

get_pos('lts300')
get_pos('bsc10x_drv014')

set_move_params('lts300')
set_move_params('bsc10x_drv014')

move('lts300')
move('bsc10x_drv014')

get_pos('lts300')
get_pos('bsc10x_drv014')


