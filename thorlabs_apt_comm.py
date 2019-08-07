import sys,json
import pprint
import struct


"""
Notes:

description of data
===================

The idea is to be as close as possible of the:

 thorlabs APT Controllers 
HOST-Controller Communications Protocol

as possible. This code has been implemented following the 04 jun 2019 version of this documentation

command_structure and response structure
----------------------------------------
  command_structure and response_structure has the same syntax to describe the input. 
  response_structure = None implies that we should not look for an answer
  response_structure = [] means there is a response but is only a default header.
"""



ERROR = 4
WARN  = 3
DEBUG = 2
INFO  = 1
NONE  = 0

LOG_LEVEL=INFO

pprint_dict=pprint.PrettyPrinter(indent=2,depth=4)
print_dict=pprint_dict.pprint

# utility functions
def log(level,msg):

    if level <= LOG_LEVEL:
        print(msg)

def format_msg(msg):
    return("\t%s" % msg.replace("\n","\n\t"))

def on_warning(msg):
    print("WARN\t:\n %s",format_msg(msg))

def on_error(msg):
    print(msg)
    print("ERR\t:\n %s\nABORTING !!",format_msg(msg))
    sys.exit(0)
    
def tohex(v):
    try:
        h_v = hex(v)[2:]
        if len(h_v)%2 != 0:
            h_v = "0"+h_v
        return "0x"+" ".join([h_v[i:i+2].upper() for i in range(0,len(h_v),2)])
    except:
        try:
            return "0x"+" ".join("{:02x}".format(ord(c)).upper() for c in v)
        except:
            pass

    return ""

# --

