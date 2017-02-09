"""build a single threaded CDPI

"""
import socket
import time
import sys
import array
import threading
import random
import struct

#OFPT_CHELLO = 80
HELLO = bytearray('\x05\x00\x00\x10\x00\x00\x00\x2c\x00\x02\x00\x08\x00\x00\x00\x10')
FEATURE_REPLY = bytearray('\x05\x06\x00\x20\x15\xa7\xe7\x34\x00\x00\x00\x00\x00\x00\x00\x11\x00\x00\x01\x00\xfe\x00\x00\x00\xff\x00\x00\xff\x00\x00\x00\x00')
assert len(FEATURE_REPLY) == 32
WSS_SETUP_REPLY_HEADER = '\x05\x75\x00\x18\x00\x00\x00\x00'
assert len(WSS_SETUP_REPLY_HEADER) == 8
WSS_TEARDOWN_REPLY_HEADER = '\x05\x77\x00\x18\x00\x00\x00\x00'
assert len(WSS_TEARDOWN_REPLY_HEADER) == 8
GET_OSNR_REPLY_HEADER = '\x05\x79\x00\x20\x00\x00\x00\x00'
assert len(GET_OSNR_REPLY_HEADER) == 8

#TCP_IP = '192.168.56.1'
TCP_IP = '127.0.0.1'
TCP_PORT = 6633

WSS_SETUP_REQUEST_STR = '!QIIIIIIIII'
WSS_SETUP_REPLY_STR = '!QII'
WSS_TEARDOWN_REQUEST_STR = '!QIIIIIIIII'
WSS_TEARDOWN_REPLY_STR = '!QII'
GET_OSNR_REQUEST_STR = '!QIIIIIIII'
GET_OSNR_REPLY_STR = '!QIIII'

class CDPI(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = (TCP_IP,TCP_PORT)
        self.sock.connect(self.connection)
        print >>sys.stderr, 'connecting to the controller:%s port %s' % self.connection

    def send_cecho(self):
        threading.Timer(40.0, self.send_cecho).start()
        self.sock.send(CECHO_REQUEST)

    def start(self):
        try:
            while(1):
                hello_count = 0 
                self.data = self.sock.recv(100)
                self.data = [ord(c) for c in self.data]
                #print self.data
                self.data = bytearray(self.data)
                if self.belong_to() == 'HELLO':
                    print "Receive Hello Request"
                    self.sock.sendall(HELLO)
                    hello_count +=1
                    print 'Hello Reply Sent'
                elif self.belong_to() == 'FEATURE_REQUEST':
                    print "Receive FEATURE_REQUEST"
                    self.sock.sendall(FEATURE_REPLY)
                    print 'FEATURE_REPLY SENT'
                elif self.belong_to() == "WSS_SETUP_REQUEST":
                    assert struct.calcsize(WSS_SETUP_REQUEST_STR) == len(self.data[8:])
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
                    print "Recieve WSS_SETUP_REQUEST, datapath_id=%s,message_id=%s, " \
                    "ITU_standards=%s,node_id=%s,input_port_id=%s,output_port_id=%s" \
                   " start_channel=%s,end_channel=%s" %(datapath_id,message_id,ITU_standards,node_id,
                                                       input_port_id,output_port_id,
                                                       start_channel,end_channel)
                    result = 0
                    WSS_SETUP_REPLY_BODY=struct.pack(WSS_SETUP_REPLY_STR,datapath_id,message_id,result)
                    WSS_SETUP_REPLY = ''.join([WSS_SETUP_REPLY_HEADER,WSS_SETUP_REPLY_BODY])
                    assert len(WSS_SETUP_REPLY) == 24
                    self.sock.sendall(WSS_SETUP_REPLY)
                    print 'WSS_SETUP_REPLY Sent to RYU'
                elif self.belong_to() == "WSS_TEARDOWN_REQUEST":
                    assert struct.calcsize(WSS_TEARDOWN_REQUEST_STR) == len(self.data[8:])
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
                    print "Recieve WSS_TEARDOWN_REQUEST, datapath_id=%s,message_id=%s, " \
                    "ITU_standards=%s,node_id=%s,input_port_id=%s,output_port_id=%s" \
                   " start_channel=%s,end_channel=%s" %(datapath_id,message_id,ITU_standards,node_id,
                                                       input_port_id,output_port_id,
                                                       start_channel,end_channel)
                    result = 0
                    WSS_TEARDOWN_REPLY_BODY=struct.pack(WSS_TEARDOWN_REPLY_STR,datapath_id,message_id,result)
                    WSS_TEARDOWN_REPLY = ''.join([WSS_TEARDOWN_REPLY_HEADER,WSS_TEARDOWN_REPLY_BODY])
                    assert len(WSS_TEARDOWN_REPLY) == 24
                    self.sock.sendall(WSS_TEARDOWN_REPLY)
                    print 'WSS_TEARDOWN_REPLY Sent to RYU'
                    
                elif self.belong_to() == "GET_OSNR_REQUEST":
                    assert struct.calcsize(GET_OSNR_REQUEST_STR) == len(self.data[8:])
                    (datapath_id,
                     message_id,
                     ITU_standards,
                     node_id,
                     port_id,
                     start_channel,
                     end_channel,
                     experiment1,
                     experiment2)=struct.unpack(GET_OSNR_REQUEST_STR,self.data[8:])
                    print "Recieve GET_OSNR_REQUEST, datapath_id=%s,message_id=%s, " \
                    "ITU_standards=%s,node_id=%s,port_id=%s" \
                   " start_channel=%s,end_channel=%s" %(datapath_id,message_id,ITU_standards,
                                                       node_id, port_id,
                                                       start_channel,end_channel)
                    result = 0
                    OSNR = random.randrange(150,200)
                    GET_OSNR_REPLY_BODY = struct.pack(GET_OSNR_REPLY_STR,datapath_id,message_id,node_id,result,OSNR)
                    GET_OSNR_REPLY = ''.join([GET_OSNR_REPLY_HEADER,GET_OSNR_REPLY_BODY])
                    assert len(GET_OSNR_REPLY) == 32
                    self.sock.sendall(GET_OSNR_REPLY)
                    print 'GET_OSNR_REPLY Sent to RYU'

        except Exception as e:
            print e
        finally:
            self.sock.close()
            
    def belong_to(self):
        if self.data[1] == 0:
            return "HELLO"
        elif self.data[1] == 5: #Feture_Request
            return "FEATURE_REQUEST"
        elif self.data[1] == 116:
            return "WSS_SETUP_REQUEST"
        elif self.data[1] == 118:
            return "WSS_TEARDOWN_REQUEST"
        elif self.data[1] == 120:
            return "GET_OSNR_REQUEST"
    


newcdpi = CDPI()
newcdpi.start()

         



        

