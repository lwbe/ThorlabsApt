#import usb.core
import struct
import IPython

cmds_code={         
    "MGMSG_HW_NO_FLASH_PROGRAMMING": 0x0018,         
    "MGMSG_HW_STOP_UPDATEMSGS": 0x0012,         
    "MGMSG_HW_REQ_INFO": 0x0005,         
    "MGMSG_HW_GET_INFO": 0x0006,         
    "MGMSG_RACK_REQ_BAYUSED": 0x0060,         
    "MGMSG_RACK_GET_BAYUSED": 0x0061,         
    "MGMSG_MOD_SET_CHANENABLESTATE": 0x0210,         
    "MGMSG_MOT_SET_LIMSWITCHPARAMS": 0x0423,         
    "MGMSG_MOT_REQ_STATUSUPDATE": 0x0480,         
    "MGMSG_MOT_GET_STATUSUPDATE": 0x0481,         
    "MGMSG_MOT_SET_HOMEPARAMS": 0x0440,         
    "MGMSG_MOT_MOVE_HOME": 0x0443,         
    "MGMSG_MOT_MOVE_HOMED": 0x0444,         
    "MGMSG_MOT_MOVE_RELATIVE": 0x0448,         
    "MGMSG_MOT_MOVE_COMPLETED": 0x0464,         
    "MGMSG_MOT_MOVE_STOPPED": 0x0466,         
    "MGMSG_MOT_SET_VELPARAMS": 0x0413,         
    "MGMSG_MOT_SET_POSCOUNTER": 0x0410,         
    "MGMSG_MOT_REQ_POSCOUNTER": 0x0411,         
    "MGMSG_MOT_GET_POSCOUNTER": 0x0412,         
    "MGMSG_HW_RESPONSE": 0x0080,         
}

code_cmds=dict((v,k) for k, v in cmds_code.items())


def decode_string(string):     
    return string.decode("hex") 

def encode_string(string):     
    return string.encode("hex") 
    
def decode_byte(string): 
    # unsigned 8 bits     
    return struct.unpack("<B",string.decode("hex"))[0] 
def encode_byte(integer): 
    # unsigned 8 bits     
    return struct.pack("<B",integer) 
    #return struct.pack("<B",integer).encode("hex") 

def decode_word(string): 
    # unsigned 16 bits     
    return struct.unpack("<H",string.decode("hex"))[0] 

def encode_word(integer): # unsigned 16 bits     
    #return struct.pack("<H",integer).encode("hex") 
    return struct.pack("<H",integer)

def decode_short(string): 
    # signed 16 bits     
    return struct.unpack("<h",string.decode("hex"))[0] 

def decode_dword(string): # unsigned 32 bits     
    return struct.unpack("<I",string.decode("hex"))[0] 

def decode_long(string): # signed 32 bits     
    return struct.unpack("<i",string.decode("hex"))[0] 

def encode_long(integer): 
    # signed 32 bits     
    #return struct.pack("<i",integer).encode("hex")
    return struct.pack("<i",integer)


def create_message(cmd,destination,param1=None,param2=None,data=None):         
    """
    Compose a message for the TH_APT controller. *cmd* is a string starting with \"MGMSG\". *destination* is an 8-bit integer. 
    Either *param1* and *param2, or *data* must be provided. *param1* and *param2* are 8-bit integers. *data* is string of variable length up to 255 bytes.
    """         
    message= encode_word(cmds_code[cmd]) 
    # cmd code         
    if param1!=None or param2!=None:             
        if param1==None or param2==None:                 
            return 0,"Both param1 and param2 must be provided to send_message"
        message += encode_byte(param1)      # param1             
        message += encode_byte(param2)      # param2             
        message += encode_byte(destination) # destination             
        message +=  encode_byte(1)                     # source         
    elif data!=None:             
        if len(data)>255:                 
            return 0,"Data is too long at %d bytes. Maximum is 255"%(len(data))             
        if len(data)%2!=0:
            return 0,"Data length must be multiple of 2. Now it's %d"%(len(data))             
            message += encode_word(len(data)/2) # data length             
            message += encode_byte(0x80|destination) # destination             
            message += encode_byte("01") # source             
            message += data        
        else:             
            return 0,"Incorrect number of parameters for compose"
            #retcode,res=submod_execcmd("write_bin@"+th_apt["bus"],th_apt["bus_id"],message)         
            #if retcode==0:             
            #    return 0,"Error writing <- %s" % (res)         
            #return 1,"ok"
    return message

def find_serial(sn):
    return usb.core.find(serial_number=sn)

def get_endpoint(sn):
    dev=find_serial(sn)
    configuration=dev.get_active_configuration()
    interface=configuration[(0,0)]  
    return interface[0]

IPython.embed()

# looking for serial number 45839057
#dev=find_serial("45839057")
#print(dev)
