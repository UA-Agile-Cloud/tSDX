"""
listening to openflow events

Author:   Yao Li (yaoli@optics.arizona.edu.cn)
Created:  2017/01/18
Version:  1.0

Last modifiedby Yao: 2017/01/20

"""

from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
import Common
import Database
import Custom_event

class South_bound_message_receive(app_manager.RyuApp):
    
    _EVENTS =  [Custom_event.South_LSPSetupReplyEvent,
                Custom_event.South_LSPTeardownReplyEvent]
                
    def __init__(self,*args,**kwargs):
        super(South_bound_message_receive,self).__init__(*args,**kwargs)
        self.listening_thread = hub.spawn(self._listening)
    
    def _listening(self):
        pass
        #while True:
            #if there are items in south_timer to be timeout
            #   send timeout reply
            #   delete these timers
            #if there are items in south_timer_no_response to be timeout
            #   delete these timers
            #hub.sleep(1)
            
    @set_ev_cls(OFPT_SETUP_CONFIG_WSS_REPLY)
    def _handle_setup_reply(self,ev):
        #if this message does not have a timer in south_timer and south_timer_no_response
        #   discard this message
        #   print error information
        #else: 
        #   update timer
        #   if all the reply msgs are received in this timer
        #       if this timer in south_timer
        #           send events to other modules based on message type
        #       else:
        #           update lsp information
        #   delete this timer 