"""
Routing and wavelength assignment
Routing: shortest path (one path)
wavlength assignment: random

Author:   Yao Li (yaoli@optics.arizona.edu)
          Jiakai Yu (jiakaiyu@email.arizona.edu)
Created:  2017/05/03
Version:  1.0

Last modified by Yao: 2017/05/19

"""

from Common import *
import random
import rwa
import Database

def routing(traf_id, sources, destinations, bw_demand):
    """input: traf_id, sources, destinations, bw_demand
              sources: a list of [node_ip, node_port_id, route_type, cost, [common_avai_chnls]]
              destinations: a list of [node_ip, node_port_id]
       output: a list of [traf_id, route_type, cost, route(a list of [node_ip, add_port_id, drop_port_id]), common_avai_chnl(a list)]
               If fail, return None
    """
    pass
    
def rerouting(traf_id, sources, destinations, bw_demand):
    """input: traf_id, sources, destinations, bw_demand
              sources: a list of [node_ip, node_port_id, route_type, cost, [common_avai_chnls]]
              destinations: a list of [node_ip, node_port_id]
       output: a list of [traf_id, route_type, cost, route(a list of [node_ip, add_port_id, drop_port_id]), common_avai_chnl(a list)]
               If fail, return None
    """
    pass
    
def rsc_allocation(traf_id, bw_demand):
    """input: traf_id, bw_demand
       output: a list of [path_id, resources (a list)]. If not found, return None
    """
    pass
    
    
def find_exit_of_this_domain(next_domain_id):        #completed
    """randomly get one edge node go outside this domain to 'next_domain_id'
       input: next_domain_id
       output: a list of [node_ip, node_port_id]. if not found, return None
    """
    out_node_list = Database.Data.phy_topo.get_out_node_id(next_domain_id)
    if out_node_list != []:
        random.shuffle(out_node_list)          
        return out_node_list[0]
    else:
        return None
    
    
def find_entry_of_next_domain(traf_id):
    """find one next domain's entry of traf_id's Traffic, based on Database.Data.intra_domain_path_list's information
       input: traf_id
       output: a list of [node_ip, node_port_id, route_type, cost, [common_avai_chnls]]. If not found, return None
    """
    pass
    
def find_intra_domain_paths(exit_of_this_domain):
    """find the intra-domain routing path(s) from several candidates in Database.Data.intra_domain_path_list, based on 
       the exit node and port.
       input: exit_of_this_domain: a list of [node_ip, node_port_id, route_type, [chnls]]
       output: a list of [path_id, resources (a list)]. If not found, return None
    """
    pass
    

