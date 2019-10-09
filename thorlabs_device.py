import serial
import os,sys

# for python 2.7
import ConfigParser as configparser

stages_file="MG17APTServer.ini"

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
                 timeout=10,
                 write=None,
                 read=None):
        # if we don't supply write or read command we fallback on serial
        self.controller_name = controller_name
        self.stage_name = stage_name
        self.channel = chan

        if write == None and read == None:
            # initialize the communication to the write and read commands
            if not port:
                port = self.find_dev(serial_number)
            if port == None:
                print("No port found for serial_number %s !!\nABORTING " % serial_number)
                sys.exit(0)

            thor_dev = serial.Serial(port,baudrate=baudrate,timeout=timeout)
            self.write = thor_dev.write
            self.read =  thor_dev.read
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

# --
    def configure(self):

        self.set_controller_and_stage()
        # extract the data for the controller and stage and set them

        self.no_flash_programming()
        self.stop_update_msg()
        self.get_info()
        self.bay_used()
        self.enable()
        self.set_limitswitch_params()
        self.get_status_update()
        self.set_velocity_params()


        # min and max position
        self.pos_min = self.stage["min pos"]
        self.pos_max = self.stage["max pos"]

        # speed and power
        self.power_rest = self.stage["rest factor"]
        self.power_move = self.stage["move factor"]

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
        
#--
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

    # communication function with the device
    def raw_read(self,length):
        return self.read(length)
#--
    def raw_write(self,keyword,*args):
        need_read , msg = self.thor_msg.create_message(keyword,*args)
        self.write(msg)
        return need_read , msg

#--
    def send_command(self,*args,**kwargs):
        """
        function to send the command with parameter and give back the result if any
        """
        print("args ",args)
        print("kwargs ",kwargs)

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
        log(DEBUG,"full message including header : %s" % (recv_msg))
        return recv_msg
        
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
    def no_flash_programming(self):
        return ("MGMSG_HW_NO_FLASH_PROGRAMMING",0,0,self.destination_controller,self.source)
# -- 
    @send
    def stop_update_msg(self):
        return ("MGMSG_HW_STOP_UPDATEMSGS",self.channel,0,self.destination,self.source)
# --
    @send 
    def start_update_msg(self):
        return ("MGMSG_HW_START_UPDATEMSGS",self.channel,0,self.destination,self.source)
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
    def set_home_params(self):
        return ("MGMSG_MOT_SET_HOMEPARAMS",0,self.destination,self.source,
                self.channel, 
                int(self.stage["home dir"]),
                int(self.stage["home limit switch"]),
                int(float(self.stage["home vel"])*self.ustep_to_vel),
                int(float(self.stage["home zero offset"])*self.ustep_to_pos))
# --
    @send
    def get_home_params(self):
        return ("MGMSG_MOT_REQ_HOMEPARAMS",self.channel,0,self.destination,self.source)
# --
    @send
    def set_limitswitch_params(self):
        return ("MGMSG_MOT_SET_LIMSWITCHPARAMS", 0, self.destination, self.source,
                self.channel,
                int(self.stage["cw hard limit"]),
                int(self.stage["ccw hard limit"]),
                int(float(self.stage["max pos"])*self.ustep_to_pos),
                int(float(self.stage["min pos"])*self.ustep_to_pos),
                int(self.stage["soft limit mode"]))
# --
    @send
    def get_limitswitch_params(self):
        return ("MGMSG_MOT_REQ_LIMSWITCHPARAMS", self.channel, 0, self.destination, self.source)
# --
    @send
    def get_info(self):
        return ("MGMSG_HW_REQ_INFO",0,0,self.destination,self.source)
# --
    @send
    def bay_used(self):
        return ("MGMSG_RACK_REQ_BAYUSED",self.channel,0,self.destination_controller,self.source)               
# --
    @send
    def get_status_update(self):
        return ("MGMSG_MOT_REQ_STATUSUPDATE",self.channel,1,self.destination,self.source)

# move function
# --
    @send
    def home(self):
            return ("MGMSG_MOT_MOVE_HOME",self.channel,0,self.destination,self.source)
# --
    @send
    def move_relative(self,distance):
        return ("MGMSG_MOT_MOVE_RELATIVE",self.channel,0,self.destination,self.source,
                1,int(distance*self.ustep_to_pos))

# --
    @send
    def get_poscounter(self):
        return ("MGMSG_MOT_REQ_POSCOUNTER",self.channel,0,self.destination,self.source)

#  high level function
# --
    def get_position(self):
        d=self.get_poscounter()
        return d

if __name__=="__main__":
    d = Thorlabs_device("40828799","BSC10x","17DRV014 Enc LNR 50mm",1)
                
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

