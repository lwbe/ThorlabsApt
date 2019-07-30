import serial
import os,sys
import thorlabs_apt_comm as tac


tac.DEBUG=False
HSLTS=None
class Thorlab_device():
    def __init__(self,serial_number,port=None,baudrate=115200,timeout=10,write=None,read=None):
        # if we don't supply write or read command we fallback on serial
        
        if write == None and read == None:
            # initialize the communication to the write and read commands
            if not port:
                port = self.find_dev(serial_number)
            print("talking to port %s for serial number %s" % (port,serial_number))
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
        expected_return_length , msg=tac.create_message(keyword,*args)
        self.write(msg)

        return expected_return_length,msg

    def send_command(self,keyword,*args):
        """
        function to send the command with parameter and give back the result if any
        """
        expected_return_length , msg=tac.create_message(keyword,*args)
        self.write(msg)
        
        # getting the response
        recv_msg=""
        if expected_return_length:
            raw_recv_msg = self.read(expected_return_length)
            recv_msg = tac.read_message(keyword,raw_recv_msg)
            return recv_msg
        return "None"

    def send_command2(self,keyword,*args):
        """
        function to send the command with parameter and give back the result if any
        """
        expected_return_length , msg=tac.create_message(keyword,*args)
        self.write(msg)
        
        # getting the response
        recv_msg=""
        if expected_return_length:
            raw_recv_msg = self.read(expected_return_length)
            recv_msg = tac.read_message(keyword,raw_recv_msg)
            return recv_msg
        return "None"


# finding the /dev/
#serial_number = "45897070"   # new LTS300
if __name__=="__main__":
    SRC=0x01
    DST=0x50
    

    lts300=Thorlab_device("45839057")
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
    print("MGMSG_MOT_REQ_POSCOUNTER")
    print(lts300.send_command("MGMSG_MOT_REQ_POSCOUNTER"            ,1,0,DST,SRC))

    hslts300=Thorlab_device("45897070")
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
    print("MGMSG_MOT_REQ_POSCOUNTER")
    print(hslts300.send_command("MGMSG_MOT_REQ_POSCOUNTER"            ,1,0,DST,SRC))
    
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

