import serial
import os,sys,time

# for python 2.7
import ConfigParser as configparser

stages_file="MG17APTServer.ini"
SERIAL_TIMEOUT=10
from thorlabs_apt_comm import Thorlabs_apt_communication



"""
Module containing a class to talk to devices throught the thorlabs_apt_comm module
"""

controllers = {
    "BSC10x": {
        "pos_factor": 128,
        "vel_factor": 128,
        "acc_factor": 128,
        "has_channel": True,
    },
    "LTS300": {
        "pos_factor": 128,
        "vel_factor": 128,
        "acc_factor": 128,
        "has_channel": False,
    },
    "BSC20x": {
        "pos_factor": 2048,
        "vel_factor": int(2048*54.68),
        "acc_factor": int(2048/90.9),
        "has_channel": True,
    },
    "HS LTS300": {
        "pos_factor": 2048,
        "vel_factor": int(2048*54.68),
        "acc_factor": int(2048/90.9),
        "has_channel": False,
    },
}


ERROR = 4
WARN  = 3
DEBUG = 2
INFO  = 1
NONE  = 0

LOG_LEVEL=INFO

# parameters for the various stages obtained throught the first two digit of the serial number
# according to the doc


# utility functions
def log(level,msg):

    if level <= LOG_LEVEL:
        print(msg)


# --
class Thorlabs_device():
    # loading configuration files
    stages_config=configparser.ConfigParser()
    stages_config.readfp(open(stages_file))

    controllers = controllers
    def __init__(self,
                 serial_number,
                 controller_name,
                 stage_name,
                 chan=None,
                 port=None,
                 baudrate=115200,
                 timeout=SERIAL_TIMEOUT,
                 write=None,
                 read=None):
        # if we don't supply write or read command we fallback on serial
        self.controller_name = controller_name
        self.stage_name = stage_name
        self.channel = chan
        self.thor_dev=None

        if write == None and read == None:
            # initialize the communication to the write and read commands
            if not port:
                port = self.find_dev(serial_number)
            if port == None:
                print("No port found for serial_number %s !!\nABORTING " % serial_number)
                sys.exit(0)

            self.thor_dev = serial.Serial(port,baudrate=baudrate,timeout=timeout)
            self.write = self.thor_dev.write
            self.read =  self.thor_dev.read
        else: 
            if write and read:
                self.write, self.read = write, read
            else:
                print("""You should supply either:
                \t - either BOTH Write and read functions
                \t - a serial number or a port to use the serial module
                You didn't and thus aborting
                """)
                sys.exit(0)

        # thorlabs communication protocal
        self.thor_msg = Thorlabs_apt_communication()
        # store the key indicating a end of motion
        self.completed_keys=[]
        for i in ["COMPLETED","STOPPED","HOMED"]:
            self.completed_keys.append(self.thor_msg.tac_data["MGMSG_MOT_MOVE_"+i]["msg_id"])

        self.set_controller_and_stage()
        # min and max position
        self.pos_min = self.stage["min pos"]
        self.pos_max = self.stage["max pos"]
        self.stop_update_msg()

# --
    def set_controller_and_stage(self):
        """
        set the controller and stage parameters according to configuration data and names
        """
        # stage
        if self.stage_name in self.stages_config.sections():
            self.stage = dict(self.stages_config.items(self.stage_name))
        else:
            print("stage %s is unknown !!! \nThe possible values are %s" % 
                  (self.stage_name,"\n".join(self.stages_config.sections()[1:])))
            sys.exit(0)

        # controller
        if self.controller_name in list(controllers):
            self.controller = self.controllers[self.controller_name]
        else:
            print("controller %s is unknown !!! \nThe possible values are %s" % (self.controller_name,"\n".join(list(self.controllers))))
            sys,exit(0)
            
        # the useful information to use the device
        # destination, channel, source
        if self.controller["has_channel"]:
            if self.channel:
                self.destination_controller = 0x11
                self.destination = self.destination_controller + self.channel + 15
            else:
                print("controller %s needs a channel !! ")
                sys.exit(0)
        else:
            self.destination = 0x50
            self.destination_controller = 0x50
            self.channel = 1
        self.source = 1

        # conversion parameter from counter to position, velocity, acceleration
        self.ustep_to_pos = int(self.controller['pos_factor']*float(self.stage["steps per rev"]))
        self.ustep_to_vel = int(self.controller['vel_factor']*float(self.stage["steps per rev"]))
        self.ustep_to_acc = int(self.controller['acc_factor']*float(self.stage["steps per rev"]))
        
        self.header={
            "destination":self.destination,
            "source":self.source,
        }
