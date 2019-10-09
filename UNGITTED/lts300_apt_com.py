

import thorlabs_device
import pprint


pp=pprint.PrettyPrinter(indent=4)

def set_device(ident):
    if ident=="LTS300":
        device=thorlabs_device.Thorlabs_device("LTS300",None,"45839057")
        
        device.destination=0x50
        device.dest_mbr=0x50
        device.channel=1
        device.source=1
        device.ustep_pos=25600
        device.ustep_vel=25600
        device.ustep_acc=25600
        device.CW_hard_lim=2
        device.CCW_hard_lim=2
        device.limit_mode=2
        device.pos_max=300
        device.pos_min=0
    elif ident=="BSC10x":
        device=thorlabs_device.Thorlabs_device("40828799","BSC10x","17DRV014 Enc LNR 50mm",1)
        device.destination=0x21
        device.dest_mbr=0x11
        device.channel=1
        device.source=1
        device.ustep_pos=25600
        device.ustep_vel=25600
        device.ustep_acc=25600
        device.CW_hard_lim=3
        device.CCW_hard_lim=3
        device.limit_mode=1
        device.pos_max=50
        device.pos_min=0
    elif ident=="BSC20x":
        device=thorlabs_device.Thorlabs_device("BSC20x","DRV14","70854298",1)
        device.destination=0x21
        device.dest_mbr=0x11
        device.channel=1
        device.source=1
        device.ustep_pos=409600
        device.ustep_vel=21987328
        device.ustep_acc=4506
        device.CW_hard_lim=3
        device.CCW_hard_lim=3
        device.limit_mode=3
        device.pos_max=50
        device.pos_min=0
    else: 
        print "nothing to set!!!"

    return device

def no_flash_programming(device):
    device.send_command("MGMSG_HW_NO_FLASH_PROGRAMMING",0,0,device.dest_mbr,device.source)

def stop_update_msg(device):
    device.send_command("MGMSG_HW_STOP_UPDATEMSGS",device.channel,1,device.destination,device.source)

def get_status_update(device):
    return device.send_command("MGMSG_MOT_REQ_STATUSUPDATE",device.channel,1,device.destination,device.source)


def enable(device):
    d = device.send_command(u'MGMSG_MOD_SET_CHANENABLESTATE',device.channel,1,device.destination,device.source)

def get_pos(device):
    d = device.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',device.channel,0,device.destination,device.source)
    return 1.*d["Position"]/device.ustep_pos

def home(device):
    device.send_command("MGMSG_MOT_MOVE_HOME",device.channel,0,device.destination,device.source)

def get_home_params(device):
    return device.send_command("MGMSG_MOT_REQ_HOMEPARAMS",device.channel,0,device.destination,device.source)

def set_home_params(device,vel):
    device.send_command("MGMSG_MOT_SET_HOMEPARAMS",0,device.destination,device.source,1,2,1,device.ustep_vel*vel,0xa)

def set_velocity_params(device,vel,acc):
    device.send_command("MGMSG_MOT_SET_VELPARAMS",0,device.destination,device.source,1,0,device.ustep_acc*acc,device.ustep_vel*vel)

def get_velocity_params(device):
    return device.send_command("MGMSG_MOT_REQ_VELPARAMS",device.channel,0,device.destination,device.source)

def set_limitswitch_params(device):
    device.send_command("MGMSG_MOT_SET_LIMSWITCHPARAMS",
                        0,
                        device.destination,
                        device.channel,
                        1,
                        device.CW_hard_lim,
                        device.CCW_hard_lim,
                        device.pos_max*device.ustep_pos,
                        device.pos_min*device.ustep_pos,
                        device.limit_mode)
    
def get_limitswitch_params(device):
    return device.send_command("MGMSG_MOT_REQ_LIMSWITCHPARAMS",device.channel,0,device.destination,device.source)
    
def move_rel(device,distance):
    device.send_command("MGMSG_MOT_MOVE_RELATIVE",0,device.destination,device.source,1,int(distance*device.ustep_pos))
    
    
def read_until_completed(device):
    completed_keys=[]
    for i in ["COMPLETED","STOPPED","HOMED"]:
        completed_keys.append(device.thor_msg.tac_data["MGMSG_MOT_MOVE_"+i]["msg_id"])
    msg_id=""
    while msg_id not in completed_keys:
        d = device.send_command("MGMSG_MOT_REQ_STATUSUPDATE",device.channel,0,device.destination,device.source)
        msg_id=d["msg_id"]
        print d["Position"]/device.ustep_pos
    return msg_id

