"""
Intra_domain path computation 

Author:   Yao Li (yaoli@optics.arizona.edu.cn)
          Yiwen Shen (ys2799@columbia.edu)
Created:  2017/01/09
Version:  1.0

Last modified by Yao: 2017/02/15

"""

from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls
import time
from Common import *
import Database
import Custom_event
import logging
from rwa_core import *
from Common import log_level

logging.basicConfig(level = log_level)

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
                #Database.Data.traf_list.update_traf_state(traf.traf_id, TRAFFIC_PATH_COMPUTATION_FAIL) 
                pc_reply_ev = Custom_event.IntraDomainPathCompReplyEvent()
                pc_reply_ev.traf_id = ev.traf_id
                pc_reply_ev.result = FAIL
                self.send_event('Intra_domain_connection_ctrl',pc_reply_ev)
                # delete traffic information
            else:
                comm_avai_chnl = path[2]
                resources = self.rsc_allocation(comm_avai_chnl, traf.bw_demand)
                if (Database.Data.insert_new_lsp(path, resources) == False):
                    self.logger.info('Insert unprovisioned lsp error!')
                    sys.exit(1);
                else:
                    #Database.Data.traf_list.update_traf_state(traf.traf_id, TRAFFIC_PATH_COMPUTATION_SUCCESS) 
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
        self.logger.debug('Path_computation module receives CrossDomainPathCompRequestEvent')
        Database.Data.traf_list.update_traf_state(ev.traf_id, TRAFFIC_PATH_COMPUTATION)     # update traffic state to path_computation
        traf = Database.Data.traf_list.find_traf_by_id(ev.traf_id)
        if (traf == None):
            self.logger.critical('Can not find traf_id in database! (cross_domain_path_domputation_at_src_domain)')
            return
        if (traf.prot_type == TRAFFIC_NO_PROTECTION or traf.prot_type == TRAFFIC_REROUTING_RESTORATION): 
            source_node_id = Database.Data.phy_topo.get_node_id_by_ip(traf.src_node_ip)
            destination_node_id = Database.Data.phy_topo.get_out_node_id(traf.domain_sequence[1])
            if destination_node_id == None:
                self.logger.critical('Cannot find a interlink. (Path_computation: _handle_cross_domain_traffic_pc_request)')
                return
            #path = self.routing(source_node_id, None, destination_node_id, traf.bw_demand)    #routing. calculate one path

            # from Yiwen
            src_node_ip = traf.src_node_ip
            src_port_id = Database.Data.phy_topo.get_port_id(src_node_ip)
            edge_node_ip = Database.Data.phy_topo.get_edge_node_ip()
            edge_node_id = Database.Data.phy_topo.get_edge_node_id()
            self.logger.info ("Begin path computation in source domain from source node {0} to edge node {1}".format(src_node_ip, edge_node_ip))
            topo = Database.Data.phy_topo.get_topo()
         
            nlambda = 3
            paths = self.routing(str(ev.traf_id), topo, nlambda, src_node_ip, src_port_id, edge_node_ip, traf.bw_dmd)    #routing. calculate one path
            # from Yiwen end
            
            # tmp routing. for temp use only
            path = list()
            #path[0] = ev.traf_id
            #path[1] = ROUTE_WORKING
            #path[2] = 0
            #path[3] = [['192.168.1.1',1,2],['192.168.1.2',1,2],['192.168.1.3'],1,2]
            #path[4] = [30]
            path.append(ev.traf_id)
            path.append(ROUTE_WORKING)
            path.append(0)
            path.append([['192.168.1.1',1,2],['192.168.1.2',1,2],['192.168.1.3',1,2]])
            path.append([15])
            #Database.Data.intra_domain_path_list.insert_a_new_path(path)
            # tmp routing end
            
            if (path == []):
                #Database.Data.traf_list.update_traf_state(ev.traf_id, TRAFFIC_PATH_COMPUTATION_FAIL)
                # send pc reply event to Cross_domain_connection_ctrl
                pc_reply_ev = Custom_event.CrossDomainPathCompReplyEvent()
                pc_reply_ev.traf_id = traf.traf_id
                pc_reply_ev.result = FAIL
                self.send_event('Cross_domain_connection_ctrl', pc_reply_ev)
            else:
                Database.Data.intra_domain_path_list.insert_a_new_path(path)    #record the result of routing
                #entry_of_next_domain = Database.Data.find_entry_of_next_domain(ev.traf_id)  # find entry of next domain
                entry_of_next_domain = []
                cross_domain_pc_ev = Custom_event.EastWest_SendPathCompRequestEvent()
                cross_domain_pc_ev.traf_id = ev.traf_id
                cross_domain_pc_ev.route_type = ROUTE_WORKING
                cross_domain_pc_ev.entry_of_next_domain = entry_of_next_domain
                self.send_event('EastWest_message_send',cross_domain_pc_ev)
                #setup a timer for cross-domain path computation. Moved to EastWest_message_send
                #new_timer = Timer()
                #new_timer.traf_id = ev.traf_id
                #new_timer.timer_type = TIMER_PATH_COMPUTATION
                #new_timer.end_time = time.time() + EASTWEST_WAITING_TIME
                #eastwest_timer.append(new_timer)
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
        # for temp use only
        self.logger.debug('Path_computation module receives EastWest_ReceivePathCompRequestEvent')
        if ev.route_type == ROUTE_REROUTE:
            Database.Data.traf_list.update_traf_stage(ev.traf_id, TRAFFIC_REROUTING) 
        traf = Database.Data.traf_list.find_traf_by_id(ev.traf_id)
        if traf == None:
            self.logger.critical('Cannot find traffic %d. (Path_computation: _handle_cross_domain_pc_request)' % ev.traf_id)
            return

        tmp_time = time.time()
        # from Yiwen
        if (traf.prot_type == TRAFFIC_1PLUS1_PROTECTION):
           pass
        if ev.route_type == ROUTE_REROUTE:
        #   update traffic stage to TRAFFIC_REROUTING in database
            pass

        #path computation in this domain

        if (traf.prot_type == TRAFFIC_NO_PROTECTION or traf.prot_type == TRAFFIC_REROUTING_RESTORATION):
            self.logger.info ("Inside TRAFFIC_NO_PROTECTION regime")

            # First perform path computation to get 3 paths, and see which wavelengths are available
            src_node_ip = '192.168.2.1'
            src_port_id = Database.Data.phy_topo.get_port_id(src_node_ip)
            dst_node_ip = traf.dst_node_ip
            dst_node_id = Database.Data.phy_topo.get_node_id_by_ip(dst_node_ip)
            self.logger.info ("Begin path computation in destination domain from source node {0} to node {1}".format(src_node_ip, dst_node_ip))
            topo = Database.Data.phy_topo.get_topo()
            #print("Destination domain topology = ", topo)

            path = self.routing(str(ev.traf_id), topo, 3, src_node_ip, src_port_id, dst_node_ip, traf.bw_dmd)
            #print (path)
            if Database.Data.controller_list.this_controller.domain_id != 2:
                pass
            else:
                if (path == []):
                    self.logger.info ("Path not found")
                    #Database.Data.traf_list.update_traf_state(ev.traf_id, TRAFFIC_PATH_COMPUTATION_FAIL)
                    # send reply message to central controller
                    # delete traffic information
                else:
                    self.logger.info ("Path found!\nIntra domain path (destination domain) = {0}".format(', '.join(map(str, path))))

                    # Find the possible wavelengths from source and dest domains
                    wavelengths_from_src=[]
                    #for i in range(0, len(ev.entry_of_next_domain)):
                        #wavelengths_from_src.append(ev.entry_of_next_domain[i][1])
                    wavelengths_from_dst=path[4]
                    self.logger.info("Possible wavelengths from source domain: {0}".format(', '.join(map(str, wavelengths_from_src))))
                    self.logger.info("Possible wavelengths from destination domain: {0}".format(', '.join(map(str, wavelengths_from_dst))))

                    # Choose lowest wavelength common to both domains
                    common_wavelengths = list(set(wavelengths_from_src) & set(wavelengths_from_dst))
                    if not common_wavelengths:
                        self.logger.info("No common wavelengths found!")
                        #Database.Data.traf_list.update_traf_state(ev.traf_id, TRAFFIC_PATH_COMPUTATION_FAIL)
                        # send reply to central controller
                    #lowest_wavelength = common_wavelengths[0]
                    #index_of_lowest_wavelength = wavelengths_from_dst.index(lowest_wavelength)

                    # Use the lowest wavelength to find the path corresponding to that wavelength
                    #chosen_path = [path[0], path[1], path[2], path[3][index_of_lowest_wavelength], path[4][0]]
                    #self.logger.info("Chosen path: {0}".format(', '.join(map(str, chosen_path))))
                    #Database.Data.intra_domain_path_list.insert_a_new_path(chosen_path)    #record the result of routing
        # from Yiwen end'''
        self.logger.info('Testing! Path computation time = %s' % str(time.time() - tmp_time))

        #for temp use only
        if Database.Data.controller_list.is_this_domain(traf.domain_sequence[0]) != True:
            path = list()
            resources = None
            if ev.route_type == ROUTE_WORKING:
                #path[0] = ev.traf_id
                #path[1] = ev.route_type
                #path[2] = 0
                #path[3] = [['192.168.2.1',1,2],['192.168.2.3',1,3]]
                #path[4] = [30]
                path.append(ev.traf_id)
                path.append(ev.route_type)
                path.append(0)
                path.append([['192.168.2.1',1,2],['192.168.2.3',1,3]])
                path.append([15])
                Database.Data.intra_domain_path_list.insert_a_new_path(path)
                resources = [15]
            elif ev.route_type == ROUTE_REROUTE:
                #path[0] = ev.traf_id
                #path[1] = ev.route_type
                #path[2] = 0
                #path[3] = [['192.168.2.1',1,3],['192.168.2.2',1,2],['192.168.2.3',2,3]]
                #path[4] = [60]
                path.append(ev.traf_id)
                path.append(ev.route_type)
                path.append(0)
                path.append([['192.168.2.1',1,2],['192.168.2.3',1,3]])
                #path.append([['192.168.2.1',1,3],['192.168.2.2',1,2],['192.168.2.3',2,3]])
                path.append([30])
                Database.Data.intra_domain_path_list.insert_a_new_path(path)
                resources = [30]
            else:
                self.logger.info('Wrong route type. (Path_computation: _handle_cross_domain_pc_request)')
            path = Database.Data.intra_domain_path_list.find_a_path(ev.traf_id, ev.route_type)
            if path == None:
                self.logger.critical('Cannot intra-domain path for traffic %d.' % ev.traf_id)
                return
            Database.Data.insert_new_lsp(path, resources)
            Database.Data.intra_domain_path_list.pop_a_path(ev.traf_id, ev.route_type)
            Database.Data.traf_list.update_traf_state(ev.traf_id, TRAFFIC_PATH_COMPUTATION_SUCCESS) 
            pc_reply_ev = Custom_event.EastWest_SendPathCompReplyEvent()
            pc_reply_ev.traf_id = ev.traf_id
            pc_reply_ev.route_type = ev.route_type
            pc_reply_ev.result = SUCCESS
            pc_reply_ev.resource_allocation = list(resources)
            self.send_event('EastWest_message_send', pc_reply_ev)
        else:
            self.logger,info('Error! This domain is the source domain. (Path_computation: _handle_cross_domain_pc_request)')
        # for temp use only end
        
                
     
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
        # for tmp use onlys
        self.logger.debug('Path_computation module receives EastWest_ReceivePathCompReplyEvent')
        if ev.result == SUCCESS:
            traf = Database.Data.traf_list.find_traf_by_id(ev.traf_id)
            path = Database.Data.intra_domain_path_list.find_a_path(ev.traf_id, ev.route_type)
            if path == None:
                self.logger.critical('Cannot intra-domain path for traffic %d.' % ev.traf_id)
                return
            Database.Data.insert_new_lsp(path, ev.resource_allocation)
            Database.Data.intra_domain_path_list.pop_a_path(ev.traf_id, ev.route_type)
            Database.Data.traf_list.update_traf_state(ev.traf_id, TRAFFIC_PATH_COMPUTATION_SUCCESS) 
            if Database.Data.controller_list.is_this_domain(traf.domain_sequence[0]) != True:
                pc_reply_ev = Custom_event.EastWest_SendPathCompReplyEvent()
                pc_reply_ev.traf_id = ev.traf_id
                pc_reply_ev.route_type = ev.route_type
                pc_reply_ev.result = SUCCESS
                pc_reply_ev.resource_allocation = list(ev.resource_allocation)
                self.send_event('EastWest_message_send', pc_reply_ev)
            else:
                if ev.route_type == ROUTE_REROUTE:
                    rerouing_reply_ev = Custom_event.CrossDomainReroutingReplyEvent()
                    rerouing_reply_ev.traf_id = ev.traf_id
                    rerouing_reply_ev.result = SUCCESS
                    self.send_event('Cross_domain_connection_ctrl', rerouing_reply_ev)
                else:
                    pc_reply_ev = Custom_event.CrossDomainPathCompReplyEvent()
                    pc_reply_ev.traf_id = ev.traf_id
                    pc_reply_ev.result = SUCCESS
                    self.send_event('Cross_domain_connection_ctrl', pc_reply_ev)
        elif ev.result == FAIL: #need to be completed 
            self.logger.info('EastWest_ReceivePathCompReplyEvent result == FAIL')
        else:   #need to be completed 
            self.logger.info('EastWest_ReceivePathCompReplyEvent result == TIMEOUT')
            

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
        self.logger.debug('Path_computation module receives IntraDomainReroutingRequest')
        traf = Database.Data.traf_list.find_traf_by_id(ev.traf_id)
        if traf == None:
            self.logger.critcal('Cannot find traffic %d. (Path_computation: _handle_intra_domain_rerouting_request)' % ev.traf_id)
            return

        # from Yiwen
        if Database.Data.controller_list.is_this_domain(traf.domain_sequence[0]) == True:
            src_node_ip = traf.src_node_ip
            src_port_id = Database.Data.phy_topo.get_port_id(src_node_ip)
            edge_node_ip = Database.Data.phy_topo.get_edge_node_ip()
            edge_node_id = Database.Data.phy_topo.get_edge_node_id()
        else:
            src_node_ip = Database.Data.phy_topo.get_edge_node_ip()
            src_port_id = Database.Data.phy_topo.get_edge_node_id()
            edge_node_ip = traf.dst_node_ip
            edge_node_id = Database.Data.phy_topo.get_port_id(edge_node_ip)
            self.logger.info ("Begin path computation in source domain from source node {0} to edge node {1}".format(src_node_ip, edge_node_ip))
            topo = Database.Data.phy_topo.get_topo()
               
            nlambda = 3
            paths = self.routing(str(ev.traf_id), topo, nlambda, src_node_ip, src_port_id, edge_node_ip, traf.bw_dmd)    #routing. calculate one path
        # from Yiwen end'''

        path = list()
        if Database.Data.controller_list.is_this_domain(traf.domain_sequence[0]) == True:
            path = []
        else:
            #path[0] = ev.traf_id
            #path[1] = ROUTE_INTRA_REROUTE
            #path[2] = 0
            #path[3] = [['192.168.2.1',1,3],['192.168.2.2',1,2],['192.168.2.3',2,3]]
            #path[4] = [30]
            path.append(ev.traf_id)
            path.append(ROUTE_INTRA_REROUTE)
            path.append(0)
            path.append([['192.168.2.1',1,3],['192.168.2.2',1,2],['192.168.2.3',2,3]])
            path.append([15])
            resources = [15]
        Database.Data.intra_domain_path_list.insert_a_new_path(path)
        path = Database.Data.intra_domain_path_list.find_a_path(ev.traf_id, ROUTE_INTRA_REROUTE)
        Database.Data.insert_new_lsp(path, resources)
        rerouting_reply_ev = Custom_event.IntraDomainReroutingReply()
        rerouting_reply_ev.traf_id = ev.traf_id
        if path != []:
            rerouting_reply_ev.result = SUCCESS
        else:
            rerouting_reply_ev.result = FAIL
        traf = Database.Data.traf_list.find_traf_by_id(ev.traf_id)
        if traf.traf_type == TRAFFIC_INTRA_DOMAIN:
            self.send_event('Intra_domain_connection_ctrl', rerouting_reply_ev)
        elif traf.traf_type == TRAFFIC_CROSS_DOMAIN:
            self.send_event('Cross_domain_connection_ctrl', rerouting_reply_ev)
        else:
            self.logger.info('Invalid traffic type! (Path_computation: _handle_intra_domain_rerouting_request)')
            
        
    @set_ev_cls(Custom_event.CrossDomainReroutingRequestEvent)
    def _handle_cross_domain_rerouting_request(self,ev):
        pass
        #update traffic stage to TRAFFIC_REROUTING
        #reroute at this first domain
        #if SUCCESS:
        #   update traffic state to TRAFFIC_PATH_COMPUTATION
        #   send Custom_event.EastWest_SendPathCompRequestEvent to 'EastWest_message_send'
        #else:
        #   update traffic state to TRAFFIC_PATH_COMPUTATION_FAIL
        #   send Custom_event.CrossDomainReroutingReplyEvent to 'Cross_domain_connection_ctrl'

        # from Yiwen
        traf = Database.Data.traf_list.find_traf_by_id(ev.traf_id)
        if (traf == None):
            self.logger.critical('Can not find traf_id in database! (cross_domain_path_domputation_at_src_domain)')
            return
        if (traf.prot_type == TRAFFIC_NO_PROTECTION or traf.prot_type == TRAFFIC_REROUTING_RESTORATION): 
            source_node_id = Database.Data.phy_topo.get_node_id_by_ip(traf.src_node_ip)
            destination_node_id = Database.Data.phy_topo.get_out_node_id(traf.domain_sequence[1])

            if destination_node_id == None:
                self.logger.critical('Cannot find a interlink. (Path_computation: _handle_cross_domain_traffic_pc_request)')
                return
            #path = self.routing(source_node_id, None, destination_node_id, traf.bw_demand)    #routing. calculate one path

            src_node_ip = traf.src_node_ip
            src_port_id = Database.Data.phy_topo.get_port_id(src_node_ip)
            edge_node_ip = Database.Data.phy_topo.get_edge_node_ip()
            edge_node_id = Database.Data.phy_topo.get_edge_node_id()
            self.logger.info ("Begin path computation in source domain from source node {0} to edge node {1}".format(src_node_ip, edge_node_ip))
            topo = Database.Data.phy_topo.get_topo()
           
            nlambda = 3
            paths = self.routing(str(ev.traf_id), topo, nlambda, src_node_ip, src_port_id, edge_node_ip, traf.bw_dmd)    #routing. calculate one path
        # from Yiwen end'''

        Database.Data.traf_list.update_traf_stage(ev.traf_id, TRAFFIC_REROUTING)
        path = list()
        #path[0] = ev.traf_id
        #path[1] = ROUTE_REROUTE
        #path[2] = 0
        #path[3] = [['192.168.1.1',1,2],['192.168.1.2',1,2],['192.168.1.3'],1,2]
        #path[4] = [60]
        path.append(ev.traf_id)
        path.append(ROUTE_REROUTE)
        path.append(0)
        path.append([['192.168.1.1',1,2],['192.168.1.2',1,2],['192.168.1.3',1,2]])
        path.append([30])
        Database.Data.intra_domain_path_list.insert_a_new_path(path)
        if path != []:
            Database.Data.traf_list.update_traf_state(ev.traf_id, TRAFFIC_PATH_COMPUTATION)
            #entry_of_next_domain = Database.Data.find_entry_of_next_domain(ev.traf_id)  # find entry of next domain
            entry_of_next_domain = []
            pc_req_ev = Custom_event.EastWest_SendPathCompRequestEvent()
            pc_req_ev.traf_id = ev.traf_id
            pc_req_ev.route_type = ROUTE_REROUTE
            pc_req_ev.entry_of_next_domain = entry_of_next_domain
            self.send_event('EastWest_message_send',pc_req_ev)
            #setup a timer for cross-domain path computation. Moved to EastWest_message_send 
            #new_timer = Timer()
            #new_timer.traf_id = ev.traf_id
            #new_timer.timer_type = TIMER_PATH_COMPUTATION
            #new_timer.end_time = time.time() + EASTWEST_WAITING_TIME
            #eastwest_timer.append(new_timer)
        else:
            Database.Data.traf_list.update_traf_state(ev.traf_id, TRAFFIC_PATH_COMPUTATION_FAIL)
            rerouing_replt_ev = Custom_event.CrossDomainReroutingReplyEvent()
            rerouing_replt_ev.traf_id = ev.traf_id
            rerouing_replt_ev.result = FAIL
            self.send_event('Cross_domain_connection_ctrl', rerouing_replt_ev)
    
        
        
    #def routing(self, source_node_id, src_port_id, destination_node_id, bw_demand):
        """input: src_node_id, src_port_id, dst_node_id, bw_demand
           output: (traf_id, route_type, cost, route(a tuple of (node_ip, add_port_id, drop_port_id)), common_avai_chnl). if fail, return None
        """
        #pass

    def routing(self, traf_id, topo, nlambda, src_node_ip, src_port_id, edge_node_ip, bw_demand):
        """input: src_node_id, src_port_id, dst_node_id, bw_demand
           output: [traf_id, route_type, cost, route(a list of node_id), common_avai_chnl]. if fail, return []
        """
        #self.logger.info (traf_id, topo, nlambda, src_node_ip, edge_node_ip)
        computed_path = path_wav_compute(traf_id, topo, nlambda, src_node_ip, edge_node_ip)
        #print (computed_path)

        routes=[]
        wavelengths=[]
        for i in range(len(computed_path)):
            routes.append(computed_path[i][0])
            wavelengths.append(computed_path[i][1])

        # translate ips to ids in computed path
        #for i in range(0, len(computed_path[0])):
        #    route.append(Database.Data.phy_topo.get_node_id_by_ip(computed_path[0][i]))
        

        return [traf_id, ROUTE_WORKING, 0, routes, wavelengths]
    
    def rsc_allocation(self, comm_avai_chnl, bw_demand):
        """input: comm_avai_chnl(a list), bw_demand
           output: resources (a list)
        """
        pass
        #return a_list
    
        
        
    