# --
    def configure(self):
        """
        configure the device
        """
        self.no_flash_programming()
        self.stop_update_msg()
        # flush the communication
        if self.thor_dev:
            self.thor_dev.timeout=1
            self.read(1000)
            self.thor_dev.timeout=SERIAL_TIMEOUT
        self.get_info()
        #self.bay_used()
        self.enable()
        self.set_limitswitchparams()

        #self.start_update_msg()
        self.get_status_update()
        #self.stop_update_msg()

        self.set_velparams()
        self.set_homeparams()
        self.set_powerparams()
#--
    def find_dev(self,sn):
        """
        very rough method to get the /dev/ attached to a serial_number
        """
            
        path = "/dev/serial/by-id"
        for r, d, f in os.walk(path):
            for i in f:
                if sn in i and os.path.islink(os.path.join(path,i)):
                    log(INFO,"Found device %s for serial number %s" %
                        (os.path.realpath(os.path.join(path,i)),sn))
                    
                    return os.path.realpath(os.path.join(path,i))
        return None
# --
# communication function with the device
# --
    def raw_read(self,length):
        return self.read(length)
# --
    def raw_write(self,keyword,*args):
        need_read , msg = self.thor_msg.create_message(keyword,*args)
        self.write(msg)
        return need_read , msg
# --
    def send_command(self,*args,**kwargs):
        """
        function to send the command with parameter and give back the result if any
        """
        msg_type, msg=self.thor_msg.create_message(*args,**kwargs)
        self.write(msg)
        log(DEBUG,"args %s or kwargs %s gives msg : %s" % (str(args),str(kwargs),msg))

        # getting the response
        recv_msg=""
        if msg_type == "request":
            log(DEBUG,"expecting answer")
            return self.read_response()
        return "None"

#-- 
    def read_response(self):
        # first we read the header
        raw_recv_msg = self.read(6)
        length_to_read,keyword = self.thor_msg.read_header(raw_recv_msg)
        log(DEBUG,"first 6 bytes gives header %s and length %d" % (keyword,length_to_read))

        if length_to_read:
            log(DEBUG,"received extra characters")
            raw_recv_msg += self.read(length_to_read)

        recv_msg=self.thor_msg.read_message(keyword,raw_recv_msg)

        if keyword=="MGMSG_HW_RESPONSE":
            return "error : reset the controller/stage"
        elif keyword== "MGMSG_HW_RICH_RESPONSE":
            return "error: reset the controller/stage %s " % str(revc_msg)

        log(DEBUG,"full message including header : %s" % (recv_msg))
        return recv_msg
