import serial
import os,sys
from thorlabs_apt_comm import Thorlabs_apt_communication

"""
Module containing a class to talk to devices throught the thorlabs_apt_comm module
"""


ERROR = 4
WARN  = 3
DEBUG = 2
INFO  = 1
NONE  = 0

LOG_LEVEL=DEBUG

# parameters for the various stages obtained throught the first two digit of the serial number
# according to the doc





# utility functions
def log(level,msg):

    if level <= LOG_LEVEL:
        print(msg)


# --
class Thorlabs_device():
    controllers = { "BSC10x" : {"type":0, "has_channels":True},
                    "BSC20x" : {"type":1, "has_channels":True},
                    "LTS300" : {"type":0, "has_channels":False},
                    "HSLTS300" : {"type":0, "has_channels":False},
                }
    stages = [None,"LTS300","DRV014"]

    serial_num_to_device =  {
        20 : {
            "type": "Legacy single channel stepper driver",
            "code": "BSC001",
        },
        30 : {
            "type": "Legacy dual channel stepper driver",
            "code": "BSC002",
        },
        45:{
            "type": "LTS series",
            "code": "LTS150/LTS300",
        },
    }
    
    def __init__(self,controller,stage,serial_number,chan=None,port=None,baudrate=115200,timeout=10,write=None,read=None):
        # if we don't supply write or read command we fallback on serial
        
        if write == None or read == None:
            # initialize the communication to the write and read commands
            if not port:
                port = self.find_dev(serial_number)
            if port == None:
                print("No port found for serial_number %s !!\nABORTING " % serial_number)
                sys.exit(0)

            thor_dev = serial.Serial(port,baudrate=baudrate,timeout=timeout)

            if not write:
                self.write = thor_dev.write
            if not read:
                self.read =  thor_dev.read
        elif write and read:
            self.write=write
            self.read=read
        else:
            print("""You should supply either:
\t - either BOTH Write and read functions
\t - a serial number or a port to use the serial module
You didn't and thus aborting
""")
            sys.exit(0)

        self.thor_msg = Thorlabs_apt_communication()
        device_id = int(str(serial_number)[0:2])
        if self.serial_num_to_device.get(device_id):
            print self.serial_num_to_device[device_id]["code"]
        

    def find_dev(self,sn):
        """
        very rough method to get the /dev/ attached to a serial_number
        """
            
        path = "/dev/serial/by-id"
        for r, d, f in os.walk(path):
            for i in f:
                if sn in i and os.path.islink(os.path.join(path,i)):
                    return os.path.realpath(os.path.join(path,i))
        return None


    def raw_read(self,length):
        return self.read(length)

    def raw_write(self,keyword,*args):
        need_read , msg = self.thor_msg.create_message(keyword,*args)
        self.write(msg)
        return need_read , msg

    def send_command(self,keyword,*args):
        """
        function to send the command with parameter and give back the result if any
        """
        msg_type, msg=self.thor_msg.create_message(keyword,*args)
        self.write(msg)
        log(DEBUG,"keyword %s with arg %s msg : %s" % (keyword,str(args),msg))
        # getting the response

        recv_msg=""
        if msg_type == "request":
            log(DEBUG,"expecting answer")
            return self.read_response()
        return "None"

    def read_response(self):
        # first we read the header
        raw_recv_msg = self.read(6)
        length_to_read,keyword = self.thor_msg.read_header(raw_recv_msg)
        log(DEBUG,"first 6 bytes gives header %s and length %d" % (keyword,length_to_read))

        if length_to_read:
            log(DEBUG,"received extra characters")
            raw_recv_msg += self.read(length_to_read)

        recv_msg=self.thor_msg.read_message(keyword,raw_recv_msg)
        log(DEBUG,"full message including header : %s" % (recv_msg))
        return recv_msg
        
    # High Level function (user)

    def request_info(self,*args):
        log(INFO,"MGMSG_HW_REQ_INFO")
        log(INFO,self.send_command("MGMSG_HW_REQ_INFO",*args))

    def get_parameters(self,*args):
        params = ["MGMSG_MOT_REQ_VELPARAMS",
                  "MGMSG_MOT_REQ_JOGPARAMS",
                  "MGMSG_MOT_REQ_GENMOVEPARAMS",
                  "MGMSG_MOT_REQ_MOVERELPARAMS",
                  "MGMSG_MOT_REQ_MOVEABSPARAMS",
                  "MGMSG_MOT_REQ_HOMEPARAMS"]
        for i in params:
            log(INFO,i)
            log(INFO,self.send_command(i,*args))




    def info(self):
        pass

    
    def home(self,*args):
        action="MGMSG_MOT_MOVE_HOME"
        log(INFO,action)
        log(INFO,self.send_command(action,*args))

    def get_status(self,*args):
        action="MGMSG_MOT_REQ_STATUSUPDATE"
        log(INFO,action)
        log(INFO,self.send_command(action,*args))
   
    def update_message(self,*args):
        action="MGMSG_HW_START_UPDATEMSGS"
        log(INFO,action)
        log(INFO,self.send_command(action,*args))

    def set_velocity(self,*args):
        pass

    def set_acceleration(self,*args):
        pass
    
    def move(self,*args):
        pass

    def get_pos(self):
        return 0.