class Thorlabs_apt_communication():
    def __init__(self,filename="thorlabs_apt.json"):
        """
        read jsonfile and set the protocol
        """
        try:
            self.tac_data = json.load(open(filename))
        except (IOError,ValueError) as e:
            on_error("%s" % e)

        self.msg_id_to_keyword={}
        # available values
        available_msg_keys = ["msg_id" , "msg_type" ,"data_structure" ,"as_long_version"]
        available_msg_types = ["send",                  # send the command and don't expect answer  if not supplied this the 
                                                        # default
                               "read",                  # this cannot be send it is only a response
                               "request"]               # this means that the keyword is a command waiting for an answer
        available_data_structure_keys = ["field","format"]
        available_data_format = ["word","short","dword","long","char","uchar","byte"]

        # check the data
        apt_keys=self.tac_data.keys()

        # the header
        if "header" not in apt_keys:
            on_error("no header section in json file !!")
            # do some preparation
        msg_size,msg_pack_string,msg_val_names = self.compute_size_pack_string(self.tac_data["header"]["data_structure"])
        self.tac_data["header"].update({"msg_size":msg_size,
                                            "msg_pack_string":msg_pack_string,
                                            "msg_val_names":msg_val_names})
        
        # everthing else
        msg_ids = []
        apt_keys.remove("header")
        for k in apt_keys:
            msg_dict = self.tac_data[k]
            msg_keys = msg_dict.keys()

            # check msg_id
            if "msg_id" not in msg_keys:
                on_error("missing \"msg_id\" for %s" % k)

            msg_keys.remove("msg_id")
            try:
                msg_dict["msg_id"]=int(msg_dict["msg_id"],16)
            except ValueError as e:
                on_error("%s\nCannot convert to int msg_id of %s with value %s" % (msg_dict["msg_id"],k))

            if msg_dict["msg_id"] in msg_ids:
                on_error("duplicate \"msg_id\" entry %d (%s) for %s" % ( msg_dict["msg_id"],tohex(msg_dict["msg_id"]),k))
            msg_ids.append(msg_dict["msg_id"])

            # lookup msg_id to keyword
            self.msg_id_to_keyword[msg_dict["msg_id"]]=k

            #check msg_types
            if "msg_type" not in msg_keys:
                # let's assume it is write then
                msg_dict["msg_type"]="send"

                if msg_dict["msg_type"] not in available_msg_types:
                    on_error("Unknown msg_type %s for %s (possible values are %s)" % (msg_dict["msg_type"],
                                                                                      k,
                                                                                      ", ".join(available_msg_types)))
            else:
                msg_keys.remove("msg_type")

            # check data structures
            msg_size,msg_pack_string,msg_val_names = 0,"",[]
            if "data_structure" in msg_keys:
                msg_keys.remove("data_structure")
                ds=msg_dict["data_structure"]
                for data in ds:
                    for dk in data.keys():
                        if dk not in available_data_structure_keys:
                            on_error("Unknown data_structure key %s for %s (possible values are %s)" % (dk,
                                                                                                        k,
                                                                                                        ", ".join(available_data_structure_keys)))
                if data["format"] not in available_data_format:
                       on_error("Unknown data_format %s for %s (possible values are %s)" % (data["format"],
                                                                                            k,
                                                                                            ", ".join(available_data_format)))

                # do some preparation
                msg_size,msg_pack_string,msg_val_names = self.compute_size_pack_string(ds)

            msg_dict.update({"msg_size":msg_size,
                             "msg_pack_string":msg_pack_string,
                             "msg_val_names":msg_val_names})

            # check that left keys are legal.
            for left_keys in msg_keys:
                if left_keys not in available_msg_keys:
                    on_error("Unknown key %s for %s (possible values are %s)" % (left_keys,
                                                                                 k,
                                                                                 ", ".join(available_msg_keys)))
                    
            
    def compute_size_pack_string(self,data_to_scan):

        _length = 0
        pack_string = ""
        val_names = []

        # get the value to evaluate it depends on the type command or return
        # for command we have to take the default

        for d in data_to_scan:
            val_names.append(d["field"])
            if d["format"] == "word":     # unsigned 16  bit integer
                _length += 2
                pack_string += "H"
            elif d["format"] == "short":  # signed 16 bit integer
                _length += 2
                pack_string += "h"
            elif d["format"] == "dword":  # unsigned 32 bit integer
                _length += 4
                pack_string += "I"
            elif d["format"] == "long":
                _length += 4
                pack_string += "i"
            elif d["format"] == "char":
                _length += 1
                pack_string += "c"
            elif d["format"] == "uchar":
                _length += 1
                pack_string += "B"
            elif d["format"].startswith("char["):
                n_char = int(d["format"].replace("char[","").replace("]",""))
                _length += n_char
                pack_string += "%ds"%n_char
            elif d["format"].startswith("byte["):
                n_bytes = int(d["format"].replace("byte[","").replace("]",""))
                _length += n_bytes
                pack_string += "%dc"%n_bytes
            else:
                print("Unknown type \nABORTING")
                sys.exit(0)
            log(DEBUG,"type : %s field_name %s total lentgh %d" % (d["format"],d["field"],_length))
        return _length,pack_string,val_names

    def get_keyword_data(self,keyword):
        if keyword not in self.tac_data:
            on_error("Keyword %s not found available keywords are: %s" % (keyword,
                                                                          "\n\t".join(self.tac_data.keys())))
            sys.exit(0)
        return self.tac_data[keyword]
    

    def create_message(self,*args):
        d = self.get_keyword_data(args[0])
        
        pack_string="<"+self.tac_data["header"]["msg_pack_string"]+d["msg_pack_string"]
        expected_names=self.tac_data["header"]["msg_val_names"] + d["msg_val_names"]
        nb_args=len(expected_names)

        if nb_args != len(args):
            err_msg="the number of args supplied is not equal to the expected one\n"  
            err_msg+="args supplied : %s" % ("\n\t".join(args))
            err_msg+="args expected : %s" % ("\n\t".join(expected_names))
            on_error(err_msg)
            
        if nb_args > 6:
            if (args[3] >> 7) != 1:   
                on_error("Asking for a long message but bit 7 of the 4 argument is not set to one")

        try:
            msg = struct.pack(pack_string ,d["msg_id"],*args[1:])
        except struct.error as e:
            err_msg = "Error : %s with pack_strings %s and args %s\n" % (e,pack_string,tohex(d["msg_id"])+str(args[1:]))
            err_msg += "Expected arguments are: %s"% (", ".join(expected_names))
            on_error(err_msg)

        log(INFO,"msg sent: %s (%s)" % (msg,tohex(msg)))

        return d["msg_type"],msg

    def read_message(self,keyword,msg):
        d=self.get_keyword_data(keyword)
        pack_string="<"+self.tac_data["header"]["msg_pack_string"]+d["msg_pack_string"]
        msg_val_names=self.tac_data["header"]["msg_val_names"]+d["msg_val_names"]
        try:
            unpack_msg = struct.unpack(pack_string,msg)
        except struct.error as e:
            print("Error : %s pack_string %s msg %s " % (e,p,msg))
            print("Mismatch between definition and what's received we expect %s " %  (", ".join(val_names)))
            print("msg received: %s (%s)" % (msg,tohex(msg)))
            debug("unpack_msg %s len %d" % (str(unpack_msg),len(unpack_msg)))
        return dict([(i,j) for i,j in zip(msg_val_names,unpack_msg)])

    def print_message(self,unpack_msg):            
        d=self.get_keyword_data(keyword)
        pack_string="<"+self.tac_data["header"]["msg_pack_string"]+d["msg_pack_string"]
        msg_val_names=self.tac_data["header"]["msg_val_names"]+d["msg_val_names"]
        try:
            unpack_msg = struct.unpack(pack_string,msg)
        except struct.error as e:
            print("Error : %s pack_string %s msg %s " % (e,p,msg))
            print("Mismatch between definition and what's received we expect %s " %  (", ".join(val_names)))
            print("msg received: %s (%s)" % (msg,tohex(msg)))
            debug("unpack_msg %s len %d" % (str(unpack_msg),len(unpack_msg)))

        return_msg="\tmsg_id %s (%s) %s\n\t" % (unpack_msg[0],unpack_msg[0],keyword)
        return_msg+="\n\t".join(["%s : %s (%s) "% (i,j,tohex(j)) for i,j in zip(msg_val_names[1:],unpack_msg[1:])])
        return return_msg


        

    def read_header(self,msg):
        pack_string="<"+self.tac_data["header"]["msg_pack_string"]
        try:
            unpack_msg = struct.unpack(pack_string,msg)
        except struct.error as e:
            print("Error : %s pack_string %s msg %s " % (e,pack_string,msg))
            print("Mismatch between definition and what's received we expect %s " %  (", ".join(val_names)))
            print("msg received: %s (%s)" % (msg,tohex(msg)))
            debug("unpack_msg %s len %d" % (str(unpack_msg),len(unpack_msg)))

        if unpack_msg[0] in  self.msg_id_to_keyword: 
            keyword = self.msg_id_to_keyword[unpack_msg[0]]
            d = self.get_keyword_data(keyword)
            return d["msg_size"],keyword
        else:
            on_error("cannot find keyword for value %d (%s) full msg %s" % (unpack_msg[0],tohex(unpack_msg[0]),str(unpack_msg)))

if __name__=="__main__":
    t=Thorlabs_apt_communication()

    #print_dict(t.tac_data)

    r,msg = t.create_message("MGMSG_HW_REQ_INFO",0,0,0x1,0x50)

    print("%s %s" %(r,msg))