# --
    def wait_until_completed(self):
        """
        This method check the statusbit and the position and ends when one of the completed movement 
        msgid is received of the stage indicates that it doesn't move forward or reverse. 
        """
        msg_id=""
        is_completed = False
        while not is_completed: # msg_id not in self.completed_keys:
            # we query the status bits
            d = self.get_statusbits()
            log(INFO, "get_statusbit return value (expected msgid=1066):  %s "%str(d))

            # some stage return a completed message when the stage arrived to the position
            # while some other don't.
            # first we check if we have a Status Bit entry 
            if d.get("Status Bits"):
                status_bits=self.extract_status_information(d["Status Bits"])
                log(INFO,"status bits (%d): %s" % ( d["Status Bits"],
                                                 str(status_bits))
                )

                # this indicates that the stage is not moving.
                if status_bits['moving forward'] == 0 and status_bits['moving reverse']== 0:
                    is_completed = True

            # we will look for the position of the stage
            msg_id = d["msg_id"]
            if msg_id not in self.completed_keys:
                                
                d = self.get_poscounter()
                log(INFO, "get_poscounter return value (expected msgid=1042):  %s "%str(d))
                if d.get("Position"):
                    print("Position %f mm" % (float(d["Position"])/(1.*self.ustep_to_pos)))
                msg_id=d["msg_id"]

            if msg_id in self.completed_keys:
                is_completed = True

            time.sleep(0.5)

        log(INFO,"movement is completed")
        
        #self.read_response() # to flush the msg queue

        return msg_id
        
    #def read_update_msg(self):
    #    self.start_update_msg()
    #    r=""
    #    while r != "q":
    #        print(self.read_response())
    #        self.read(6)  # flush something but what?
    #        r=raw_input()

    #    self.stop_update_msg()
        
# -- 
    def extract_status_information(self,s):
        return {
            "CW forward hw limit switch active"    : 1 if s & 0x00000001 else 0,
            "CCW reverse hw limit switch active"   : 1 if s & 0x00000002 else 0,
            "CW forward soft limit switch active"  : 1 if s & 0x00000004 else 0,
            "CCW reverse soft limit switch active" : 1 if s & 0x00000008 else 0,
            "moving forward"                       : 1 if s & 0x00000010 else 0,
            "moving reverse"                       : 1 if s & 0x00000020 else 0,
            "jogging forward"                      : 1 if s & 0x00000040 else 0,
            "jogging reverse"                      : 1 if s & 0x00000080 else 0,
            "homing"                               : 1 if s & 0x00000200 else 0,
            "homed"                                : 1 if s & 0x00000400 else 0,
        }
        
        

# low Level function (user)
# --  Decorator
    def send(func):
        def wrapper(self):
            p = func(self)
            log(INFO,"keyword %s params: %s" % (p[0],", ".join([str(i) for i in p[1:]])))
            return  self.send_command(*p)
        return wrapper

# --
    @send
    def mod_identify(self):
        return ("MGMSG_MOD_IDENTIFY",0,0,self.destination,self.source)
# --
    @send
    def no_flash_programming(self):
        return ("MGMSG_HW_NO_FLASH_PROGRAMMING",0,0,self.destination_controller,self.source)
# -- 
    @send
    def stop_update_msg(self):
        return ("MGMSG_HW_STOP_UPDATEMSGS",self.channel,0,self.destination_controller,self.source)
# --
    @send 
    def start_update_msg(self):
        return ("MGMSG_HW_START_UPDATEMSGS",self.channel,0,self.destination_controller,self.source)
# --
    @send
    def enable(self):
        return ("MGMSG_MOD_SET_CHANENABLESTATE",self.channel,1,self.destination,self.source)
# --
    @send
    def disable(self):
        return ("MGMSG_MOD_SET_CHANENABLESTATE",self.channel,2,self.destination,self.source)
# --
    @send
    def set_homeparams(self):
        return ("MGMSG_MOT_SET_HOMEPARAMS",0,self.destination,self.source,
                self.channel, 
                int(self.stage["home dir"]),
                int(self.stage["home limit switch"]),
                int(float(self.stage["home vel"])*self.ustep_to_vel),
                int(float(self.stage["home zero offset"])*self.ustep_to_pos))
# --
    @send
    def get_homeparams(self):
        return ("MGMSG_MOT_REQ_HOMEPARAMS",self.channel,0,self.destination,self.source)
# --
    @send
    def set_velparams(self):
        return ("MGMSG_MOT_SET_VELPARAMS",0,self.destination,self.source,
                self.channel,
                 0, #int(float(self.stage["def min vel"])*self.ustep_to_vel),
                int(0.5*float(self.stage["max accn"])*self.ustep_to_acc),
                int(0.5*float(self.stage["max vel"])*self.ustep_to_vel)
            )
