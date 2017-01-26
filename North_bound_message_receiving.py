"""
Generate events after receiving north-bound messages 

Author:   Yao Li (yaoli@optics.arizona.edu.cn)
Created:  2017/01/16
Version:  1.0

Last modified by Yao: 2017/01/20

"""

from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
import Common
import Database
import Custom_event

class North_bound_message_receive(app_manager.RyuApp):
    
    _EVENTS =  [Custom_event.North_CrossDomainTrafficRequestEvent,
                Custom_event.North_IntraDomainTrafficRequestEvent,
                Custom_event.North_IntraDomainTrafficTeardownRequestEvent,
                Custom_event.North_CrossDomainTrafficTeardownRequestEvent]
                
    def __init__(self,*args,**kwargs):
        super(North_bound_message_receive,self).__init__(*args,**kwargs)
        self.listening_thread = hub.spawn(self._listening)
        
    def _listening(self):
        pass
        #while True:
            #receive a message
            #setup a timer in north_timer
            #send events to other modules based on message type
            #if there are items in north_timer to be timeout:
            #   send timeout reply
            #   delete these timers
            #hub.sleep(1)
        
            