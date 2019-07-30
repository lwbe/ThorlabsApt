import sys
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




DEBUG=True

def debug(*args):
    if DEBUG:
        print(" ".join([str(i) for i in args]))


tac_data = { "default_command_structure": [
    { "field" : "msg_id",                        "format" : "word",    },      
    { "field" : "param1",                        "format" : "uchar",    },
    { "field" : "param2",                        "format" : "uchar",    },
    { "field" : "dest",                          "format" : "uchar",    },
    { "field" : "source",                        "format" : "uchar",    },
],
             "default_response_structure": [    
                 { "field" : "msg_id",   "format" : "word",    },      
                 { "field" : "param1",   "format" : "uchar",    },
                 { "field" : "param2",   "format" : "uchar",    },
                 { "field" : "dest",     "format" : "uchar",    },
                 { "field" : "source",   "format" : "uchar",    },
             ],

             "MGMSG_MOD_IDENTIFY": { "msg_id"   : 0x0223,},
             "MGMSG_HW_REQ_INFO" : { "msg_id"   : 0x0005, 
                                     "response" : {
                                         "keyword" : "MGMSG_HW_GET_INFO",
                                         "msg_id": 0x0006,   
                                         "response_structure" : [ 
                                             { "field" : "serial_number",                 "format" : "long", },
                                             { "field" : "model_number",                  "format" : "char[8]", },
                                             { "field" : "type",                          "format" : "word",    },
                                             { "field" : "firmware_version_minor_rev " ,  "format" : "uchar",}, 
                                             { "field" : "firmware_version_interim_rev ", "format" : "uchar",}, 
                                             { "field" : "firmware_version_major_rev ",   "format" : "uchar",}, 
                                             { "field" : "firmware_version_unused ",      "format" : "uchar",}, 
                                             { "field" : "internal_data",                 "format" : "char[60]",}, 
                                             { "field" : "HW Version",                    "format" : "word",},
                                             { "field" : "Mod_state",                     "format" : "word",},
                                             { "field" : "nb_channels",                   "format" : "word",},
                                         ],
                                     },
                                 },

             "MGMSG_MOT_MOVE_HOME":  { "msg_id"   : 0x0443,
                                      "response" : {
                                           "keyword": "MGMSG_MOT_MOVE_HOMED",
                                           "msg_id" : 0x0444,
                                           "response_structure" : [],
                                       }
                                },
            
             "MGMSG_MOT_SET_LIMSWITCHPARAMS": {"msg_id" : 0x423,
                                               "command_structure" : [
                                                   { "field" : "chan_id",       "format" : "word", },      
                                                   { "field" : "CW_hardlimit",  "format" : "word", }, 
                                                   { "field" : "CCW_hardlimit", "format" : "word", }, 
                                                   { "field" : "CW_softlimit",  "format" : "long", }, 
                                                   { "field" : "CCW_softlimit", "format" : "long", }, 
                                                   { "field" : "Limit_mode",    "format" : "word", }, 
                                               ],
                                           },
             "MGMSG_MOT_REQ_LIMSWITCHPARAMS": {"msg_id" : 0x424,
                                               "response": {
                                                   "keyword":"MGMSG_MOT_GET_LIMSWITCHPARAMS",
                                                   "msg_id" : 0x425,
                                                   
                                                   "response_structure" : [
                                                       { "field" : "chan_id",       "format" : "word", },      
                                                       { "field" : "CW_hardlimit",  "format" : "word", }, 
                                                       { "field" : "CCW_hardlimit", "format" : "word", }, 
                                                       { "field" : "CW_softlimit",  "format" : "long", }, 
                                                       { "field" : "CCW_softlimit", "format" : "long", }, 
                                                       { "field" : "Limit_mode",    "format" : "word", }, 
                                                   ],
                                               },
                                           },
             "MGMSG_HW_START_UPDATEMSGS": {"msg_id": 0x0011,},
             "MGMSG_HW_STOP_UPDATEMSGS": {"msg_id": 0x0012,},

             "MGMSG_MOT_REQ_STATUSUPDATE": {"msg_id": 0x0480,
                                            "response": {
                                                "keyword":"MGMSG_MOT_GET_STATUSUPDATE",
                                                "msg_id" : 0x481,
                                                
                                                "response_structure" : [
                                                    { "field" : "chan_id",      "format" : "word", },      
                                                    { "field" : "Position",     "format" : "long", }, 
                                                    { "field" : "EncCount",     "format" : "long", }, 
                                                    { "field" : "Status Bits",  "format" : "dword", }, 
                                                    { "field" : "Chan Ident 2", "format" : "word", }, 
                                                    { "field" : "Unused_1",     "format" : "long", },  
                                                    { "field" : "Unused_2",     "format" : "long", },  
                                                    { "field" : "Unused_3",     "format" : "long", }, 
                                                ],
                                            },
                                        },
             "MGMSG_HW_NO_FLASH_PROGRAMMING": {"msg_id": 0x0018,},
             
             "MGMSG_MOD_SET_CHANENABLESTATE": {"msg_id": 0x0210,},
             "MGMSG_MOD_REQ_CHANENABLESTATE": {"msg_id": 0x0211,
                                               "response": {
                                                   "keyword": "MGMSG_MOD_GET_CHANENABLESTATE",
                                                   "msg_id": 0x212,
                                                   "response_structure": []
                                               },
                                           },

             "MGMSG_MOD_SET_POSCOUNTER": {"msg_id": 0x0410,
                                          "command_structure":[
                                              { "field" : "chan_id",       "format" : "word", },      
                                              { "field" : "Position",  "format" : "long", },
                                          ]
                                      },
             "MGMSG_MOT_REQ_POSCOUNTER": {"msg_id": 0x0411,
                                          "response": {
                                              "keyword":"MGMSG_MOT_GET_POSCOUNTER",
                                              "msg_id" : 0x0412,
                                              
                                              "response_structure" : [
                                                  { "field" : "chan_id",       "format" : "word", },      
                                                  { "field" : "Position",  "format" : "long", },
                                              ],
                                          },
                                      },
             "MGMSGS_MOT_SET_VELPARAMS": {"msg_id" : 0x413,
                                          "command_structure":[
                                              {"field" : "Chan_id"      , "format":"word",},
                                              {"field" : "Min_velocity" , "format":"long",},
                                              {"field" : "Accel"        , "format":"long",},                                              
                                              {"field" : "Max_velocity" , "format":"long",},
                                          ]
                                      },
             "MGMSGS_MOT_REQ_VELPARAMS": {"msg_id" : 0x414,
                                          "response" :{
                                              "keyword" : "MGMSGS_MOT_GET_VELPARAMS",
                                              "msg_id" : 0x415,
                                              "response_structure":[
                                                  {"field" : "Chan_id"      , "format":"word",},
                                                  {"field" : "Min_velocity" , "format":"long",},
                                                  {"field" : "Accel"        , "format":"long",},                                              
                                                  {"field" : "Max_velocity" , "format":"long",},
                                              ]
                                          },
                                      },

             "MGMSGS_MOT_SET_JOGPARAMS": {"msg_id" : 0x0416,
                                          "command_structure":[
                                              {"field" : "Chan_id"       , "format":"word",},
                                              {"field" : "Jog_mode"      , "format":"word",},
                                              {"field" : "Jog_step_size" , "format":"long",},
                                              {"field" : "Min_velocity"  , "format":"long",},
                                              {"field" : "Jog_accel"        , "format":"long",},                                              
                                              {"field" : "Jog_max_velocity" , "format":"long",},
                                              {"field" : "Jog_stop_mode"      , "format":"word",},
                                          ]
                                      },
             "MGMSGS_MOT_REQ_JOGPARAMS": {"msg_id" : 0x0417,
                                          "response":{
                                              "keyword":"MGMSGS_MOT_GET_JOGPARAMS",
                                              "msg_id" : 0x0418,
                                              "response_structure":[
                                                  {"field" : "Chan_id"       , "format":"word",},
                                                  {"field" : "Jog_mode"      , "format":"word",},
                                                  {"field" : "Jog_step_size" , "format":"long",},
                                                  {"field" : "Min_velocity"  , "format":"long",},
                                                  {"field" : "Jog_accel"        , "format":"long",},                                              
                                                  {"field" : "Jog_max_velocity" , "format":"long",},
                                                  {"field" : "Jog_stop_mode"      , "format":"word",}
                                              ]
                                          },
                                      },
             "MGMSGS_MOT_SET_GENMOVEPARAMS": {"msg_id" : 0x043A,
                                              "command_structure":[
                                                  {"field" : "Chan_id"       , "format":"word",},
                                                  {"field" : "Backlash_distance"      , "format":"long",}
                                              ]
                                          },
             "MGMSGS_MOT_REQ_GENMOVEPARAMS": {"msg_id" : 0x043B,
                                              "response":{
                                                  "keyword" : "MGMSGS_MOT_SET_GENMOVEPARAMS",
                                                  "msg_id" : 0x043C,
                                                  "response_structure":[
                                                      {"field" : "Chan_id"       , "format":"word",},
                                                      {"field" : "Backlash_distance"      , "format":"long",}
                                                  ]
                                              },
                                          },

             "MGMSGS_MOT_SET_MOVERELPARAMS": {"msg_id" : 0x0445,
                                              "command_structure":[
                                                  {"field" : "Chan_id"       , "format":"word",},
                                                  {"field" : "Relative_distance"      , "format":"long",}
                                              ]
                                          },

             "MGMSGS_MOT_REQ_MOVERELPARAMS": {"msg_id" : 0x0446,
                                              "response":{
                                                  "keyword":"MGMSGS_MOT_GET_MOVERELPARAMS",
                                                  "msg_id" : 0x0447,
                                                  "response_structure":[
                                                      {"field" : "Chan_id"       , "format":"word",},
                                                      {"field" : "Relative_distance"      , "format":"long",}
                                                  ]
                                              },
                                          },
             "MGMSGS_MOT_SET_MOVEABSPARAMS": {"msg_id" : 0x0450,
                                              "command_structure":[
                                                  {"field" : "Chan_id"       , "format":"word",},
                                                  {"field" : "Absolute_position"      , "format":"long",}
                                              ]
                                          },
             "MGMSGS_MOT_REQ_MOVEABSPARAMS": {"msg_id" : 0x0451,
                                              "response" :{
                                                  "keyword": "MGMSGS_MOT_GET_MOVEABSPARAMS",
                                                  "msg_id" : 0x0452,
                                                  "response_structure":[
                                                      {"field" : "Chan_id"       , "format":"word",},
                                                      {"field" : "Absolute_position"      , "format":"long",}
                                                  ]
                                          },
                                          },
             "MGMSGS_MOT_SET_HOMEPARAMS": {"msg_id" : 0x0440,
                                           "command_structure":[
                                               {"field" : "Chan_id"         , "format":"word",},
                                               {"field" : "Home_direction"  , "format":"word",},
                                               {"field" : "Limit_switch"    , "format":"word",},
                                               {"field" : "Home_Velocity"   , "format":"long",},
                                               {"field" : "Offset_distance" , "format":"long",}
                                           ]
                                       },
            "MGMSGS_MOT_REQ_HOMEPARAMS": {"msg_id" : 0x0441,
                                           "response": {
                                               "keyword": "MGMSGS_MOT_GET_HOMEPARAMS",
                                               "msg_id" : 0x0442,
                                               "command_structure":[
                                                   {"field" : "Chan_id"         , "format":"word",},
                                                   {"field" : "Home_direction"  , "format":"word",},
                                                   {"field" : "Limit_switch"    , "format":"word",},
                                                   {"field" : "Home_Velocity"   , "format":"long",},
                                                   {"field" : "Offset_distance" , "format":"long",}
                                               ]
                                           },
                                       },
            "MGMSG_MOT_MOVE_RELATIVE":{"msg_id": 0x0448,
                                       #"as_long_version" : True,
                                       #"command_structure":[
                                       #    {"field" : "Chan_id"       , "format":"word",},
                                       #    {"field" : "Relative_distance"      , "format":"long",}
                                       #]
                                   },
            "MGMSG_MO_MOVE_COMPLETED" : { "msg_id":0x464,
                                          "response_structure" : [
                                              { "field" : "chan_id",      "format" : "word", },      
                                              { "field" : "Position",     "format" : "long", }, 
                                              { "field" : "EncCount",     "format" : "long", }, 
                                              { "field" : "Status Bits",  "format" : "dword", }, 
                                              { "field" : "Chan Ident 2", "format" : "word", }, 
                                          ],
                                      },
            "MGMSG_MOT_MOVE_ABSOLUTE":{"msg_id":0x453,
                                       #"as_long_version":True,
                                       
                                       #"command_structure":[
                                       #    {"field" : "Chan_id"       , "format":"word",},
                                       #    {"field" : "Absolute_position"      , "format":"long",}
                                       #]
                                   },
                                           
            "MGMSG_MOT_MOVE_JOG" :{"msg_id":0x046A},
            "MGMSGS_MOT_MOVE_VELOCITY": {"msg_id" : 0x0457,
                                            # "command_structure":[
                                            #     {"field" : "Chan_id"       , "format":"word",},
                                            #     {"field" : "Relative_distance"      , "format":"long",}
                                            # ]
                                          },
            "MGMSGS_MOT_MOVE_STOP" : {"msg_id" : 0x0465,
                                            # "command_structure":[
                                            #     {"field" : "Chan_id"       , "format":"word",},
                                            #     {"field" : "Relative_distance"      , "format":"long",}
                                            # ]
                                          },
            "MGMSGS_MOT_MOVE_STOPPED": {"msg_id" : 0x0466,
                                          "response_structure" : [
                                              { "field" : "chan_id",      "format" : "word", },      
                                              { "field" : "Position",     "format" : "long", }, 
                                              { "field" : "EncCount",     "format" : "long", }, 
                                              { "field" : "Status Bits",  "format" : "dword", }, 
                                              { "field" : "Chan Ident 2", "format" : "word", }, 
                                          ],
                                    },

         }



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