def get_info(device):
    return device.send_command("MGMSG_HW_REQ_INFO",0,0,device.dest_mbr,device.source)

def bay_used(device):
    return  device.send_command("MGMSG_RACK_REQ_BAYUSED",0,0,device.dest_mbr,device.source)               



def initialize_device(device):
    no_flash_programming(device)
    stop_update_msg(device)
    get_info(device)
    #bay_used(device)
    enable(device)
    #set_limitswitch_params(device)
    get_status_update(device)
    set_velocity_params(device,1,1)

comment="""


from lts300_apt_com import *

# needed steps
no_flash_programming(device2)
stop_update_msg(device2)
#device.send_command("MGMSG_HW_STOP_UPDATEMSGS",device.channel,1,device.destination,device.source)
device2.send_command("MGMSG_HW_REQ_INFO",0,0,device2.dest_mbr,device2.source)
device.send_command("MGMSG_RACK_REQ_BAYUSED",1,0,0x11,1)               
enable(device2)
device2.send_command("MGMSG_MOT_SET_LIMSWITCHPARAMS",0,0,0x21,1,1,3,3,50*device2.ustep_pos,0,3)
get_pos(device2)
# end of initialisation


set_velocity_params(device2,1,1)




move_rel(device2,1)


get_status_update(device2)

set_velocity_params(device2,0.1,10)
device2.send_command("MGMSG_MOT_SET_LIMSWITCHPARAMS",0,0,0x21,1,1,3,3,50*device2.ustep_pos,0,3)


home(device2)
get_pos(device2)
move_rel(device2,10)
set_velocity_params(device2,1,1)
move_rel(device2,10)
move_rel(device2,-10)
get_status_update(device2)
get_limitswitch_params(device2)
get_status_update(device2)
home(device2)
set_home_params(device2,1)
device.send_command("MGMSG_MOT_REQ_HOMEPARAMS",0,0,0x50,1)
device.send_command("MGMSG_MOT_REQ_HOMEPARAMS",0,0,0x21,1)
device.send_command("MGMSG_MOT_REQ_HOMEPARAMS",1,0,0x21,1)
device.send_command("MGMSG_RACK_REQ_BAYUSED",1,0,0x11,1)
history

get_limitswitch_params(device2)
msg sent: $! (0x24 04 01 00 21 01)
Out[3]: 
{u'CCW_hardlimit': 3,
 u'CCW_softlimit': 0,
 u'CW_hardlimit': 3,
 u'CW_softlimit': 20480000,
 u'Limit_mode': 3,
 u'chan_id': 1,
 u'dest': 129,
 u'msg_id': 1061,
 u'param1': 16,
 u'param2': 0,
 u'source': 33}


get_velocity_params(device2)
msg sent: ! (0x14 04 01 00 21 01)
Out[4]: 
{u'Accel': 4506,
 u'Chan_id': 1,
 u'Max_velocity': 21987328,
 u'Min_velocity': 0,
 u'dest': 129,
 u'msg_id': 1045,
 u'param1': 14,
 u'param2': 0,
 u'source': 33}

device2.send_command("MGMSG_MOT_REQ_HOMEPARAMS",device2.channel,0,device2.destination,device2.source)
msg sent: A! (0x41 04 01 00 21 01)
Out[5]: 
{u'Chan_id': 1,
 u'Home_Velocity': 0,
 u'Home_direction': 2,
 u'Limit_switch': 1,
 u'Offset_distance': 12800,
 u'dest': 129,
 u'msg_id': 1090,
 u'param1': 14,
 u'param2': 0,
 u'source': 33}



"""

# stop_update_msg(device2)

