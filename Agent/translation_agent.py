"""
Weiyang Mo (wmo@optics.arizona.edu)
"""
import ast
import math
import struct
import time
import sys
import Queue
import threading
import socket
import array
import logging
import operator

from nistica import Nistica

log_level = 'DEBUG' #Set log level
if log_level == 'INFO':
    logging.basicConfig(level=logging.INFO)
if log_level == 'DEBUG':
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.CRITICAL)




AGENT_IP_LIST = []
try:
    agent_ip_file_loc = 'agent.txt'
    logging.debug('Opening %s to retrive default agent IP list' % agent_ip_file_loc)
    agent_ip_file = open(agent_ip_file_loc,'r')
    for line in agent_ip_file:
        if len(line.split('.'))!= 4:
            logging.critical('The IP address read from %s is malformed %s, expect xxx.xxx.xxx.xxx' %  (agent_ip_file_loc,line.rstrip()))
            sys.exit()
        else:
            AGENT_IP_LIST.append(line.rstrip())
    logging.info('Default agent IP list:%s' % str(AGENT_IP_LIST))
    logging.debug('Agent list is successfully read')
    logging.debug('Next step is to decide the agent IP and RYU')
except IOError as e:
    logging.critical(e)
    logging.critical('Failed to open file %s!Check if the file exists' % agent_ip_file_loc)
    sys.exit()

automated_IP_discover = True #automate discover agent's IP and then set correct RYU IP
if automated_IP_discover:
    """Automate find 192.168.x.x IP, and connect to a correct RYU IP.
    This might fail if this computer has more than one IP address
    having format 192.168.x.x
    """
    logging.debug('Automatic IP discover is enabled')
    from netifaces import interfaces, ifaddresses, AF_INET
    for ifaceName in interfaces():
        addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
        logging.info('interfacename:%s,address:%s' % (ifaceName, ', '.join(addresses)))
        address = str(addresses[0])
        if address == 'No IP addr':
            pass
        else:
            if address.split('.')[0:2] == ['192','168']: #The interface we care starts with 192.168.x.x
                AGENT_IP = address
                if AGENT_IP not in AGENT_IP_LIST:
                    logging.warn('Agent IP %s does no belong to the default IP list' % AGENT_IP)
                    response = raw_input('Press Enter to Continue')
                    
                third = AGENT_IP.split('.')[2]
                RYU = ['192','168','0','0']
                RYU[2] = third
                RYU_IP = '.'.join(RYU)
                RYU_PORT = 6633
                agent_node_file_loc = 'agent%s_node.txt' % third
                agent_monitor_file_loc = 'agent%s_monitor.txt' % third
                datapath_id_int = 16 + int(third)
                datapath_id = chr(datapath_id_int)
                logging.debug('agent_node file location:%s' % (agent_node_file_loc))
                logging.debug('agent_monitor file location:%s' % (agent_monitor_file_loc))
                logging.debug('datapath id:%s' %(datapath_id_int))
                logging.info('RYU IP,%s:%s' % (RYU_IP,RYU_PORT))
                break
        
else:
    logging.debug('Manual IP input is enabled')
    AGENT_IP = raw_input('Enter agent IP address(xxx.xxx.xxx.xxx):')
    if AGENT_IP in AGENT_IP_LIST:
        if AGENT_IP == '192.168.1.100':
            RYU_IP = '192.168.1.0'
            agent_node_file_loc = 'agent1_node.txt'
            agent_monitor_file_loc = 'agent1_monitor.txt'
            datapath_id_int = 17
            datapath_id = chr(datapath_id_int)
            logging.debug('agent_node file location:%s' % (agent_node_file_loc))
            logging.debug('agent_monitor file location:%s' % (agent_monitor_file_loc))
            logging.debug('datapath id:%s' % (datapath_id_int))
        elif AGENT_IP == '192.168.2.100':
            RYU_IP = '192.168.1.0'
            agent_node_file_loc = 'agent2_node.txt'
            agent_monitor_file_loc = 'agent2_monitor.txt'
            datapath_id_int = 18
            datapath_id = chr(datapath_id_int)
            logging.debug('agent_node file location:%s' % (agent_node_file_loc))
            logging.debug('agent_monitor file location:%s' % (agent_monitor_file_loc))
            logging.debug('datapath id:%s' %(datapath_id_int))
       
    else:
        logging.critical('The IP address %s you entered is not a valid agent IP!' % AGENT_IP)
        logging.critical('Exit the program.....')
        sys.exit()
    RYU_PORT = int(raw_input('Enter target tcp port (6633 by default):'))
    logging.info('RYU IP,%s:%s' % (RYU_IP,RYU_PORT))
    if RYU_PORT != 6633:
        logging.warning('You set non-default RYU port %s, the default port is 6633' % RYU_PORT)

