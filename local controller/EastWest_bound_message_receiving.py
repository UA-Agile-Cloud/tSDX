"""
EastWest message receiving

Author:   Yao Li (yaoli@optics.arizona.edu.cn)
Created:  2017/01/19
Version:  1.0

Last modified by Yao: 2017/01/20

"""

from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
import Common
import Database
import Custom_event

class EastWest_message_receive(app_manager.RyuApp):
    
    _EVENTS =  [Custom_event.EastWest_ReceivePathCompRequestEvent,
                Custom_event.EastWest_ReceivePathCompReplyEvent,
                Custom_event.EastWest_ReceiveTrafSetupRequestEvent,
                Custom_event.EastWest_ReceiveTrafSetupReplyEvent,
                Custom_event.EastWest_ReceiveTrafTeardownRequest,
                Custom_event.EastWest_ReceiveTrafTeardownReply,
                Custom_event.EastWest_ReceiveTearDownPath,
                Custom_event.EastWest_ReceiveOSNRMonitoringRequestEvent,
                Custom_event.EastWest_ReceiveOSNRMonitoringReplyEvent]
                
    def __init__(self,*args,**kwargs):
        super(EastWest_message_receive,self).__init__(*args,**kwargs)
        self.listening_thread = hub.spawn(self._listening)
        
    def _listening(self):
        pass
        #while True:
            #receive a message
            #if this message does not have a timer in Database.Data.eastwest_timer
            #   discard this message
            #   print error information
            #else: 
            #   send events to other modules based on message type
            #   delete this timer 
            #if there are items in Database.Data.eastwest_timer to be timeout
            #   send timeout reply
            #   delete these timers
            #hub.sleep(1)
            
