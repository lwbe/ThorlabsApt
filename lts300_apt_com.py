

import thorlabs_device
import pprint


pp=pprint.PrettyPrinter(indent=4)
device=thorlabs_device.Thorlabs_device("LTS300",None,"45839057")


def get_pos(device):
    d = device.send_command(u'MGMSG_MOT_REQ_POSCOUNTER',1,0,0x50,1)
    return d["Position"]/25600.

def home(device):
    device.send_command("MGMSG_MOT_MOVE_HOME",1,0,0x50,1)       

def move_rel(device,distance):
    device.send_command("MGMSG_MOT_MOVE_RELATIVE",1,0,0x50,1,1,int(distance*25600))
    
    
def read_until_completed(device):
    completed_keys=[]
    for i in ["COMPLETED","STOPPED","HOMED"]:
        completed_keys.append(device.thor_msg.tac_data["MGMSG_MOT_MOVE_"+i]["msg_id"])
    msg_id=""
    while msg_id not in completed_keys:
        d = device.send_command("MGMSG_MOT_REQ_STATUSUPDATE",1,0,0x50,1)
        msg_id=d["msg_id"]
    return msg_id

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
