"""
Inter-domain connection control

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
import logging
from Common import log_level

logging.basicConfig(level = log_level)

class Cross_domain_connection_ctrl(app_manager.RyuApp):
    
    _EVENTS =  [Custom_event.North_CrossDomainTrafficRequestEvent,
                Custom_event.North_CrossDomainTrafficTeardownRequestEvent,
                Custom_event.North_TrafficReplyEvent,
                Custom_event.North_TrafficTeardownReplyEvent,
                Custom_event.North_TrafficStateUpdateEvent,
                Custom_event.CrossDomainPathCompRequestEvent,
                Custom_event.CrossDomainPathCompReplyEvent,
                Custom_event.CrossDomainReroutingRequestEvent,
                Custom_event.CrossDomainReroutingReplyEvent,
                Custom_event.EastWest_SendTrafSetupRequestEvent,
                Custom_event.EastWest_ReceiveTrafSetupRequestEvent,
                Custom_event.EastWest_SendTrafSetupReplyEvent,
                Custom_event.EastWest_ReceiveTrafSetupReplyEvent,
                Custom_event.EastWest_SendTrafTeardownRequest,
                Custom_event.EastWest_ReceiveTrafTeardownRequest,
                Custom_event.EastWest_SendTrafTeardownReply,
                Custom_event.EastWest_ReceiveTrafTeardownReply,
                Custom_event.EastWest_SendTearDownPath,
                Custom_event.EastWest_ReceiveTearDownPath,
                Custom_event.EastWest_SendOSNRMonitoringRequestEvent,
                Custom_event.EastWest_ReceiveOSNRMonitoringRequestEvent,
                Custom_event.EastWest_SendOSNRMonitoringReplyEvent,
                Custom_event.EastWest_ReceiveOSNRMonitoringReplyEvent,
                Custom_event.South_LSPSetupRequestEvent,
                Custom_event.South_LSPSetupReplyEvent,
                Custom_event.South_OSNRMonitoringRequest,
                Custom_event.South_OSNRMonitoringReply,
                Custom_event.IntraDomainReroutingRequest,
                Custom_event.IntraDomainReroutingReply]
                
    def __init__(self,*args,**kwargs):
        super(Cross_domain_connection_ctrl,self).__init__(*args,**kwargs)
        
    @set_ev_cls(Custom_event.North_CrossDomainTrafficRequestEvent)
    def _handle_cross_domain_traffic_request(self,ev):
        if (Database.Data.traf_list.insert_new_traf(ev) == False):   #insert new traffic information to database
            self.logger.info('Insert traffic to database error!')
        if (controller_list.is_src_domain(ev.domain_sequence[0]) == False):      # this domain is not the source domian
            self.logger.info('This domain is not the source domain of cross-domain traffic %d. Waiting'%ev.traf_id)
            return
        else:     # this domain is the source domain
            cross_domain_traffic_pc_ev = Custom_event.CrossDomainPathCompRequestEvent()   # send custom event to trigger traffic setup
            cross_domain_traffic_pc_ev.traf_id = ev.traf_id
            self.send_event('Path_computation',cross_domain_traffic_pc_ev)
        
    @set_ev_cls(Custom_event.CrossDomainPathCompReplyEvent)
    def _handle_cross_domain_pc_reply(self,ev):
        pass
        #if SUCCESS:
        #   update traffic state to TRAFFIC_SETUP
        #   send Custom_event.South_LSPSetupRequestEvent to 'Intra_domain_connection_ctrl'
        #elif FAIL:
        #   send Custom_event.North_TrafficReplyEvent to 'North_bound_message_send'
        #   send Custom_event.EastWest_SendTrafTeardownRequest to 'EastWest_message_send'
        #else:
        #   error

    @set_ev_cls(Custom_event.South_LSPSetupReplyEvent)
    def _handle_lsp_setup_reply(self,ev):
        pass
        #if SUCCESS: 
        #   update lsp state to LSP_SETUP_SUCCESS in database
        #   if this domain is the source domain:
        #       send Custom_event.EastWest_SendTrafSetupRequestEvent to 'EastWest_message_send'
        #       setup a timer
        #   elif this domain is the destination domain:
        #       update traffic state to TRAFFIC_SETUP_SUCCESS
        #       send Custom_event.EastWest_SendTrafSetupReplyEvent to 'EastWest_message_send'
        #   else:
        #       send Custom_event.EastWest_SendTrafSetupRequestEvent to 'EastWest_message_send'
        #elif FAIL:  
        #   update lsp state to LSP_SETUP_FAIL in database
        #   update traffic state to TRAFFIC_SETUP_FAIL
        #   if this domain is the source domain:     
        #       send Custom_event.North_TrafficReplyEvent to 'North_bound_message_send'
        #       send Custom_event.EastWest_SendTrafTeardownRequest to 'EastWest_message_send'
        #       send Custom_event.South_LSPTeardownRequestEvent to 'Intra_domain_connection_ctrl'
        #   else:
        #       send Custom_event.EastWest_SendTrafSetupReplyEvent to 'EastWest_message_send'
        #       send Custom_event.South_LSPTeardownRequestEvent to 'Intra_domain_connection_ctrl'
        
        
    @set_ev_cls(Custom_event.EastWest_ReceiveTrafSetupRequestEvent)
    def _handle_receive_traffic_setup_request(self,ev): 
        pass
        #if ev.traf_stage is right
        #   update traffic state to TRAFFIC_SETUP
        #   send Custom_event.South_LSPSetupReplyEvent to 'Intra_domain_connection_ctrl'
        
    
    @set_ev_cls(Custom_event.EastWest_ReceiveTrafSetupReplyEvent)
    def _handle_receive_traffic_setup_reply(self,ev): 
        pass
        #update traffic state to ev.traf_state
        #if this domain is not the source domain:
        #   send Custom_event.EastWest_SendTrafSetupReplyEvent to 'EastWest_message_send'
        #else:
        #   send Custom_event.North_TrafficReplyEvent to 'North_bound_message_send'
        #   if ev.traf_state == TRAFFIC_SETUP_FAIL
        #       send Custom_event.EastWest_SendTrafTeardownRequest to 'EastWest_message_send'
        #       send Custom_event.South_LSPTeardownRequestEvent to 'Intra_domain_connection_ctrl'
        #   elif ev.traf_state == TRAFFIC_SETUP_SUCCESS:
        #       if ev.traf_stage is TRAFFIC_WORKING:
        #           send Custom_event.South_OSNRMonitoringRequest to 'Monitoring'
        #       elif ev.traf_stage is TRAFFIC_REROUTING:
        #           send Custom_event.EastWest_SendTearDownPath to 'EastWest_message_send' to teardown working(backup) path
        #           send Custom_event.South_OSNRMonitoringRequest to 'Monitoring'
        #       else:
        #           error
        #   else:
        #       error
        
    @set_ev_cls(Custom_event.South_OSNRMonitoringReply)
    def _handle_OSNR_monitoring_reply(self,ev):
        pass
        #if ev.result is not SUCCESS:
        #   if this domain is not the source domain:
        #       send EastWest_SendOSNRMonitoringReplyEvent to 'EastWest_message_send' 
        #   else:
        #       print OSNR monitoring error or timeout
        #else:
        #   if is_OSNR_all_good == True:
        #       if this domain is not the destination domain:
        #           send EastWest_SendOSNRMonitoringRequestEvent to 'EastWest_message_send' 
        #       else:
        #           send EastWest_SendOSNRMonitoringReplyEvent to 'EastWest_message_send' 
        #       return
        #   traffic on working path:
        #   if impairment at this domain
        #       if traffic protection type is TRAFFIC_REROUTING_RESTORATION:
        #           update traf_state to TRAFFIC_INTRA_DOMAIN_REROUTE
        #           update traff_stage to TRAFFIC_REROUTING
        #           send Custom_event.IntraDomainReroutingRequest to Path_computation
        #       elif traffic protection type is TRAFFIC_1PLUS1_PROTECTION
        #           switch to backup path
        #           update traf_state to TRAFFIC_ON_BACKUP_PATH:
        #           send Custom_event.North_TrafficStateUpdateEvent to 'North_bound_message_send'
        #           trigger backup path OSNR monitering
        #       elif traffic protection type is TRAFFIC_NO_PROTECTION:
        #           update traffic state to TRAFFIC_INACTIVE
        #           if this domain is the source domain:
        #               send Custom_event.North_TrafficStateUpdateEvent to 'North_bound_message_send'
        #           else:
        #               send EastWest_SendOSNRMonitoringReplyEvent to 'EastWest_message_send' 
        #   else: 
        #       send EastWest_SendOSNRMonitoringRequestEvent to 'EastWest_message_send' (is_is_inter_domain_impairment == True)
        #   traffic on rerouting path:
        #   update traffic state to TRAFFIC_INACTIVE
        #   if this domain is the source domain:
        #       send Custom_event.North_TrafficStateUpdateEvent to 'North_bound_message_send'
        #   else:
        #       send EastWest_SendOSNRMonitoringReplyEvent to 'EastWest_message_send' 
        
    @set_ev_cls(Custom_event.EastWest_ReceiveOSNRMonitoringRequestEvent)
    def _handle_cross_domain_OSNR_monitoring_request(self,ev):
        pass
        #send Custom_event.South_OSNRMonitoringRequest to 'Monitoring'
        
    @set_ev_cls(Custom_event.EastWest_ReceiveOSNRMonitoringReplyEvent)
    def _handle_cross_domain_OSNR_monitoring_reply(self,ev):
        pass
        #if ev.result == SUCCESS
        #   if traffic stage at this domain is TRAFFIC_REROUTING
        #       update ev.traf_stage and ev.traf_state as those at this domain
        #if this domain is not the source domain:
        #   send EastWest_SendOSNRMonitoringReplyEvent to 'EastWest_message_send' 
        #else:
        #   if ev.result != SUCCESS
        #       print OSNR monitoring error or timeout
        #   else:
        #       if ev.is_inter_domain_impairment == True and ev.traf_stage != TRAFFIC_REROUTING
        #           send Custom_event.CrossDomainReroutingRequestEvent to 'Path_computation'
        #       else:
        #           update traffic stage and state
        #           send Custom_event.North_TrafficStateUpdateEvent to 'North_bound_message_send'
        #           send Custom_event.EastWest_SendTrafTeardownRequest to 'EastWest_message_send' if necessary
        
    
    @set_ev_cls(Custom_event.IntraDomainReroutingReply)
    def _handle_intra_domain_rerouting_reply(self,ev):
        pass
        #if SUCCESS:
        #   update traf_state to TRAFFIC_INTRA_DOMAIN_REROUTE_SUCCESS
        #   send Custom_event.South_LSPSetupRequestEvent to 'Intra_domain_connection_ctrl'
        #elif FAIL:
        #   update traf_state to TRAFFIC_INTRA_DOMAIN_REROUTE_FAIL 
        #   if this domain is the source domain:
        #       send Custom_event.North_TrafficStateUpdateEvent to 'North_bound_message_send'
        #       send Custom_event.EastWest_SendTrafTeardownRequest to 'EastWest_message_send'
        #   else:
        #       send EastWest_SendOSNRMonitoringReplyEvent to 'EastWest_message_send'
        #else:
        #   error   
    
    
    @set_ev_cls(Custom_event.CrossDomainReroutingReplyEvent)
    def _handle_cross_domain_rerouting_reply(self,ev):
        pass
        #if result is SUCCESS:
        #   update traffic state to TRAFFIC_SETUP
        #   send Custom_event.South_LSPSetupRequestEvent to 'Intra_domain_connection_ctrl'
        #elif FAIL:
        #   send Custom_event.North_TrafficReplyEvent to 'North_bound_message_send'
        #   send Custom_event.EastWest_SendTrafTeardownRequest to 'EastWest_message_send'
        #else:
        #   error 
        
        
    @set_ev_cls(Custom_event.EastWest_ReceiveTrafTeardownRequest)
    def _handle_receive_traffic_teardown_request(self,ev): 
        pass
        #if this domain is not the destination domain:
        #   send Custom_event.EastWest_SendTrafTeardownRequest to 'EastWest_message_send'
        #   send Custom_event.South_LSPTeardownRequestEvent to 'Intra_domain_connection_ctrl'
        
    @set_ev_cls(Custom_event.EastWest_ReceiveTrafTeardownReply)
    def _handle_receive_traffic_teardown_reply(self,ev): 
        pass
        #if traffic state at this domain is TRAFFIC_TEARDOWN_FAIL
        #   update ev.result to be FAIL
        #if this domain is not the source domain:
        #   send Custom_event.EastWest_SendTrafTeardownReply to 'EastWest_message_send'
        #else:
        #   if this teardown is launched by central controller:
        #       send Custom_event.North_TrafficTeardownReplyEvent to 'North_bound_message_send'
        #   else:
        #       send Custom_event.North_TrafficStateUpdateEvent to 'North_bound_message_send'
        #delete traffic, lsp informations
    
    
    @set_ev_cls(Custom_event.EastWest_ReceiveTearDownPath)
    def _handle_receive_teardown_path_request(self,ev): 
        pass
        #if this domain is not the destination domain:
        #   send Custom_event.EastWest_SendTearDownPath to 'EastWest_message_send'
        #send Custom_event.EastWest_ReceiveTearDownPath to 'Intra_domain_connection_ctrl'
              
    @set_ev_cls(Custom_event.North_CrossDomainTrafficTeardownRequestEvent)
    def _handle_cross_domain_traffic_teardown_request(self,ev):
        pass
        #if this domain is the source domain:
        #   send Custom_event.EastWest_SendTrafTeardownRequest to 'EastWest_message_send'
        #   send Custom_event.South_LSPTeardownRequestEvent to 'Intra_domain_connection_ctrl'
        #else:
        #   do nothing
        

    