def compute_size_pack_string(data,t):
    if t not in ["command_structure","response_structure"]:
        print('Error the type of command can only be "command_structure","response_structure" found %s !!\nABORTING' % t)
        sys.exit(0)

    _length = 0
    pack_string = "<"
    val_names = []

    # get the value to evaluate it depends on the type command or return
    # for command we have to take the default

    data_to_scan = tac_data["default_%s" % t][:]            
    if t in data and data[t]:
        data_to_scan.extend(data[t])

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
        debug("type : %s field_name %s total lentgh %d" % (d["format"],d["field"],_length))
    return _length,pack_string,val_names

def get_keyword_data(keyword):
    if keyword not in tac_data:
        print("Keyword %s not found in the available keyword!!!\nABORTINGkeywords are:%s" % (keyword,"\n\t".join(tac_data.keys())))
        sys.exit(0)
    return tac_data[keyword]
    
def create_message(*args):
    d = get_keyword_data(args[0])
    c,pack_string,val_names = compute_size_pack_string(d,"command_structure")
    if len(val_names) > 6:
        if (args[3] >> 7) != 1:   
            print("Asking for a long message but bit 7 of the 4 argument is not set to one")
            for i,j  in zip(val_names,args):
                print("%s %s (%s)" % (i,j,tohex(j)))

            sys.exit(0)
    #args[0] =  d["msg_id"]
    try:
        msg = struct.pack(pack_string ,d["msg_id"],*args[1:])
    except struct.error as e:
        print("Error : %s with pack_strings %s and args %s " % (e,pack_string,str(args[1:])))
        print("Expected arguments are: %s"% (", ".join(val_names)))
        sys.exit(0)
    print("msg sent: %s (%s)" % (msg,tohex(msg)))
    if "response" in d:
        response_length,p,v = compute_size_pack_string(d["response"],"response_structure")
        return response_length,msg
    else:
        return 0,msg

def read_message(keyword,msg):
    d=get_keyword_data(keyword)
    response_length,p,val_names = compute_size_pack_string(d["response"],"response_structure")
    try:
        unpack_msg = struct.unpack(p,msg)
    except struct.error as e:
        print("Error : %s pack_string %s msg %s " % (e,p,msg))
        print("Mismatch between definition and what's received we expect %s " %  (", ".join(val_names)))
    print("msg received: %s (%s)" % (msg,tohex(msg)))
    debug("unpack_msg %s len %d" % (str(unpack_msg),len(unpack_msg)))
    return "\n\t".join(["%s : %s (%s) "% (i,j,tohex(j)) for i,j in zip(val_names,struct.unpack(p,msg))])