# --
    @send
    def set_velparams_max(self):
        return ("MGMSG_MOT_SET_VELPARAMS",0,self.destination,self.source,
                self.channel,
                 0, #int(float(self.stage["def min vel"])*self.ustep_to_vel),
                int(float(self.stage["max accn"])*self.ustep_to_acc),
                int(float(self.stage["max vel"])*self.ustep_to_vel)
            )
# --
    @send
    def get_velparams(self):
        return ("MGMSG_MOT_REQ_VELPARAMS",self.channel,0,self.destination,self.source)
# --
    @send
    def set_limitswitchparams(self):
        return ("MGMSG_MOT_SET_LIMSWITCHPARAMS", 0, self.destination, self.source,
                self.channel,
                int(self.stage["cw hard limit"]),
                int(self.stage["ccw hard limit"]),
                int(float(self.stage["max pos"])*self.ustep_to_pos),
                int(float(self.stage["min pos"])*self.ustep_to_pos),
                int(self.stage["soft limit mode"]))
# --
    @send
    def get_limitswitchparams(self):
        return ("MGMSG_MOT_REQ_LIMSWITCHPARAMS", self.channel, 0, self.destination, self.source)
# --
    @send
    def set_powerparams(self):
        return ("MGMSG_MOT_SET_POWERPARAMS",0,self.destination,self.source,
                 self.channel,
                 int(self.stage["rest factor"]),
                 int(self.stage["move factor"]))
# --
    @send
    def get_powerparams(self):
        return ("MGMSG_MOT_REQ_POWERPARAMS",self.channel,0,self.destination,self.source)
# --
    @send
    def get_info(self):
        return ("MGMSG_HW_REQ_INFO",0,0,self.destination_controller,self.source)
# --
    @send
    def bay_used(self):
        return ("MGMSG_RACK_REQ_BAYUSED",self.channel,0,self.destination_controller,self.source)               
# --
    @send
    def get_status_update(self):
        return ("MGMSG_MOT_REQ_STATUSUPDATE",self.channel,0,self.destination,self.source)
# --
    @send
    def get_poscounter(self):
        return ("MGMSG_MOT_REQ_POSCOUNTER",self.channel,0,self.destination,self.source)
# --
    @send
    def get_statusbits(self):
        return ("MGMSG_MOT_REQ_STATUSBITS",self.channel,0,self.destination,self.source)


# --
#  high level function
# --
    def get_position(self):
        d=self.get_poscounter()
        return d["Position"]/(1.*self.ustep_to_pos)
# --
# move function
# --
        
    def home(self):
        self.send_command("MGMSG_MOT_MOVE_HOME",self.channel,0,self.destination,self.source)
        self.wait_until_completed()
# --
    def move_relative(self,distance):
        self.send_command("MGMSG_MOT_MOVE_RELATIVE",0,self.destination,self.source,
                1,int(distance*self.ustep_to_pos))
        self.wait_until_completed()

#====================================================================================================================

if __name__=="__main__":
    d1 = Thorlabs_device("40828799","BSC10x","17DRV014 Enc LNR 50mm",1)
    d2 = Thorlabs_device("70854298","BSC20x","17DRV014 Enc LNR 50mm",1)
    d3 = Thorlabs_device("45839057","LTS300","LTS300 300mm Stage")
    d4 = Thorlabs_device("45897070","HS LTS300","HS LTS300 300mm Stage")
    #hslts300=Thorlabs_device("45897070")
    #hslts300.request_info(0,0,DST,SRC)
    #hslts300.get_parameters(0,0,DST,SRC)
    #hslts300.update_message(0,0,DST,SRC)
    #hslts300.get_status(0,0,DST,SRC)

    #serial_number = "45839057"
    #lts300=Thorlabs_device("45839057")
    #lts300.request_info(0,0,DST,SRC)
    #lts300.get_parameters(0,0,DST,SRC)
    #lts300.update_message(0,0,DST,SRC)
    #lts300.get_status(0,0,DST,SRC)

