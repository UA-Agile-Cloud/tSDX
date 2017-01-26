"""
Handle physical layer monitoring

Author:   Yao Li (yaoli@optics.arizona.edu.cn)
Created:  2017/01/09
Version:  1.0

Last modified by Yao: 2017/01/20

"""

from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls
import Common
import Database
import Custom_event

class Monitoring(app_manager.RyuApp):
    
    _EVENTS =  [Custom_event.South_OSNRMonitoringRequest,
                Custom_event.South_OSNRMonitoringReply]
                
    def __init__(self,*args,**kwargs):
        super(Monitoring, self).__init__(*args,**kwargs)
        
    @set_ev_cls(Custom_event.South_OSNRMonitoringRequest)
    def _handle_OSNR_monitoring_request(self,ev):
        pass
        #send OFPT_GET_OSNR_REQUEST to agent
        #setup a timer in south_timer
        
    @set_ev_cls(OFPT_GET_OSNR_REPLY)
    def _handle_OSNR_monitoring_reply(self,ev):
        pass
        #receive OFPT_GET_OSNR_REPLY
        #if cannot find a timer in south_timer:
        #   print error information
        #else:
        #   record monitored OSNR in Database
        #   update timer
        #   if all the replies are received:
        #       delete this timer
        #       if traf is intra-domain:
        #           send Custom_event.South_OSNRMonitoringReply to 'Intra_domain_connection_ctrl'
        #       else:
        #           send Custom_event.South_OSNRMonitoringReply to 'Cross_domain_connection_ctrl'