logging.debug('Agent IP and RYU IP is successtully set')
logging.debug('Now determine the topology mapping')
    
NODETOCONNECTION ={}
"""
a mapping between node id to serial com number,
may vary with system change
"""
try:
    agent_node_file = open(agent_node_file_loc,'r')
    logging.debug('Reading node information from agent %s' % (AGENT_IP))
    for line in agent_node_file:
        try:
            (nodeid,serialcom) = line.split(':')
            serialcom = serialcom.rstrip()
        except ValueError as e:
            logging.critical(e)
            logging.critical('Text file content is not in correct format.' \
                             'Sould be nodeid:serialcom')
            sys.exit()
        try:
##            locals()['node'+ str(nodeid)] = 'Connection %s' % nodeid
            locals()['node'+ str(nodeid)] = Nistica(serialcom)
        except IOError as e:
            logging.critical(e)
            logging.critical('The serial port %s is not connected to this agent %s' % (serialcom,AGENT_IP))
            for device in NODETOCONNECTION.values():
                device.close()
            sys.exit()       
        NODETOCONNECTION[int(nodeid)] = locals()['node'+ str(nodeid)]         
except IOError as e:
    logging.critical(e)
    logging.critical('Failed to open file %s!Check if the file exists' % agent_node_file_loc)
    sys.exit()


PORTIDTOPORT={} #For future development...not used now
##for nodeid in NODETOCONNECTION.keys():
##    PORTIDTOPORT[nodeid] = {}
##
##try:
##    agent_port_file_loc = 'port.txt'
##    agent_port_file = open(agent_port_file_loc,'r')
##    for line in agent_port_file:
##        (nodeid,portmapping) = line.split(';')
##        try:
##            portmapping = ast.literal_eval(portmapping)
##        except ValueError as e:
##            logging.critical(e)
##            logging.critical('Text file content is not in correct format.' \
##                                 'Sould be nodeid;{portid:port}')
##        nodeid = int(nodeid)
##        for (portid,port) in portmapping.items():
##            PORTIDTOPORT[nodeid][portid] = port
##except IOError as e:
##    logging.critical(e)
##    logging.critical('Failed to open file %s!Check if the file exists' % loc)
##    sys.exit()
##

NODEPORTIDTOOMONITOR = {} #Note, assume OCM monitors the corresponding node. e.g. NODE1 OCM monitors power of NODE1
try:
    agent_monitor_file = open(agent_monitor_file_loc,'r')
    logging.debug('Reading monitor information from agent %s' % (AGENT_IP))
    for line in agent_monitor_file:
        try:
            (portion1,portion2) = line.split(':')
            (NODEID,PORTID) = ast.literal_eval(portion1)
            (MONITORNODE,MONITORPORT) = ast.literal_eval(portion2) #MONITORPORT=0 if OCM of subswitch 0, 1 if OCM of subswitch 1
            NODEPORTIDTOOMONITOR[(NODEID,PORTID)] = (MONITORNODE,MONITORPORT)
        except ValueError as e:
            logging.critical(e)
            logging.critical('Text file content is not in correct format.' \
                             'Sould be portid')
            sys.exit()


            
except IOError as e:
    logging.critical(e)
    logging.critical('Failed to open file %s!Check if the file exists' % agent_monitor_file_loc)
    sys.exit()
    
        
HELLO = bytearray('\x05\x00\x00\x10\x00\x00\x00\x2c\x00\x02\x00\x08\x00\x00\x00\x10')
FEATURE_REPLY = '\x05\x06\x00\x20\x15\xa7\xe7\x34\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\xfe\x00\x00\x00\xff\x00\x00\xff\x00\x00\x00\x00'
FEATURE_REPLY = list(FEATURE_REPLY)
FEATURE_REPLY[15] = datapath_id
FEATURE_REPLY = ''.join(FEATURE_REPLY)
assert len(FEATURE_REPLY) == 32
WSS_SETUP_REPLY_HEADER = '\x05\x75\x00\x18\x00\x00\x00\x00'
assert len(WSS_SETUP_REPLY_HEADER) == 8
WSS_TEARDOWN_REPLY_HEADER = '\x05\x77\x00\x18\x00\x00\x00\x00'
assert len(WSS_TEARDOWN_REPLY_HEADER) == 8
GET_OSNR_REPLY_HEADER = '\x05\x79\x00\x20\x00\x00\x00\x00'
assert len(GET_OSNR_REPLY_HEADER) == 8

