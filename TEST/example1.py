import logging
import struct
import threading
import time

from revent import Event,EventMixin
from ryu.base import app_manager
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER,CONFIG_DISPATCHER,DEAD_DISPATCHER,HANDSHAKE_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_4
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import packet_base
import ryu.controller.ofp_handler as handler

import nonryuapp.database as database

class Test(app_manager.RyuApp):
    """A class inherits RyuApp, automatically loaded by RyuApp and can be communicating with other RYU modules

    It sends extension flow mods down to CDPI

    """

    OFP_VERSIONS = [ofproto_v1_4.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        """Call the base RyuApp __init__"""
        super(Test, self).__init__(*args, **kwargs)


    @set_ev_cls(ofp_event.EventOFPTSetupConfigWSSReply,[CONFIG_DISPATCHER,MAIN_DISPATCHER,DEAD_DISPATCHER])
    def handle_WSS_SETUP_CONFIG_REPLY(self,ev):
        msg = ev.msg
        (datapath_id,message_id,result) = (msg.datapath_id,msg.message_id,msg.result)
        try:
            datapath=database.Data.dpid2datapath[datapath_id]
        except:
            print 'Bad things occur......Datapath not found...'
        self.logger.info('RYU get WSS_SETUP_CONFIG_REPLY from agent %s' % datapath_id)
        if result == 0:
            self.logger.info('Successfully established!')
            mod = datapath.ofproto_parser.OFPTGetOSNRRequest(datapath,
                                                            datapath_id=datapath_id,
                                                            message_id=9,
                                                            ITU_standards=2, 
                                                            node_id=1,
                                                            port_id=1, 
                                                            start_channel=3,
                                                            end_channel=3,
                                                            experiment1=0,
                                                            experiment2=0)
            datapath.send_msg(mod)
            self.logger.info('To Measure OSNR, an OSNR request is sent to agent %s' % datapath_id)
        else:
            self.logger.info('Not established due to some unknown errors!')

    @set_ev_cls(ofp_event.EventOFPTTeardownConfigWSSReply,[CONFIG_DISPATCHER,MAIN_DISPATCHER,DEAD_DISPATCHER])
    def handle_WSS_TEARDOWN_CONFIG_REPLY(self,ev):
        msg = ev.msg
        (datapath_id,message_id,result) = (msg.datapath_id,msg.message_id,msg.result)
        try:
            datapath=database.Data.dpid2datapath[datapath_id]
        except:
            print 'Bad things occur......Datapath not found...'
        self.logger.info('RYU get WSS_TEARDOWN_CONFIG_REPLY from agent %s' % datapath_id)
        if result == 0:
            self.logger.info('Successfully deleted!')
        else:
            self.logger.info('Not deleted due to some unknown errors!')


    @set_ev_cls(ofp_event.EventOFPTGetOSNRReply,[CONFIG_DISPATCHER,MAIN_DISPATCHER,DEAD_DISPATCHER])
    def handle_OSNR_REPLY(self,ev):
        OSNR_THRESHOLD = 17
        msg = ev.msg
        (datapath_id,message_id,node_id,result,OSNR) = (msg.datapath_id,msg.message_id,msg.node_id,msg.result,msg.OSNR)
        try:
            datapath=database.Data.dpid2datapath[datapath_id]
        except:
            print 'Bad things occur......Datapath not found...'
        OSNR = round(OSNR/10.0,1)
        self.logger.info('RYU get GET_OSNR_REPLY from agent %s' % datapath_id)
        if result == 0:
            self.logger.info('Measured OSNR is %s' % OSNR) 
            if OSNR<OSNR_THRESHOLD:
                self.logger.info('OSNR below threshold, delete the channel')
                mod = datapath.ofproto_parser.OFPTTeardownConfigWSSRequest(datapath,
                                                            datapath_id=datapath_id,
                                                            message_id=3,
                                                            ITU_standards=2, 
                                                            node_id=1,
                                                            input_port_id=0, 
                                                            output_port_id=1,
                                                            start_channel=3,
                                                            end_channel=3,
                                                            experiment1=0,
                                                            experiment2=0)
                datapath.send_msg(mod)
            else:
                self.logger.info('New channel is accepted')
        else:
            self.logger.info('OSNR not measured due to some unknown errors!')
            
 
            
        
    def action(self, event):
        dpid = 17
        datapath = database.Data.dpid2datapath[dpid]
        mod1 = datapath.ofproto_parser.OFPTSetupConfigWSSRequest(datapath,
                                                        datapath_id=dpid,
                                                        message_id=1,
                                                        ITU_standards=2, 
                                                        node_id=1,
                                                        input_port_id=0, 
                                                        output_port_id=1,
                                                        start_channel=3,
                                                        end_channel=3,
                                                        experiment1=0,
                                                        experiment2=0)                                                                 
        datapath.send_msg(mod1)
        self.logger.info('a WSS Request is sent by RYU')

class Request(Event):
    def __init__(self):
        Event.__init__(self)
#        self.logger.info('Generate a cflow message')

class Events(EventMixin):
     _eventMixin_events = set([Request])
        
aevent = Events()
atest = Test()
aevent.addListenerByName('Request', atest.action)
threading.Timer(10.0,aevent.raiseEvent,(Request,)).start() #After 10 secs, a Cflowmod will be generated and sent out
