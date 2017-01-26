"""
Intra-domain connection control

Author:   Yao Li (yaoli@optics.arizona.edu.cn)
Created:  2017/01/09
Version:  1.0

Last modified by Yao: 2017/01/20

"""

import sys
from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls
import Common
import Database
import Custom_event

class Intra_domain_connection_ctrl(app_manager.RyuApp):
    
    _EVENTS =  [Custom_event.North_IntraDomainTrafficRequestEvent,
                Custom_event.North_IntraDomainTrafficTeardownRequestEvent,
                Custom_event.North_TrafficStateUpdateEvent,
                Custom_event.North_TrafficReplyEvent,
                Custom_event.North_TrafficTeardownReplyEvent,
                Custom_event.IntraDomainPathCompRequestEvent,
                Custom_event.IntraDomainPathCompReplyEvent,
                Custom_event.South_LSPSetupRequestEvent,
                Custom_event.South_LSPSetupReplyEvent,
                Custom_event.South_OSNRMonitoringRequest,
                Custom_event.South_OSNRMonitoringReply,
                Custom_event.IntraDomainReroutingRequest,
                Custom_event.IntraDomainReroutingReply,
                Custom_event.EastWest_ReceiveTearDownPath]
                
    def __init__(self,*args,**kwargs):
        super(Intra_domain_connection_ctrl, self).__init__(*args,**kwargs)
                    
    @set_ev_cls(Custom_event.North_IntraDomainTrafficRequestEvent)
    def _handle_intra_domain_traffic_request(self,ev):
        if (Database.Data.traf_list.insert_new_traf(ev) == False):   #insert new traffic information to database
            self.logger.info('Insert traffic to database error!')
        intra_domain_traffic_pc_ev = Custom_event.IntraDomainPathCompRequestEvent()   # send custom event to trigger traffic setup
        intra_domain_traffic_pc_ev.traf_id = ev.traf_id
        self.send_event('Path_computation',intra_domain_traffic_pc_ev)

    @set_ev_cls(Custom_event.IntraDomainPathCompReplyEvent)
    def _handle_intra_domain_pc_reply(self,ev):
        pass
        #if SUCCESS: 
        #   update traffic state: Database.Data.traf_list.update_traf_state(ev.traf_id, TRAFFIC_PATH_COMPUTATION_SUCCESS) 
        #   send Custom_event.South_LSPSetupRequestEvent to 'Intra_domain_connection_ctrl'
        #elif FAIL:
        #   update traffic state: Database.Data.traf_list.update_traf_state(ev.traf_id, TRAFFIC_PATH_COMPUTATION_FAIL) 
        #   send Custom_event.North_TrafficReplyEvent to 'North_bound_message_send'
        #   delete traffic and lsp information in database
        #else:
        #   error
    

    @set_ev_cls(Custom_event.South_LSPSetupRequestEvent)
    def _handle_lsp_setup_request(self,ev):
        """Intra-domain lightpath setup 
        """
        pass
        #update Phy_topo
        #for all the unprovisioned lsps with lsp.traf_id == ev.traf_id
        #   send OFPT_SETUP_CONFIG_WSS_REQUEST message
        #setup a timer in south_timer
        
    @set_ev_cls(Custom_event.South_LSPSetupReplyEvent)
    def _handle_lsp_setup_reply(self,ev):
        pass
        #lsp is working or protection:
        #if SUCCESS:
        #   update traffic state to TRAFFIC_SETUP_SUCCESS
        #   update lsp state to LSP_SETUP_SUCCESS in database
        #   send Custom_event.North_TrafficReplyEvent to 'North_bound_message_send'
        #   send Custom event.South_OSNRMonitoringRequest to 'Monitoring'
        #elif FAIL:
        #   update traffic state to TRAFFIC_SETUP_FAIL
        #   update lsp state to LSP_SETUP_FAIL in database
        #   send Custom_event.North_TrafficReplyEvent to 'North_bound_message_send'
        #   delete traffic and lsp information in database, update Phy_topo
        #lsp is rerouting:
        #if SUCCESS:
        #   update traffic state to TRAFFIC_INTRA_DOMAIN_REROUTE_SUCCESS
        #   update rerouting lsp state to LSP_SETUP_SUCCESS in database
        #   send Custom_event.North_TrafficStateUpdateEvent to 'North_bound_message_send'
        #   send Custom_event.South_OSNRMonitoringRequest to 'Monitoring'
        #   tear down old lsp
        #elif FAIL:
        #   update traffic state to TRAFFIC_INTRA_DOMAIN_REROUTE_FAIL
        #   update rerouting lsp state to LSP_SETUP_FAIL in database
        #   send Custom_event.North_TrafficReplyEvent to 'North_bound_message_send'
        #   tear down old lsp
        #   update Phy_topo
        
    @set_ev_cls(Custom_event.South_OSNRMonitoringReply)
    def _handle_OSNR_monitoring_reply(self,ev):
        pass
        #if result is not SUCCESS:
        #   error
        #else:
        #   if is_OSNR_all_good == True
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
        #           send Custom_event.North_TrafficStateUpdateEvent to 'North_bound_message_send'
        #   else: 
        #       update traffic state to TRAFFIC_INACTIVE
        #       send Custom_event.North_TrafficStateUpdateEvent to 'North_bound_message_send'
        #   traffic on rerouting path:
        #   if impairment at this domain
        #       update traffic state to TRAFFIC_INACTIVE
        #       send Custom_event.North_TrafficStateUpdateEvent to 'North_bound_message_send'
        #   else: 
        #       update traffic state to TRAFFIC_INACTIVE
        #       send Custom_event.North_TrafficStateUpdateEvent to 'North_bound_message_send'
        
    @set_ev_cls(Custom_event.IntraDomainReroutingReply)
    def _handle_intra_domain_rerouting_reply(self,ev):
        pass
        #if SUCCESS:
        #   update traf_state to TRAFFIC_INTRA_DOMAIN_REROUTE_SUCCESS
        #   send Custom_event.South_LSPSetupRequestEvent to 'Intra_domain_connection_ctrl'
        #elif FAIL:
        #   traffic is intra_domain:
        #   update traf_state to TRAFFIC_INTRA_DOMAIN_REROUTE_FAIL 
        #   send Custom_event.North_TrafficReplyEvent to 'North_bound_message_send'
        #   delete traffic and lsp information in database
        #else:
        #   error         
        
    @set_ev_cls(Custom_event.South_LSPTeardownRequestEvent)
    def _handle_lsp_teardown_request(self,ev):
        """Intra-domain lightpath teardown 
        """
        pass
        #for all the provisioned lsps with lsp.traf_id == ev.traf_id
        #   send OFPT_TEARDOWN_CONFIG_WSS_REQUEST message
        #setup a timer in south_timer
        
    @set_ev_cls(Custom_event.South_LSPTeardownReplyEvent)
    def _handle_lsp_teardown_reply(self,ev):
        pass
        #if SUCCESS:
        #   update traffic state to TRAFFIC_TEARDOWN_SUCCESS
        #else:
        #   update traffic state to TRAFFIC_TEARDOWN_FAIL
        #recover Phy_topo  
        #if traffic is intra-domain:
        #   if this teardown is launched by central controller:
        #       send Custom_event.North_TrafficTeardownReplyEvent to 'North_bound_message_send'
        #   else:
        #       send Custom_event.North_TrafficStateUpdateEvent to 'North_bound_message_send'
        #   delete traffic, lsp informations
        #else:
        #   if this domain is the destination domain:
        #       send Custom_event.EastWest_SendTeardownTrafficReply to 'EastWest_message_send'
        #       delete traffic, lsp informations
        
        
    @set_ev_cls(Custom_event.EastWest_ReceiveTearDownPath)
    def _handle_receive_teardown_path_request(self,ev): 
        """teardown specified lsp(s) of a traffic 
        """
        pass
        #for lsps need to be teardown:
        #   send OFPT_TEARDOWN_CONFIG_WSS_REQUEST messages to agent 
        #setup a time in south_timer_no_response
        
    @set_ev_cls(Custom_event.North_IntraDomainTrafficTeardownRequestEvent)
    def _handle_intra_domain_traffic_teardown_request(self,ev):   
        pass
        #setup a timer
        #send Custom_event.South_LSPTeardownRequestEvent to 'Intra_domain_connection_ctrl'
        
    #@set_ev_cls(Custom_event.EastWest_TearDownPathReply)
   #     """reply of teardown specified lsp(s) of a traffic 
   #     """
   # def _handle_teardown_path_reply(self,ev): 
   #     #
   
    