WSS_SETUP_REQUEST_STR = '!QIIIIIIIII'
WSS_SETUP_REPLY_STR = '!QII'
WSS_TEARDOWN_REQUEST_STR = '!QIIIIIIIII'
WSS_TEARDOWN_REPLY_STR = '!QII'
GET_OSNR_REQUEST_STR = '!QIIIIIIII'
GET_OSNR_REPLY_STR = '!QIIII'        

q = Queue.Queue()


class TCP_bridge(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = (RYU_IP,RYU_PORT)
        try:
            self.sock.connect(self.connection)
        except:
            logging.critical('Time out....cannot connect to %s:%s' % (RYU_IP,RYU_PORT))
            for device in NODETOCONNECTION.values():
                device.close()
            sys.exit()
            
        print >>sys.stderr, 'connecting to the controller:%s port %s' % self.connection

    def start(self):
        try:
            while(1):
                self.data = self.sock.recv(100)
                q.put(self.data)                

        except Exception as e:
            logging.critical('OOPS, something wrong when capturing received data, that might be due to the connection disrption')
            logging.critical('Can not be recovered, agent shall be manually rebooted...')
            for device in NODETOCONNECTION.values():
                device.close()
            sys.exit()
        finally:
            self.sock.close()

    def msg_handler(self):
        try:
            while(1):
                data = q.get()
                data = [ord(c) for c in data]
                data = bytearray(data)
                if self.belong_to(data) == 'HELLO':
                    logging.info('Receive Hello Request')
                    self.sock.sendall(HELLO)
                    logging.info('Hello Reply Sent to RYU')
                    logging.info('---------------------------------------')
                elif self.belong_to(data) == 'FEATURE_REQUEST':
                    logging.info('Receive FEATURE_REQUEST')
                    self.sock.sendall(FEATURE_REPLY)
                    logging.info('FEATURE_REPLY SENT')
                    logging.info('---------------------------------------')
                elif self.belong_to(data) == 'WSS_SETUP_REQUEST':
                    try:
                        assert struct.calcsize(WSS_SETUP_REQUEST_STR) == len(data[8:])
                    except AssertionError as e:
                        logging.critical(e)
                        logging.critical('WSS_SETUP_REQUEST from RYU is not in a correct format')
                        for device in NODETOCONNECTION.values():
                            device.close()
                        sys.exit()
                        
                    (datapath_id,
                     message_id,
                     ITU_standards,
                     node_id,
                     input_port_id,
                     output_port_id,
                     start_channel,
                     end_channel,
                     experiment1,
                     experiment2)=struct.unpack(WSS_SETUP_REQUEST_STR,self.data[8:])
                    logging.info('Recieve WSS_SETUP_REQUEST from RYU')
                    logging.debug('  datapath_id=%s,message_id=%s, ' \
                        'ITU_standards=%s,node_id=%s,input_port_id=%s,output_port_id=%s,' \
                       'start_channel=%s,end_channel=%s' %(datapath_id,message_id,ITU_standards,node_id,
                                                           input_port_id,output_port_id,
                                                           start_channel,end_channel))                
                    self.WSS_setup(ITU_standards,datapath_id,message_id,node_id,input_port_id,output_port_id,start_channel,end_channel)
                elif self.belong_to(data) == 'WSS_TEARDOWN_REQUEST':
                    try:
                        assert struct.calcsize(WSS_TEARDOWN_REQUEST_STR) == len(data[8:])
                    except AssertionError as e:
                        logging.critical(e)
                        logging.critical('WSS_TEARDOWN_REQUEST from RYU is not in a correct format')
                        for device in NODETOCONNECTION.values():
                            device.close()
                        sys.exit()
                    (datapath_id,
                     message_id,
                     ITU_standards,
                     node_id,
                     input_port_id,
                     output_port_id,
                     start_channel,
                     end_channel,
                     experiment1,
                     experiment2)=struct.unpack(WSS_TEARDOWN_REQUEST_STR,self.data[8:])
                    logging.info('Receive WSS_TEARDOWN_REQUEST from RYU')
                    logging.debug('  datapath_id=%s,message_id=%s, ' \
                        'ITU_standards=%s,node_id=%s,input_port_id=%s,output_port_id=%s,' \
                       'start_channel=%s,end_channel=%s' %(datapath_id,message_id,ITU_standards,node_id,
                                                           input_port_id,output_port_id,
                                                           start_channel,end_channel))
                    self.WSS_teardown(ITU_standards,datapath_id,message_id,node_id,input_port_id,output_port_id,start_channel,end_channel)
                elif self.belong_to(data) == "GET_OSNR_REQUEST":
                    try:
                        assert struct.calcsize(GET_OSNR_REQUEST_STR) == len(data[8:])
                    except AssertionError as e:
                        logging.critical(e)
                        logging.critical('GET_OSNR_REQUEST from RYU is not in a correct format')
                        for device in NODETOCONNECTION.values():
                            device.close()
                        sys.exit()
                    (datapath_id,
                     message_id,
                     ITU_standards,
                     node_id,
                     port_id,
                     start_channel,
                     end_channel,
                     experiment1,
                     experiment2)=struct.unpack(GET_OSNR_REQUEST_STR,self.data[8:])
                    logging.debug('Recieve GET_OSNR_REQUEST, datapath_id=%s,message_id=%s,' \
                    'ITU_standards=%s,node_id=%s,port_id=%s' \
                    'start_channel=%s,end_channel=%s' %(datapath_id,message_id,ITU_standards,
                                                       node_id,port_id,
                                                       start_channel,end_channel))
                    self.get_OSNR(ITU_standards,datapath_id,message_id,node_id,port_id,start_channel,end_channel)
                        
        except Exception as e:
            logging.critical(e)
            for device in NODETOCONNECTION.values():
                device.close()
            sys.exit()
            
                
    def WSS_setup(self,ITU_standards,datapath_id,message_id,node_id,input_port_id,output_port_id,start_channel,end_channel):
        MID = 100
        if ITU_standards == 2:
            logging.debug('ITU 50GHz grid')
            space = 2
        elif ITU_standards == 3:
            logging.debug('ITU 100GHz grid')
            space = 1
        else:
            logging.warn('ITU grid unspecified')
            space = raw_input('Please specifiy ITU grid (1 for 100G, 2 for 50G..., exit if decide to quit program')
            if space == 'exit':
                for device in NODETOCONNECTION.values():
                    device.close()
                sys.exit()
            else:
                space = int(space)
        try:
            device = NODETOCONNECTION[node_id]
        except KeyError as e:
            logging.critical('node_id:%s does not belong to this agent %s' % (node_id,AGENT_IP))
            for device in NODETOCONNECTION.values():
                device.close()
            sys.exit()
##        inport = portidtoport[node][input_port_id] 
##        outport = portidtoport[node][output_port_id]
        inport = input_port_id #Use virtual mapping
        outport = output_port_id #Use virtual mapping
        result = 0
        if node_id == 1: #First node
            logging.debug('Switch channels on node %s' % node_id)
            logging.debug('Output port is %s' % outport)
            inner_port = 1
            for channel in range(start_channel*space,(end_channel+1)*space,space):
                device.chan_port_switching(channel=channel,port=inner_port,table=0,MID=MID)
                if device.reply[2] == chr(MID) and device.reply[4] == '\x00': #No Error
                    logging.debug('Switching channel %s on sub switch 1:OK' % (channel))
                    result = result | 0  
                else:
                    logging.debug('Switching channel %s on sub switch 1:FAIL' % (channel))
                    result = result | 1
        elif node_id == 2 or node_id == 3:
            logging.debug('Switch channels on node %s' % node_id)
            if outport == 2 and inport == 1:
                logging.debug('Output port is %s' % outport)
                inner_port = 2
                result_sub1 = 0
                for channel in range(start_channel*space,(end_channel+1)*space,space):
                    device.chan_port_switching(channel=channel,port=inner_port,table=0,MID=MID)
                    if device.reply[2] == chr(MID) and device.reply[4] == '\x00': #No Error
                        logging.debug('Switching channel %s on sub switch 1:OK' % (channel))
                        result_sub1 = result_sub1 | 0  
                    else:
                        logging.debug('Switching channel %s on sub switch 1:FAIL' % (channel))
                        result_sub1 = result_sub1 | 1

                result_sub2 = 0
                for channel in range(start_channel*space,(end_channel+1)*space,space):
                    device.chan_port_switching(channel=channel,port=inner_port,table=1,MID=MID)
                    if device.reply[2] == chr(MID) and device.reply[4] == '\x00': #No Error
                        logging.debug('Switching channel %s on sub switch 2:OK' % (channel))
                        result_sub2 = result_sub2 | 0  
                    else:
                        logging.debug('Switching channel %s on sub switch 2:FAIL' % (channel))
                        result_sub2 = result_sub1 | 1                
                result = result_sub1 | result_sub2
        elif node_id == 4:
            logging.debug('Switch channels on node %s' % node_id)
            if outport == 2:
                logging.debug('Output port is %s' % outport)
                inner_port = 1
                result = 0 
                for channel in range(start_channel*space,(end_channel+1)*space,space):
                    device.chan_port_switching(channel=channel,port=inner_port,table=0,MID=MID)
                    if device.reply[2] == chr(MID) and device.reply[4] == '\x00': #No Error
                        logging.debug('Switching channel %s on sub switch 1:OK' % (channel))
                        result = result | 0  
                    else:
                        logging.debug('Switching channel %s on sub switch 1:FAIL' % (channel))
                        result = result | 1
            elif outport == 3:
                logging.debug('Output port is %s' % outport)
                inner_port = 2
                result_sub1 = 0
                for channel in range(start_channel*space,(end_channel+1)*space,space):
                    device.chan_port_switching(channel=channel,port=inner_port,table=0,MID=MID)
                    if device.reply[2] == chr(MID) and device.reply[4] == '\x00': #No Error
                        logging.debug('Switching channel %s on sub switch 1:OK' % (channel))
                        result_sub1 = result_sub1 | 0  
                    else:
                        logging.debug('Switching channel %s on sub switch 1:FAIL' % (channel))
                        result_sub1 = result_sub1 | 1

                result_sub2 = 0
                for channel in range(start_channel*space,(end_channel+1)*space,space):
                    device.chan_port_switching(channel=channel,port=inner_port,table=1,MID=MID)
                    if device.reply[2] == chr(MID) and device.reply[4] == '\x00': #No Error
                        logging.debug('Switching channel %s on sub switch 2:OK' % (channel))
                        result_sub2 = result_sub2 | 0  
                    else:
                        logging.debug('Switching channel %s on sub switch 2:FAIL' % (channel))
                        result_sub2 = result_sub1 | 1                
                result = result_sub1 | result_sub2
                
        elif node_id == 5:
            logging.debug('Switch channels on node %s' % node_id)
            result = 0
            if outport == 2:
                logging.debug('Output port is %s' % outport)
                inner_port = 1
                for channel in range(start_channel*space,(end_channel+1)*space,space):
                    device.chan_port_switching(channel=channel,port=inner_port,table=0,MID=MID)
                    if device.reply[2] == chr(MID) and device.reply[4] == '\x00': #No Error
                        logging.debug('Switching channel %s on sub switch 1:OK' % (channel))
                        result = result | 0  
                    else:
                        logging.debug('Switching channel %s on sub switch 1:FAIL' % (channel))
                        result = result | 1
                
        elif node_id == 6:
            logging.debug('Switch channels on node %s' % node_id)
            result = 0
            if inport == 1 and outport == 3:
                logging.debug('Output port is %s' % outport)
                inner_port = 1
            elif inport == 2 and outport == 3:
                logging.debug('Output port is %s' % outport)
                inner_port = 2
            for channel in range(start_channel*space,(end_channel+1)*space,space):
                device.chan_port_switching(channel=channel,port=inner_port,table=0,MID=MID)
                if device.reply[2] == chr(MID) and device.reply[4] == '\x00': #No Error
                    logging.debug('Switching channel %s on sub switch 1:OK' % (channel))
                    result = result | 0  
                else:
                    logging.debug('Switching channel %s on sub switch 1:FAIL' % (channel))
                    result = result | 1
            
        if result == 0:
            logging.debug('Successfully switch from channel %s to channel %s' % (start_channel*space,end_channel*space))
        elif result == 1:
            logging.debug('Fail to switch from channel %s to channel %s' % (start_channel*space,end_channel*space))
                
        logging.debug('return message_id=%s' % str(message_id))
        WSS_SETUP_REPLY_BODY=struct.pack(WSS_SETUP_REPLY_STR,datapath_id,message_id,result)
        WSS_SETUP_REPLY = ''.join([WSS_SETUP_REPLY_HEADER,WSS_SETUP_REPLY_BODY])
        try:
            assert len(WSS_SETUP_REPLY) == 24
        except AssertionError as e:
            logging.critical(e)
            logging.critical('WSS_TEARDOWN_REPLY is not in a correct format')
            for device in NODETOCONNECTION.values():
                device.close()
            sys.exit()
        self.sock.sendall(WSS_SETUP_REPLY)
        logging.info('WSS_SETUP_REPLY Sent to RYU')

    def WSS_teardown(self,ITU_standards,datapath_id,message_id,node_id,input_port_id,output_port_id,start_channel,end_channel):
        MID = 101
        if ITU_standards == 2:
            logging.debug('ITU 50GHz grid')
            space = 2
        elif ITU_standards == 3:
            logging.debug('ITU 100GHz grid')
            space = 1
        else:
            logging.warn('ITU grid unspecified')
            space = raw_input('Please specifiy ITU grid (1 for 100G, 2 for 50G..., exit if decide to quit program')
            if space == 'exit':
                for device in NODETOCONNECTION.values():
                    device.close()
                sys.exit()
            else:
                space = int(space)
        try:
            device = NODETOCONNECTION[node_id]
        except KeyError as e:
            logging.critical('node_id:%s does not belong to this agent %s' % (node_id,AGENT_IP))
            for device in NODETOCONNECTION.values():
                device.close()
            sys.exit()
##        inport = portidtoport[node][input_port_id] 
##        outport = portidtoport[node][output_port_id]
        inport = input_port_id #Use virtual mapping
        outport = output_port_id #Use virtual mapping
        result = 0
        if node_id == 1: #First node
            logging.debug('Delete channels on node %s' % node_id)
            logging.debug('Output port is %s' % outport)
            for channel in range(start_channel*space,(end_channel+1)*space,space):
                device.chan_port_switching(channel=channel,port=0,table=0,MID=MID)
                if device.reply[2] == chr(MID) and device.reply[4] == '\x00': #No Error
                    logging.debug('Delete channel %s on sub switch 1:OK' % (channel))
                    result = result | 0  
                else:
                    logging.debug('Delete channel %s on sub switch 1:FAIL' % (channel))
                    result = result | 1
        elif node_id == 2 or node_id == 3:
            logging.debug('Delete channels on node %s' % node_id)
            if outport == 2 and inport == 1:
                logging.debug('Output port is %s' % outport)
                result_sub1 = 0
                for channel in range(start_channel*space,(end_channel+1)*space,space):
                    device.chan_port_switching(channel=channel,port=0,table=0,MID=MID)
                    if device.reply[2] == chr(MID) and device.reply[4] == '\x00': #No Error
                        logging.debug('Delete channel %s on sub switch 1:OK' % (channel))
                        result_sub1 = result_sub1 | 0  
                    else:
                        logging.debug('Delete channel %s on sub switch 1:FAIL' % (channel))
                        result_sub1 = result_sub1 | 1

                result_sub2 = 0
                for channel in range(start_channel*space,(end_channel+1)*space,space):
                    device.chan_port_switching(channel=channel,port=0,table=1,MID=MID)
                    if device.reply[2] == chr(MID) and device.reply[4] == '\x00': #No Error
                        logging.debug('Delete channel %s on sub switch 2:OK' % (channel))
                        result_sub2 = result_sub2 | 0  
                    else:
                        logging.debug('Delete channel %s on sub switch 2:FAIL' % (channel))
                        result_sub2 = result_sub1 | 1                
                result = result_sub1 | result_sub2
        elif node_id == 4:
            logging.debug('Delete channels on node %s' % node_id)
            if outport == 2:
                logging.debug('Output port is %s' % outport)
                result = 0 
                for channel in range(start_channel*space,(end_channel+1)*space,space):
                    device.chan_port_switching(channel=channel,port=0,table=0,MID=MID)
                    if device.reply[2] == chr(MID) and device.reply[4] == '\x00': #No Error
                        logging.debug('Delete channel %s on sub switch 1:OK' % (channel))
                        result = result | 0  
                    else:
                        logging.debug('Delete channel %s on sub switch 1:FAIL' % (channel))
                        result = result | 1
            elif outport == 3:
                logging.debug('Output port is %s' % outport)
                result_sub1 = 0
                for channel in range(start_channel*space,(end_channel+1)*space,space):
                    device.chan_port_switching(channel=channel,port=0,table=0,MID=MID)
                    if device.reply[2] == chr(MID) and device.reply[4] == '\x00': #No Error
                        logging.debug('Delete channel %s on sub switch 1:OK' % (channel))
                        result_sub1 = result_sub1 | 0  
                    else:
                        logging.debug('Delete channel %s on sub switch 1:FAIL' % (channel))
                        result_sub1 = result_sub1 | 1

                result_sub2 = 0
                for channel in range(start_channel*space,(end_channel+1)*space,space):
                    device.chan_port_switching(channel=channel,port=0,table=1,MID=MID)
                    if device.reply[2] == chr(MID) and device.reply[4] == '\x00': #No Error
                        logging.debug('Delete channel %s on sub switch 2:OK' % (channel))
                        result_sub2 = result_sub2 | 0  
                    else:
                        logging.debug('Delete channel %s on sub switch 2:FAIL' % (channel))
                        result_sub2 = result_sub1 | 1                
                result = result_sub1 | result_sub2
                
        elif node_id == 5:
            logging.debug('Delete channels on node %s' % node_id)
            result = 0
            if outport == 2:
                logging.debug('Output port is %s' % outport)
                for channel in range(start_channel*space,(end_channel+1)*space,space):
                    device.chan_port_switching(channel=channel,port=0,table=0,MID=MID)
                    if device.reply[2] == chr(MID) and device.reply[4] == '\x00': #No Error
                        logging.debug('Delete channel %s on sub switch 1:OK' % (channel))
                        result = result | 0  
                    else:
                        logging.debug('Delete channel %s on sub switch 1:FAIL' % (channel))
                        result = result | 1
                
        elif node_id == 6:
            logging.debug('Delete channels on node %s' % node_id)
            result = 0
            if inport == 1 and outport == 3:
                logging.debug('Output port is %s' % outport)
            elif inport == 2 and outport == 3:
                logging.debug('Output port is %s' % outport)
            for channel in range(start_channel*space,(end_channel+1)*space,space):
                device.chan_port_switching(channel=channel,port=0,table=0,MID=MID)
                if device.reply[2] == chr(MID) and device.reply[4] == '\x00': #No Error
                    logging.debug('Delete channel %s on sub switch 1:OK' % (channel))
                    result = result | 0  
                else:
                    logging.debug('Delete channel %s on sub switch 1:FAIL' % (channel))
                    result = result | 1
            
        if result == 0:
            logging.debug('Successfully delete from channel %s to channel %s' % (start_channel*space,end_channel*space))
        elif result == 1:
            logging.debug('Fail to delete from channel %s to channel %s' % (start_channel*space,end_channel*space))
                
        logging.debug('return message_id=%s' % str(message_id))
        WSS_TEARDOWN_REPLY_BODY=struct.pack(WSS_TEARDOWN_REPLY_STR,datapath_id,message_id,result)
        WSS_TEARDOWN_REPLY = ''.join([WSS_TEARDOWN_REPLY_HEADER,WSS_TEARDOWN_REPLY_BODY])
        try:
            assert len(WSS_TEARDOWN_REPLY) == 24
        except AssertionError as e:
            logging.critical(e)
            logging.critical('WSS_TEARDOWN_REPLY is not in a correct format')
            for device in NODETOCONNECTION.values():
                device.close()
            sys.exit()
        self.sock.sendall(WSS_TEARDOWN_REPLY)
        logging.info('WSS_TEARDOWN_REPLY Sent to RYU')

    def get_OSNR(self, ITU_standards,datapath_id,message_id,node_id,port_id,start_channel,end_channel):
        MID = 102
        if ITU_standards == 2:
            logging.debug('ITU 50GHz grid')
            space = 2
        elif ITU_standards == 3:
            logging.debug('ITU 100GHz grid')
            space = 1
        else:
            logging.warn('ITU grid unspecified')
            space = raw_input('Please specifiy ITU grid (1 for 100G, 2 for 50G..., exit if decide to quit program')
            if space == 'exit':
                for device in NODETOCONNECTION.values():
                    device.close()
                sys.exit()
            else:
                space = int(space)

        
      
        (monitor_node,monitor_port) = NODEPORTIDTOOMONITOR[(node_id,port_id)]      
        try:
            device = NODETOCONNECTION[monitor_node]
            subswitch_id = monitor_port
        except KeyError as e:
            logging.critical('node_id:%s does not belong to this agent %s' % (node_id,AGENT_IP))
            for device in NODETOCONNECTION.values():
                device.close()
            sys.exit()

        
        result = 0
        OSNR = {}
        for channel in range(start_channel*space,(end_channel+1)*space,space):
            device.per_channel_monitor(channel=channel,table=subswitch_id,MID=MID)
            if device.reply[2] == chr(MID) and device.reply[4] == '\x00':
                power1 = device.chtopower[channel]
                if power1 == -100.0:
                    result = result | 1
                    logging.debug('Check Channel %s sideband power: failed' % (channel))
                else:
                    logging.debug('Check Channel %s power:%s dBm: Success' % (channel,power1))
            else:
                result = result | 1
                logging.debug('Check Channel %s power: failed' % (channel))
##                break

            device.per_channel_monitor(channel=channel-1,table=subswitch_id,MID=MID)
            if device.reply[2] == chr(MID) and device.reply[4] == '\x00':
                power2 = device.chtopower[channel-1]
                if power2 == -100.0:
                    result = result | 1
                    logging.debug('Check Channel %s sideband power: failed' % (channel))
                else:
                    logging.debug('Check Channel %s sideband power:%s dBm: Success' % (channel,power2))
            else:
                result = result | 1
                logging.debug('Check Channel %s sideband power: failed' % (channel))
##                break
            if result == 0:
                osnr = power1 - power2 + 6  #0.1nm noise reference
            else:
                osnr = 'Not measured'
            OSNR[channel] = osnr

        OSNRmin = min(OSNR.values())
        OSNRmin_channel = min(OSNR.iteritems(), key=operator.itemgetter(1))[0]
        logging.debug('OSNR results:%s' % (str(OSNR)))
        logging.info('Worst OSNR is %s at channel %s' % (OSNRmin,OSNRmin_channel))
        if result == 0:
            logging.debug('Successfully monitor OSNR from channel %s to channel %s' % (start_channel*space,end_channel*space))
        elif result == 1:
            logging.debug('Fail to monitor OSNR from channel %s to channel %s' % (start_channel*space,end_channel*space))

            
        OSNR_val= int(OSNRmin*10)
        if OSNR_val < 0:
            OSNR_val = 0
        logging.debug('return message_id=%s' % str(message_id))
        GET_OSNR_REPLY_BODY = struct.pack(GET_OSNR_REPLY_STR,datapath_id,message_id,node_id,result,OSNR_val)
        GET_OSNR_REPLY = ''.join([GET_OSNR_REPLY_HEADER,GET_OSNR_REPLY_BODY])
        try:
            assert len(GET_OSNR_REPLY) == 32
        except AssertionError as e:
            logging.critical(e)
            logging.critical('GET_OSNR_REPLY is not in a correct format')
            for device in NODETOCONNECTION.values():
                device.close()
            sys.exit()
            
        self.sock.sendall(GET_OSNR_REPLY)
        logging.info('GET_OSNR_REPLY Sent to RYU')
                
        
        
        
                              
    def belong_to(self,data):
        if data[1] == 0:
            return "HELLO"
        elif data[1] == 5: #Feture_Request
            return "FEATURE_REQUEST"
        elif data[1] == 116:
            return "WSS_SETUP_REQUEST"
        elif data[1] == 118:
            return "WSS_TEARDOWN_REQUEST"
        elif data[1] == 120:
            return "GET_OSNR_REQUEST"


if __name__=='__main__':
    try:
        connection = TCP_bridge()
        t1 = threading.Thread(target = connection.start)
        t1.daemon = True
        t2 = threading.Thread(target = connection.msg_handler)
        t2.daemon = True
        threads = []
        thread_count = 2
        threads.append(t1)
        threads.append(t2)
        t1.start()
        t2.start()

        while threading.active_count() > 0:
            time.sleep(0.1)

    except KeyboardInterrupt:
        logging.critical('Connection closed, close device connections!')
        for device in NODETOCONNECTION.values():
            device.close()
##
##
##
##    while 1:
##        try:
##            pass
##        except KeyboardInterrupt:
##            logging.critical('Lost connection, close device connections!')
##            for device in NODETOCONNECTION.values():
##                device.close()
##            raise
####            
        



