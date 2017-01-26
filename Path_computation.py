"""
Intra_domain path computation 

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

class Path_computation(app_manager.RyuApp):
    
    _EVENTS =  [Custom_event.IntraDomainPathCompRequestEvent,
                Custom_event.IntraDomainPathCompReplyEvent,
                Custom_event.CrossDomainPathCompRequestEvent,
                Custom_event.CrossDomainPathCompReplyEvent,
                Custom_event.CrossDomainReroutingRequestEvent,
                Custom_event.CrossDomainReroutingReplyEvent,
                Custom_event.EastWest_SendPathCompRequestEvent,
                Custom_event.EastWest_ReceivePathCompRequestEvent,
                Custom_event.EastWest_SendPathCompReplyEvent,
                Custom_event.EastWest_ReceivePathCompReplyEvent,
                Custom_event.IntraDomainReroutingRequest,
                Custom_event.IntraDomainReroutingReply]
                
    def __init__(self,*args,**kwargs):
        super(Path_computation, self).__init__(*args,**kwargs)

    @set_ev_cls(Custom_event.IntraDomainPathCompRequestEvent)
    def _handle_intra_domain_traffic_pc_request(self,ev): 
        """Path computation of a intra-domain traffic
        """
        Database.Data.traf_list.update_traf_state(ev.traf_id, TRAFFIC_PATH_COMPUTATION)     # update traffic state to path_computation
        traf = Database.Data.traf_list.find_traf_by_id(ev.traf_id)
        if (traf == None):
            self.logger.info('Can not find traf_id in database! (intra_domain_path_domputation)')
            return
        if (traf.prot_type == TRAFFIC_NO_PROTECTION or traf.prot_type == TRAFFIC_REROUTING_RESTORATION): 
            source_node_id = Database.Data.phy_topo.get_node_id_by_ip(traf.src_node_ip)
            destination_node_id = Database.Data.phy_topo.get_node_id_by_ip(traf.dst_node_ip)
            path = self.routing(source_node_id, None, destination_node_id, traf.bw_demand)    #routing. calculate one path
            if (path == []):
                    Database.Data.traf_list.update_traf_state(traf.traf_id, TRAFFIC_PATH_COMPUTATION_FAIL) 
                    pc_reply_ev = Custom_event.IntraDomainPathCompReplyEvent()
                    pc_reply_ev.traf_id = ev.traf_id
                    pc_reply_ev.result = FAIL
                    self.send_event('Intra_domain_connection_ctrl',pc_reply_ev)
                    # delete traffic information
            else:
                comm_avai_chnl = path[2]
                resources = self.rsc_allocation(comm_avai_chnl, traf.bw_demand)
                if (Database.Data.lsp_list.insert_new_lsp(path, resources) == False):
                    self.logger.info('Insert unprovisioned lsp error!')
                    sys.exit(1);
                else:
                    Database.Data.traf_list.update_traf_state(traf.traf_id, TRAFFIC_PATH_COMPUTATION_SUCCESS) 
                    pc_reply_ev = Custom_event.IntraDomainPathCompReplyEvent()
                    pc_reply_ev.traf_id = ev.traf_id
                    pc_reply_ev.result = SUCCESS
                    self.send_event('Intra_domain_connection_ctrl',pc_reply_ev)
        elif (ev.prot_type == TRAFFIC_1PLUS1_PROTECTION):
            pass
        else:
            self.logger.info('Protection type error! Protection type = %d' % ev.prot_type)


    @set_ev_cls(Custom_event.CrossDomainPathCompRequestEvent)
    def _handle_cross_domain_traffic_pc_request(self,ev): 
        """Path computation of a cross-domain traffic at its source domain
        """
        Database.Data.traf_list.update_traf_state(ev.traf_id, TRAFFIC_PATH_COMPUTATION)     # update traffic state to path_computation
        traf = Database.Data.traf_list.find_traf_by_id(ev.traf_id)
        if (traf == None):
            self.logger.info('Can not find traf_id in database! (cross_domain_path_domputation_at_src_domain)')
            return
        if (traf.prot_type == TRAFFIC_NO_PROTECTION or traf.prot_type == TRAFFIC_REROUTING_RESTORATION): 
            source_node_id = Database.Data.phy_topo.get_node_id_by_ip(traf.src_node_ip)
            destination_node_id = Database.Data.phy_topo.get_out_node_id(traf.domain_sequence[1])
            path = self.routing(source_node_id, None, destination_node_id, traf.bw_demand)    #routing. calculate one path
            if (path == []):
                Database.Data.traf_list.update_traf_state(ev.traf_id, TRAFFIC_PATH_COMPUTATION_FAIL)
                # send reply message to central controller
                # delete traffic information
            else:
                Database.Data.intra_domain_path_list.insert_a_new_path(path)    #record the result of routing
                entry_of_next_domain = Database.Data.find_entry_of_next_domain(ev.traf_id)  # find entry of next domain
                cross_domain_pc_ev = Custom_event.EastWest_sendPathCompRequestEvent()   # send custom event to EastWest-bound interface
                cross_domain_pc_ev.traf_id = ev.traf_id
                cross_domain_pc_ev.entry_of_next_domain = entry_of_next_domain
                self.send_event('EastWest_message_send',cross_domain_pc_ev)
                #setup a timer for cross-domain path computation
        elif (traf.prot_type == TRAFFIC_1PLUS1_PROTECTION):
            pass
        else:
            self.logger.info('Protection type error! Protection type = %d' % ev.prot_type)

    @set_ev_cls(Custom_event.EastWest_ReceivePathCompRequestEvent)
    def _handle_cross_domain_pc_request(self,ev):
        """path computation at domains (which are not the source domain) of a cross-domain traffic
        """
        pass
        #if (traf.prot_type == TRAFFIC_1PLUS1_PROTECTION):
        #   pass
        #if ev.route_type == ROUTE_REROUTE:
        #   update traffic stage to TRAFFIC_REROUTING in database
        #path computation in this domain
        #if SUCCESS:
        #   if this domain is not the destination domain:
        #       send Custom_event.EastWest_SendPathCompRequestEvent to 'EastWest_message_send'
        #   else:
        #       do resource allocation, update Database.Data.lsp_list
        #       update traffic state in database (TRAFFIC_PATH_COMPUTATION_SUCCESS)
        #       send Custom_event.EastWest_SendPathCompReplyEvent to 'EastWest_message_send'
        #else:
        #   update traffic state in database (TRAFFIC_PATH_COMPUTATION_FAIL)
        #   send Custom_event.EastWest_SendPathCompReplyEvent to 'EastWest_message_send'
        
    @set_ev_cls(Custom_event.EastWest_ReceivePathCompReplyEvent)
    def _handle_cross_domain_pc_reply(self,ev):
        """handle cross-domain path computation reply 
        """
        pass
        #if (traf.prot_type == TRAFFIC_1PLUS1_PROTECTION):
        #   pass
        #if ev.result == SUCCESS:
        #   do resource allocation, update Database.Data.lsp_list
        #   update traffic state to TRAFFIC_PATH_COMPUTATION_SUCCESS in database
        #else:
        #   update traffic state to TRAFFIC_PATH_COMPUTATION_FAIL in database  
        #if this domain is not the source domain:       
        #   send Custom_event.EastWest_SendPathCompReplyEvent to 'EastWest_message_send'
        #else:
        #   if ev.route_type == ROUTE_REROUTE:
        #       send Custom_event.CrossDomainReroutingReplyEvent to 'Cross_domain_connection_ctrl'
        #   else:
        #       send Custom_event.CrossDomainPathCompReplyEvent to 'Cross_domain_connection_ctrl'
            

    @set_ev_cls(Custom_event.IntraDomainReroutingRequest)
    def _handle_intra_domain_rerouting_request(self,ev): 
        pass
        #rerouting
        #if SUCCESS:
        #   insert a new LSP to lsp_list
        #if traffic is intra-domain:
        #   send Custom_event.IntraDomainReroutingReply to 'Intra_domain_connection_ctrl'
        #elif traffic is cross-domain:
        #   send Custom_event.IntraDomainReroutingReply to 'Cross_domain_connection_ctrl'
        #else:
        #   error
        
    @set_ev_cls(Custom_event.CrossDomainReroutingRequestEvent)
    def _handle_cross_domain_rerouting_request(self,ev):
        pass
        #update traffic stage to TRAFFIC_REROUTING
        #reroute at this first domain
        #if SUCCESS:
        #   update traffic state to TRAFFIC_PATH_COMPUTATION
        #   send Custom_event.EastWest_SendPathCompRequestEvent to 'EastWest_message_send'
        #else:
        #   update traffic stage to TRAFFIC_PATH_COMPUTATION_FAIL
        #   send Custom_event.CrossDomainReroutingReplyEvent to 'Cross_domain_connection_ctrl'
        
        
        
    def routing(self, source_node_id, src_port_id, destination_node_id, bw_demand):
        """input: src_node_id, src_port_id, dst_node_id, bw_demand
           output: [traf_id, route_type, cost, route(a list of node_id), common_avai_chnl]. if fail, return []
        """
        pass
        #return a_path
    
    def rsc_allocation(self, comm_avai_chnl, bw_demand):
        """input: comm_avai_chnl(a list), bw_demand
           output: resources (a list)
        """
        pass
        #return a_list
    
        
        
    