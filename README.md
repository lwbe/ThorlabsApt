# ThorlabsApt

**NOTE** this code is a semi work in progress I needed it to debug some thorlabs hardware but it is not meant to be a complete working solution. Don't hesitate to contact me for help.

## Overview
The motivation of this package is to implement the thorlabs "HOST-Controller Communications Protocol" as described in the 04 jun 2019 version of this documentation a version can be found here https://www.thorlabs.com/Software/Motion%20Control/APT_Communications_Protocol.pdf but it might be more up to date. The idea is to create the binary string to send to the device. 

This package is composed of two parts **thorlabs_apt_comm.py**  which implement the communication protocol  and **thorlabs_device.py** a simple code that talk to thorlabs device through serial port and is rather limited.

### thorlabs_apt_comm.py
The communication protocol is described in the link above and essentially consist in a keyword followed by mandatory parameters and optionnaly data. The transcription of the protocol is made in the  thorlabs_apt.json file.

A typical entry of this json file is 


    "header" : {
        "data_structure":[ 
            { "field" : "msg_id",  "format" : "word"   },      
            { "field" : "param1",  "format" : "uchar"  },
            { "field" : "param2",  "format" : "uchar"  },
            { "field" : "dest",    "format" : "uchar"  },
            { "field" : "source",  "format" : "uchar"  }
        ]
    },
     "header_long" : {
        "data_structure":[ 
            { "field" : "msg_id",             "format" : "word"   },      
            { "field" : "data_packet_length", "format" : "word"  },
            { "field" : "dest",               "format" : "uchar"  },
            { "field" : "source",             "format" : "uchar"  }
        ]
    },
     "MGMSG_HW_NO_FLASH_PROGRAMMING": {   
        "msg_id"   : "0x0018"
    },
     "MGMSG_MOD_IDENTIFY": {   
        "msg_id"   : "0x0223"
    },
     ....
    "MGMSG_HW_REQ_INFO" : {   
        "msg_id"   : "0x0005",
        "msg_type" : "request"
     }, 
     "MGMSG_HW_GET_INFO": {
        "msg_id": "0x0006", 
        "msg_type" : "read",  
        "data_structure" : [ 
            { "field" : "serial_number",                 "format" : "long"    },
            { "field" : "model_number",                  "format" : "char[8]" },
            { "field" : "type",                          "format" : "word"    },
            { "field" : "firmware_version_minor_rev " ,  "format" : "uchar"   }, 
            { "field" : "firmware_version_interim_rev ", "format" : "uchar"   },
            { "field" : "firmware_version_major_rev ",   "format" : "uchar"   }, 
            { "field" : "firmware_version_unused ",      "format" : "uchar"   }, 
            { "field" : "internal_data",                 "format" : "char[60]"}, 
            { "field" : "HW Version",                    "format" : "word"    },
            { "field" : "Mod_state",                     "format" : "word"    },
            { "field" : "nb_channels",                   "format" : "word"    }
        ]
    },


Quickly, the simple commands like **MGMSG\_HW\_NO\_FLASH\_PROGRAMMING** will be composed of the **msg_id** (here 0x0223)  value with 4 more parameters which will give a 6 bytes word.

Some commands will reply and give values and in fact one should send the **\_REQ\_** part of the command and read 6 bytes from the device to get the header and then read the data. For example sending **MGMSG\_HW\_REQ\_INFO** will return a header of 6 bytes containing **MGMSG\_HW\_GET\_INFO** containing the length of the data in the third byte here 0x44 and one then can read the next 0x44 = 68 bytes and decode them according the data_structure_dictionnary

### thorlabs_device.py
Uses thorlabs_apt_comm.py to talk to device. It knows only a few controllers "BSC10x", "LTS300", "BSC20x","HS LTS300" and the stages are stored in the file MG17APTServer.ini and one should look up in this file the name of the stage. Some functions only are implemented
   
- no\_flash\_programming
- stop\_update\_msg:
- start\_update\_msg
- enable
- disable
- set\_homeparams
- get\_homeparams
- set\_velparams
- set\_velparams_max
- get\_velparams
- set\_limitswitchparams
- get\_limitswitchparams
- set\_powerparams
- get\_powerparams
- get\_info
- bay\_used
- get\_status_update
- get\_poscounter
- get\_statusbits
- get\_position
- home
- move\_relative

They are more or less the same as the **yyyy** in the **MSG\_xxx\_yyyyyy** or made more human readable 

To instanciate the class for a device the syntax is 

     def __init__(self,
     Thorlabs_device(serial_number,
		     controller_name,
                     stage_name,
                     chan=None,
                     port=None,
                     baudrate=115200,
                     timeout=10,
                     write=None,
                     read=None):

-  Where **serial_number** is the serial number that can be found with

    lsusb -v | grep iSerial

-  where **controller\_name** is one of the  "BSC10x", "LTS300", "BSC20x","HS LTS300"  and 
-  where **stage\_name** should be taken as the entry in MG17APTServer.ini. For example for a LTS300 stage there are two entries 

   [LTS300 300mm Stage]
   [HS LTS300 300mm Stage]

   and the stage name is either "LTS300 300mm Stage" or "HS LTS300 300mm Stage"

-  **chan** should be set to something if the controller has more than one channel. Beware that in the case of multichannel you need to set one device per channel.

####Examples

For a LTS300 with serial number 45xxxxx

        lts300= Thorlabs_device("45839057","LTS300","LTS300 300mm Stage")

For a BS103 with serial number 40xxxxxx and stage DRV014 50mm

    bsc103 = Thorlabs_device("40xxxxxxx","BSC10x","17DRV014 Enc LNR 50mm",1)
 
Then to get the info of the stage as a dictionnary 

    lts300.get_info()

or 
 
    bs103.get_info()


Beware that you need to have the controller present otherwise it will crash since it cannot find the device with this serial number.


## Installation
This python software works with python 2.7 

To use this package you need to install the packages that are store in doc/requirements.txt

The best is to use a virtual environement you need to install **virtualenv** from your distribution package

    virtualenv venv
    source venv/bin/activate
    pip install -r doc/requirements.txt