comment="""
# get info
print("MGMSG_HW_REQ_INFO")
pp.pprint(a.send_command("MGMSG_HW_REQ_INFO",0,0,0x50,1))

print(50*"-"+"\nMGMSG_MOD_REQ_CHANENABLESTATE")
pp.pprint(a.send_command("MGMSG_MOD_REQ_CHANENABLESTATE",0,0,0x50,1))

print(50*"-"+"\nMGMSG_MOT_REQ_VELPARAMS")
pp.pprint(a.send_command("MGMSG_MOT_REQ_VELPARAMS",0,0,0x50,1))

print(50*"-"+"\nMGMSG_MOT_REQ_JOGPARAMS")
pp.pprint(a.send_command("MGMSG_MOT_REQ_JOGPARAMS",0,0,0x50,1))

print(50*"-"+"\nMGMSG_MOT_REQ_GENMOVEPARAMS")
pp.pprint(a.send_command("MGMSG_MOT_REQ_GENMOVEPARAMS",0,0,0x50,1))

print(50*"-"+"\nMGMSG_MOT_REQ_MOVERELPARAMS")
pp.pprint(a.send_command("MGMSG_MOT_REQ_MOVERELPARAMS",0,0,0x50,1))

print(50*"-"+"\nMGMSG_MOT_REQ_MOVEABSPARAMS")
pp.pprint(a.send_command("MGMSG_MOT_REQ_MOVEABSPARAMS",0,0,0x50,1))

print(50*"-"+"\nMGMSG_MOT_REQ_HOMEPARAMS")
pp.pprint(a.send_command("MGMSG_MOT_REQ_HOMEPARAMS",0,0,0x50,1))

print(50*"-"+"\nMGMSG_MOT_REQ_LIMSWITHPARAMS")
pp.pprint(a.send_command("MGMSG_MOT_REQ_LIMSWITCHPARAMS",0,0,0x50,1))

print(50*"=")


# set parameters
print("MGMSG_MOT_SET_HOMEPARAMS")
pp.pprint(a.send_command("MGMSG_MOT_SET_HOMEPARAMS",0,0,0x50,1,1,2,1,25600/10,int(1.6*25600)))
print("--> MGMSG_MOT_REQ_HOMEPARAMS")
pp.pprint(a.send_command("MGMSG_MOT_REQ_HOMEPARAMS",0,0,0x50,1))
print(50*"-")
# get position
print("Getting position")
pp.pprint(a.send_command("MGMSG_MOT_REQ_POSCOUNTER",0,0,0x50,1))

print("MGMSG_MOT_SET_VELPARAMS")

a.send_command("MGMSG_MOT_SET_VELPARAMS",0,0,0x50,1,1,0,25600*5,25600*4)



# home 
a.send_command("MGMSG_HW_START_UPDATEMSGS",0,0,0x50,1)

print("start homing")
a.send_command("MGMSG_MOT_MOVE_HOME",0,0,0x50,1)

print("reading ouptut")
pprint(a.read_response())
pprint(a.read_response())
pprint(a.read_response())
pprint(a.read_response())

a.send_command("MGMSG_HW_STOP_UPDATEMSGS",0,0,0x50,1)

# get position
pp.pprint(a.send_command("MGMSG_MOT_REQ_POSCOUNTER",0,0,0x50,1))

# move slowly

# follow the move

# home

 # move slowly

# follow the move version 2



a.send_command("MGMSG_MOT_REQ_POSCOUNTER",1,0,0x50,1)


a.send_command("MGMSG_MOT_SET_MOVERELPARAMS",1,0,0x50,1,1,10*25600)
a.send_command("MGMSG_MOT_MOVE_VELOCITY",1,0x01,0x50,1)
a.send_command("MGMSG_MOT_MOVE_STOP",1,0x01,0x50,1,1)

a.send_command("MGMSG_MOT_SET_LIMSWITCHPARAMS",0,0,0x50,1,1,2,2,7680000,0,3)

pp.pprint(a.send_command("MGMSG_MOT_REQ_POSCOUNTER",0,0,0x50,1))


















a.send_command("MGMSG_MOT_GET_LIMSWITCHPARAMS",0,0,0x50,1)
a.send_command("MGMSG_MOT_REQ_LIMSWITCHPARAMS",0,0,0x50,1)
a.send_command("MGMSG_MOT_REQ_LIMSWITCHPARAMS",0,0,0x50,1)
a.send_command("MGMSG_MOT_REQ_POSCOUNTER",0,0,0x50,1)
a.send_command("MGMSG_MOT_REQ_POSCOUNTER",0,0,0x50,1)
a=thorlabs_device.Thorlabs_device("LTS300",None,"45839057")
a.send_command("MGMSG_MOT_REQ_POSCOUNTER",0,0,0x50,1)
a.send_command("MGMSG_MOT_REQ_POSCOUNTER",1,0,0x50,1)
a.send_command("MGMSG_MOT_SET_POSCOUNTER",1,0,0x50,1,1,100000)
a.send_command("MGMSG_MOT_SET_POSCOUNTER",1,0,0x50,1,1,2560000)
a.send_command("MGMSG_MOT_REQ_VELPARAMS",1,0,0x50)
a.send_command("MGMSG_MOT_REQ_VELPARAMS",1,0,0x50,1)
a.send_command("MGMSG_MOT_MOVE_RELATIVE",1,0,0x50,1,10000)
a.send_command("MGMSG_MOT_MOVE_RELATIVE",1,0,0x50,1,1,10000)
a.send_command("MGMSG_MOT_REQ_POSCOUNTER",1,0,0x50,1)
a.send_command("MGMSG_MOT_MOVE_RELATIVE",1,0,0x50,1,1,1000000)
2147483648/25600.
a.send_command("MGMSG_MOT_SET_LIMSWITCHPARAMS",0,0,0x50,1)
a.send_command("MGMSG_MOT_REQ_LIMSWITCHPARAMS",0,0,0x50,1)
a.send_command("MGMSG_MOT_REQ_LIMSWITCHPARAMS",0,0,0x50,1)
a.send_command("MGMSG_MOT_REQ_LIMSWITCHPARAMS",0,0,0x50,1)
a.send_command("MGMSG_MOT_REQ_LIMSWITCHPARAMS",0,0,0x50,1)
a.send_command("MGMSG_MOT_MOVE_RELATIVE",1,0,0x50,1,1,10000)
a.send_command("MGMSG_MOT_MOVE_RELATIVE",1,0,0x50,1,1,100000)
a.read_response()
a.read_response()
a.read_response()
a.read_response()
a.read_response()
a.read_response()
a.read_response()
a.read_response()
a.read_response()
a.read_response()
a.read_response()
a.read_response()
a.read(6)
a.send_command("MGMSG_MOT_MOVE_RELATIVE",1,0,0x50,1,1,-1000000)
a.read(6)
a.read_response()
a.read_response()
a.read_response()
a.send_command("MGMSG_MOT_MOVE_RELATIVE",1,0,0x50,1,1,1000000)
a.read_response()
a.send_command("MGMSG_HW_STOP_UPDATEMSGS",0,0,0x50,1)
a.send_command("MGMSG_MOT_MOVE_RELATIVE",1,0,0x50,1,1,-1000000)
a.read_response()









BSC10x stuff


read_until_completed(device)
hex(1124)
device2=thorlabs_device.Thorlabs_device("LTS300",None,"40828799")
home(device2)
device2.send_command("MGMSG_HW_REQ_INFO",0,0,0x50,1)
device2.send_command("MGMSG_MOD_IDENTIFY",0,0,0x21,1)
device2.send_command("MGMSG_RACK_BAYUSED",0,0,0x21,1)
device2.send_command("MGMSG_REQ_VEL_PARAMS",0,0,0x21,1)
device2.send_command("MGMSG_REQ_VELPARAMS",0,0,0x21,1)
device2.send_command("MGMSG_MOT_REQ_VELPARAMS",0,0,0x21,1)
device2.send_command("MGMSG_MOT_SET_VELPARAMS",0,0,0x21,1,1,0,25600*5,25600*4)
device2.send_command("MGMSG_MOT_REQ_VELPARAMS",0,0,0x21,1)
a.send_command("MGMSG_MOT_SET_LIMSWITCHPARAMS",0,0,0x50,1,1,2,2,7680000,0,3)
7680000/25600.
device2.send_command("MGMSG_MOT_SET_LIMSWITCHPARAMS",0,0,0x50,1,1,2,2,50*25600,0,3)
device2.send_command("MGMSG_MOT_MOVE_HOME",1,0,0x21,1)
device2.send_command("MGMSG_MOD_REQ_CHANENABLESTATE",0,0,0x21,1)
device2.send_command("MGMSG_MOD_SET_CHANENABLESTATE",1,1,0x21,1)
device2.send_command("MGMSG_MOT_MOVE_HOME",1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
50*25600
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command("MGMSG_MOT_REQ_HOMEPARAMS",1,0,0x21,1)
device2.send_command("MGMSG_MOT_SET_HOMEPARAMS",1,0,0x21,1,1,2,1,25600,12800)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command("MGMSG_MOT_REQ_VELPARAMS",1,0,0x21,1)
device2.send_command("MGMSG_MOT_MOVE_RELATIVE",1,0,0x21,1,1,int(20*25600))
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command("MGMSG_MOT_REQ_MOVEVELPARAMS",1,0,0x21,1)
device2.send_command("MGMSG_MOT_REQ_MOVERELPARAMS",1,0,0x21,1)
device2.send_command("MGMSG_MOT_REQ_VELPARAMS",1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command("MGMSG_MOT_REQ_VELPARAMS",1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x21,1)
device2.read(100)
history


"""