if __name__=="__main__":
    SRC=0x01
    DST=0x50
    
    hslts300=Thorlabs_device("45897070")
    hslts300.request_info(0,0,DST,SRC)
    hslts300.get_parameters(0,0,DST,SRC)
    hslts300.update_message(0,0,DST,SRC)
    hslts300.get_status(0,0,DST,SRC)

    #serial_number = "45839057"
    lts300=Thorlabs_device("45839057")
    lts300.request_info(0,0,DST,SRC)
    lts300.get_parameters(0,0,DST,SRC)
    #lts300.update_message(0,0,DST,SRC)
    lts300.get_status(0,0,DST,SRC)


#    home(hslts300,0,0,DST,SRC)

#    print("MGMSG_MOT_REQ_POSCOUNTER")
#    print(hslts300.send_command("MGMSG_MOT_REQ_POSCOUNTER"            ,1,0,DST,SRC))

    #hslts300=Thorlab_device("45839057")
    #request_info(hslts300,0,0,DST,SRC)
    #get_parameters(hslts300,0,0,DST,SRC)
    #home(hslts300,0,0,DST,SRC)
    #print("MGMSG_MOT_REQ_POSCOUNTER")
    #print(hslts300.send_command("MGMSG_MOT_REQ_POSCOUNTER"            ,1,0,DST,SRC))


    #lts300=Thorlab_device("45839057")
    #print("MGMSG_HW_NO_FLASH_PROGRAMMING")
    #print(lts300.send_command("MGMSG_HW_NO_FLASH_PROGRAMMING",0,0,DST,SRC))
    #print("MGMSG_HW_STOP_UPDATEMSGS")
    #print(lts300.send_command("MGMSG_HW_STOP_UPDATEMSGS"     ,0,0,DST,SRC))
    #print("MGMSG_HW_REQ_INFO")
    #print(lts300.send_command("MGMSG_HW_REQ_INFO"            ,0,0,DST,SRC))
    #print("MGMSG_MOD_SET_CHANENABLESTATE")
    #print(lts300.send_command("MGMSG_MOD_SET_CHANENABLESTATE"            ,1,1,DST,SRC))
    #print("MGMSG_MOT_SET_LIMSWITCHPARAMS")
    #print(lts300.send_command("MGMSG_MOT_SET_LIMSWITCHPARAMS"            ,1,1,DST| 0x80,SRC,1,3,0,25600*300,0,3))
    #print("MGMSG_MOT_REQ_POSCOUNTER")
    #print(lts300.send_command("MGMSG_MOT_REQ_POSCOUNTER"            ,1,0,DST,SRC))


    #print("MGMSG_HW_NO_FLASH_PROGRAMMING")
    #print( hslts300.send_command("MGMSG_HW_NO_FLASH_PROGRAMMING",0,0,DST,SRC))
    #print("MGMSG_HW_STOP_UPDATEMSGS")
    #print(hslts300.send_command("MGMSG_HW_STOP_UPDATEMSGS"     ,0,0,DST,SRC))
    #print("MGMSG_HW_REQ_INFO")
    #print(hslts300.send_command("MGMSG_HW_REQ_INFO"            ,0,0,DST,SRC))
    #print("MGMSG_MOD_SET_CHANENABLESTATE")
    #print(hslts300.send_command("MGMSG_MOD_SET_CHANENABLESTATE"            ,
    #print("MGMSG_MOT_SET_LIMSWITCHPARAMS")
    #print(hslts300.send_command("MGMSG_MOT_SET_LIMSWITCHPARAMS"            ,1,1,DST| 0x80,SRC,1,3,0,25600*300,0,3))
    
    comment="""
    serial_number = "45839057"  # old
    HSLTS_port = find_dev(serial_number)
    print("talking to port %s" % HSLTS_port)
    if HSLTS_port == None:
        print("No port found for serial_number %s !!\nABORTING " % serial_number)
        sys.exit(0)


    # initialize the communication
    HSLTS = serial.Serial(HSLTS_port,baudrate=115200)                    


    # init configure sequence from cmd_th_apt
    pos_max=float(pos_max)
    pos_min=float(pos_min)
    if th_apt["chan"]!="undef":
    th_apt["chan_addr"]=0x20 + th_apt["chan"]
    th_apt["mb_addr"]=0x11
    else:
    th_apt["chan_addr"]=0x50
    th_apt["mb_addr"]=0x50
    retcode,res=self.send_message(th_apt,"MGMSG_HW_NO_FLASH_PROGRAMMING",th_apt["mb_addr"],param1=0,param2=0)
    retcode,res=self.send_message(th_apt,"MGMSG_HW_STOP_UPDATEMSGS",th_apt["mb_addr"],param1=0,param2=0)
    retcode,res=self.send_message(th_apt,"MGMSG_HW_REQ_INFO",th_apt["mb_addr"],param1=0,param2=0)
    retcode,res=self.recv_message(th_apt)
    if retcode==0:
    raise self.th_apt_Exception((0,"Error getting hw info: %s" % (res)))
    message=res
    if self.code_cmds[self.cmd(message)]!="MGMSG_HW_GET_INFO":
    raise self.th_apt_Exception((0,"Error checking hw info: wrong message received"))
    if decode_word(message[176:180])>1:
    if th_apt["chan"]=="undef":
    raise self.th_apt_Exception((0,"Channel is needed for this controller"))
    # Check if bay is used
    retcode,res=self.send_message(th_apt,"MGMSG_RACK_REQ_BAYUSED",th_apt["mb_addr"],param1=th_apt["chan"]-1,param2=0)
    if retcode==0:
    raise self.th_apt_Exception((0,"Error sending check of chan: %s" % (res)))
    retcode,res=self.recv_message(th_apt)
    if retcode==0:
    raise self.th_apt_Exception((0,"Error getting check of chan: %s" % (res)))
    message=res
    if self.code_cmds[self.cmd(message)]!="MGMSG_RACK_GET_BAYUSED" or self.param1(message)!=th_apt["chan"]-1:
    raise self.th_apt_Exception((0,"Error checking chan: wrong message received"))
    if self.param2(message)!=0x01:
    raise self.th_apt_Exception((0,"Bay not connected in controller"))
    else:
    if th_apt["chan"]!="undef":
    raise self.th_apt_Exception((0,"Only one channel on this controller"))
    # Enable channel
    retcode,res=self.send_message(th_apt,"MGMSG_MOD_SET_CHANENABLESTATE",th_apt["chan_addr"],param1=1,param2=1)
if retcode==0:
                raise self.th_apt_Exception((0,"Error enabling channel: %s" % (res)))
# Set axis scaling parameters
    if th_apt["model"]=="BSC2_LNR50":
    th_apt.update(self.BSC2_DRV014)
            elif th_apt["model"]=="LTS300":
    th_apt.update(self.BSC_DRV014)
else:
    raise self.th_apt_Exception((0,"Unknown model %s. Please, contact the developers to implement support."%(th_apt["model"])))
    # Limits for 32b fields
    th_apt["p_lim"]=float(2147483648)/th_apt["usteps_per_mm_p"]
    th_apt["v_lim"]=float(2147483648)/th_apt["usteps_per_mm_v"]
    th_apt["a_lim"]=float(2147483648)/th_apt["usteps_per_mm_a"]
    print("Maximum protocol velocity: {0:.1f} mm/s".format(th_apt["v_lim"]))
    print("Maximum protocol acceleration: {0:.1f} mm/s**2".format(th_apt["a_lim"]))
    # Set axis limits
    data= "0100"
    data += th_apt["limitswitch"]*2
    data += encode_long(int(round(th_apt["usteps_per_mm_p"]*pos_max)))
    data += encode_long(int(round(th_apt["usteps_per_mm_p"]*pos_min)))
    data += "0300"
    retcode,res=self.send_message(th_apt,"MGMSG_MOT_SET_LIMSWITCHPARAMS",th_apt["chan_addr"],data=data)
    if retcode==0:
    raise self.th_apt_Exception((0,"Error setting limits on axis: %s" % (res)))
    th_apt["pos_max"]=pos_max
    th_apt["pos_min"]=pos_min
    # Get status update message (at least it lights up the channel LED)
    res=self.get_statusupdate(th_apt)
    except self.th_apt_Exception as e:
    _,_=submod_execcmd("inval@"+th_apt["bus"],th_apt["bus_id"])
    return e[0]
    th_apt["configured"]=True
    return 1,"ok"
    """



    # sending the message and getting the message if any
