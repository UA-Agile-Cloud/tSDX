# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 14:15:39 2017

@author: Weiyang.M
"""

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


"""This will be a virtual agent for OPM detection of both domains
The physical IP address sits same with agent 1, which is 192.168.1.100
It will have two virtual clients which connect to two ryu controllers
Controller 1: 192.168.1.0, Controller 2: 192.168.2.0
"""

AGENT_IP = '192.168.1.100'
(RYU_IP1,PORT1,datapath_id1) = ('192.168.1.0',6633,chr(19))
(RYU_IP2,PORT2,datapath_id2) = ('192.168.2.0',6633,chr(20))   

nodeid = 7
NODETOCONNECTION ={}
#NODETOCONNECTION[nodeid] =  Nistica('com2')
NODETOCONNECTION[nodeid] = 1


        
HELLO = bytearray('\x05\x00\x00\x10\x00\x00\x00\x2c\x00\x02\x00\x08\x00\x00\x00\x10')
FEATURE_REPLY1 = '\x05\x06\x00\x20\x15\xa7\xe7\x34\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\xfe\x00\x00\x00\xff\x00\x00\xff\x00\x00\x00\x00'
FEATURE_REPLY1 = list(FEATURE_REPLY1)
FEATURE_REPLY1[15] = datapath_id1
FEATURE_REPLY1 = ''.join(FEATURE_REPLY1)
assert len(FEATURE_REPLY1) == 32
FEATURE_REPLY2 = '\x05\x06\x00\x20\x15\xa7\xe7\x34\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\xfe\x00\x00\x00\xff\x00\x00\xff\x00\x00\x00\x00'
FEATURE_REPLY2 = list(FEATURE_REPLY2)
FEATURE_REPLY2[15] = datapath_id2
FEATURE_REPLY2 = ''.join(FEATURE_REPLY2)
assert len(FEATURE_REPLY2) == 32
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
    def __init__(self,RYU_IP,RYU_PORT,datapath_id):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = (RYU_IP,RYU_PORT)
        self.datapath_id = datapath_id
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
                    if self.datapath_id == chr(19):
                        self.sock.sendall(FEATURE_REPLY1)
                    elif self.datapath_id == chr(20):
                        self.sock.sendall(FEATURE_REPLY2)
                    logging.info('FEATURE_REPLY SENT')
                    logging.info('---------------------------------------')
                elif self.belong_to(data) == 'WSS_SETUP_REQUEST':
                   pass
                elif self.belong_to(data) == 'WSS_TEARDOWN_REQUEST':
                   pass
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
#        MID = 100
        pass

    def WSS_teardown(self,ITU_standards,datapath_id,message_id,node_id,input_port_id,output_port_id,start_channel,end_channel):
#        MID = 101
        pass

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

        
      
#        (monitor_node,monitor_port) = NODEPORTIDTOOMONITOR[(node_id,port_id)]  
        (monitor_node,monitor_port) = (7,0)    
        try:
            device = NODETOCONNECTION[monitor_node]
            subswitch_id = monitor_port
        except KeyError as e:
            logging.critical('node_id:%s does not belong to this agent %s' % (node_id,AGENT_IP))
            for device in NODETOCONNECTION.values():
                device.close()
            sys.exit()

        
        #Now measure OSNR using OPM
        #OPM BLOCK
                
        
        
        
                              
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
        connection1 = TCP_bridge(RYU_IP1,PORT1,datapath_id1)
        connection2 = TCP_bridge(RYU_IP2,PORT2,datapath_id2)
        t1 = threading.Thread(target = connection1.start)
        t1.daemon = True
        t2 = threading.Thread(target = connection1.msg_handler)
        t2.daemon = True
        t3 = threading.Thread(target = connection2.start)
        t3.daemon = True
        t4 = threading.Thread(target = connection2.msg_handler)
        t4.daemon = True
        threads = []
        thread_count = 4
        threads.append(t1)
        threads.append(t2)
        threads.append(t3)
        threads.append(t4)
        t1.start()
        t2.start()
        t3.start()
        t4.start()

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