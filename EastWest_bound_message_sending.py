"""
EastWest message sending

Author:   Yao Li (yaoli@optics.arizona.edu.cn)
Created:  2017/01/10
Version:  1.0

Last modified by Yao: 2017/01/20

"""

from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls
import Common
import Database
import Custom_event

class EastWest_message_send(app_manager.RyuApp):
    
    _EVENTS =  [Custom_event.EastWest_SendPathCompRequestEvent,
                Custom_event.EastWest_SendPathCompReplyEvent,
                Custom_event.EastWest_SendTrafSetupRequestEvent,
                Custom_event.EastWest_SendTrafSetupReplyEvent,
                Custom_event.EastWest_SendTrafTeardownRequest,
                Custom_event.EastWest_SendTrafTeardownReply,
                Custom_event.EastWest_SendTearDownPath,
                Custom_event.EastWest_SendOSNRMonitoringRequestEvent,
                Custom_event.EastWest_SendOSNRMonitoringReplyEvent]
                
    def __init__(self,*args,**kwargs):
        super(EastWest_message_send,self).__init__(*args,**kwargs)
        
    @set_ev_cls(Custom_event.EastWest_SendPathCompRequestEvent)
    def _handle_send_cross_domain_pc_request(self,ev):
        #send cross-domain path computation request message to next domain
        #if this domain is the source domain:
        #   setup a timer in Database.Data.eastwest_timer
        pass
        
    @set_ev_cls(Custom_event.EastWest_SendPathCompReplyEvent)
    def _handle_send_cross_domain_pc_reply(self,ev):
        #send cross-domain path computation reply message to previous domain
        pass
        
        
    @set_ev_cls(Custom_event.EastWest_SendTrafSetupRequestEvent)
    def _handle_send_cross_domain_setup_request(self,ev):
        #send cross-domain traffic setup request message to next domain
        #if this domain is the source domain:
        #   setup a timer in Database.Data.eastwest_timer
        pass
        
        
    @set_ev_cls(Custom_event.EastWest_SendTrafSetupReplyEvent)
    def _handle_send_cross_domain_setup_reply(self,ev):
        #send cross-domain traffic setup reply message to previous domain
        pass
    
    
    @set_ev_cls(Custom_event.EastWest_SendTrafTeardownRequest)
    def _handle_send_traf_teardown_request(self,ev):
        #send teardown traffic request message to next domain
        #if this domain is the source domain:
        #   setup a timer in Database.Data.eastwest_timer
        pass
        
    @set_ev_cls(Custom_event.EastWest_SendTrafTeardownReply)
    def _handle_send_traf_teardown_reply(self,ev):
        #send teardown traffic reply message to previous domain    
        pass
        
    
    @set_ev_cls(Custom_event.EastWest_SendTearDownPath)
    def _handle_send_teardown_path_request(self,ev):
        #send teardown path message to next domain
        pass
        
    @set_ev_cls(Custom_event.EastWest_SendOSNRMonitoringRequestEvent)
    def _handle_send_cross_domain_OSNR_monitoring_request(self,ev):
        #send OSNR monitoring request message to next domain
        #if this domain is the source domain:
        #   setup a timer in Database.Data.eastwest_timer
        pass
        
    @set_ev_cls(Custom_event.EastWest_SendOSNRMonitoringReplyEvent)
    def _handle_send_cross_domain_OSNR_monitoring_reply(self,ev):
        #send OSNR monitoring repy message to previous domain
        pass