#    print("MGMSG_MOD_IDENTIFY :  %s " % send_command("MGMSG_MOD_IDENTIFY",1,0,0x1,0x50))
#    print("MGMSG_HW_REQ_INFO :  %s " % send_command("MGMSG_HW_REQ_INFO",0,0,0x1,0x50))
#    #print("MGMSG_HW_GET_INFO :  %s " % send_command("MGMSG_HW_GET_INFO",1,0,0x1,0x50))

    #print("MGMSG_MOT_REQ_LIMSWITCHPARAMS : %s " % send_command("MGMSG_MOT_REQ_LIMSWITCHPARAMS",1,0,0x1,0x50))
    #print("MGMSG_MOT_GET_LIMSWITCHPARAMS :  %s " % send_command("MGMSG_MOT_GET_LIMSWITCHPARAMS",1,0,0x1,0x50))
    #print("MGMSG_MOT_SET_LIMSWITCHPARAMS :  %s " % send_command("MGMSG_MOT_SET_LIMSWITCHPARAMS",16,0,0x1 | 0x80,0x50,1,2,2,49152,18,1))
    
    #print("MGMSG_MOT_REQ_LIMSWITCHPARAMS :  %s " % send_command("MGMSG_MOT_REQ_LIMSWITCHPARAMS",1,0,0x1,0x50))
    #print("MGMSG_MOT_GET_LIMSWITCHPARAMS :  %s " % send_command("MGMSG_MOT_GET_LIMSWITCHPARAMS",1,0,0x1,0x50))

