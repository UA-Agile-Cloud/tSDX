"""
send north-bound messages 

Author:   Yao Li (yaoli@optics.arizona.edu.cn)
Created:  2017/01/18
Version:  1.0

Last modified by Yao: 2017/01/20

"""

from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls
import Common
import Database
import Custom_event

class North_bound_message_send(app_manager.RyuApp):
    
    _EVENTS =  [Custom_event.North_TrafficReplyEvent,
                Custom_event.North_TrafficTeardownReplyEvent,
                Custom_event.North_TrafficStateUpdateEvent]
                
    def __init__(self,*args,**kwargs):
        super(North_bound_message_send,self).__init__(*args,**kwargs)
        
    @set_ev_cls(Custom_event.North_TrafficReplyEvent)
    def _handle_traffic_reply(self,ev):
        pass
        #if cannot find a timer of this reply:
        #   print error information
        #else:
        #send reply message
        #delete this timer
        
        
    @set_ev_cls(Custom_event.North_TrafficTeardownReplyEvent)
    def _handle_traffic_teardown_reply(self,ev):
        pass
        #if cannot find a timer of this reply:
        #   print error information
        #else:
        #send reply message
        #delete this timer
        
    @set_ev_cls(Custom_event.North_TrafficStateUpdateEvent)
    def _handle_traffic_state_update(self,ev):
        pass
        #if cannot find a timer of this reply:
        #   print error information
        #else:
        #send reply message
        #delete this timer

            