"""
contains data structures in Ryu controller

Author:   Yao Li (yaoli@optics.arizona.edu.cn)
Created:  2017/01/09
Version:  2.0

Last modified by Yao: 2017/01/20

"""

import Common

# Physical layer information

class Phy_node:
    def __init__(self):
        self.node_ip = ''
        self.node_id = 0
        self.node_type = 0
        self.port_num = 0
        self.ports = dict()        # port_id: port_type
     
     
class Phy_link:
    def __init__(self):
        self.link_id = 0
        self.link_type = 0
        self.src_node_ip = ''
        self.src_port_id = 0
        self.src_domain_id = 0
        self.dst_node_ip = ''
        self.dst_port_id = 0 
        self.dst_domain_id = 0 
        self.length = 0  
        self.ITU_Standards = 0  
        self.chnl_num = 0  
        self.chnl_ava = dict()      # chnl_id: chnl_avai
                
class Phy_topo:
    def __init__(self):
        self.node_num = 0
        self.link_num = 0
        self.node_list = []
        self.link_list = []
        
    def get_node_id_by_ip(self, node_ip):
        """input: node_ip
           output: node_id
        """
        return a_id
        
    def get_out_node_id(self):
        """randomly get an edge node go outside this domain
           input: null
           output: node_id
        """
        return a_id
        
# Physical layer information ends

# Lightpath information

class Node_for_route:
    def __init__(self):
        self.node_ip = ''
        self.add_port_id = 0
        self.add_port_power = 0
        self.drop_port_id = 0
        self.drop_port_power = 0

class Explicit_route:
    def __init__(self):
        self.hope_num = 0
        #self.route_type = 0
        self.cost = 0
        self.route = []

class LSP:
    def __init__(self):
        self.lsp_id = 0
        self.traf_id = 0
        self.route_type = 0
        self.lsp_state = 1
        self.add_node_ip = ''
        self.add_port_id = 0
        self.add_port_OSNR = None
        self.drop_node_ip = ''
        self.drop_port_id = 0
        self.drop_port_OSNR = None
        self.ITU_Standards = 0
        self.occ_chnl_num = 0
        self.occ_chnl = []
        self.explicit_route = Explicit_route()
        
class LSP_list:
    def __init__(self):
        self.lsp_num = 0
        self.lsp_list = []
        
    def insert_new_lsp(self, path, resources):
        """input: path: [traf_id, route_type, cost, route(a list of node_id), common_avai_chnl(a list)]
                  resources: common_avai_chnl(a list)
           output: a bool indicates result
        """
        return abool

# Lightpath information ends
        
# Traffic information

class Time:
    def __init__(self):
        self.valid = 0
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.day = 0
        self.month = 0
        self.year = 0

class Traffic:
    def __init__(self):
        self.traf_id = 0
        self.traf_stage = 0
        self.traf_state = 0
        self.src_node_ip = ''
        self.dst_node_ip = ''
        self.traf_type = 0
        self.prot_type = 0
        self.up_time = None
        self.down_time = None
        self.bw_dmd = 0
        self.OSNR_req = 0
        self.domain_num = 0
        self.domain_list = []
       
class Traffic_list:
    def __init__(self):
        self.traf_num = 0
        self.traf_list = []
        
    def insert_new_traf(self, ev):
        """input: an instance of class North_TrafficRequestEvent
           output: a bool indicates result
        """
    
        return abool
        
    def find_traf_by_id(self, traf_id):
        """input: a traffic id
           output: an instance of class Traffic or None(not found)
        """
    
        return atraf
        
    def update_traf_state(self, traf_id, traf_state):
        """input: traf_id, traf_state
           output: a bool indicates result
        """
        return abool
        
       
# Traffic information ends

# Controller information

class Controller:
    def __init__(self):
        self.controller_type = 0
        self.controller_ip = ''
        self.domain_id = 0
        
class Domain_sequence:
    def __init__(self):
        self.src_domain_id = 0
        self.dst_domain_id = 0
        self.hop_num = 0
        self.domain_list = []
        
class Controller_list:
    def __init__(self):
        self.this_controller = Controller()
        self.central_controller = Controller()
        self.local_controllers = []
        self.domain_sequence_num = 0
        self.domain_sequence_list = dict()      #(src_domain_id, dst_domain_id): [domain_id1, domain_id2, ...]
        
    def is_src_domain(self, domain_id):

        """input: domain_id
           output: a bool indicates if domain_id is this domain's id
        """
        return abool
        
# Controller information ends

# data structure used for cross-domain path computation

class Intra_domain_path:
    def __init__(self):
        self.traf_id = 0
        self.route_type = 0
        self.cost = 0
        self.route = []     # list of Node_for_route
        self.chnl = []      # common availabe channels
        
class Intra_domain_path_list:
    def __init__(self):
        self.intra_domain_path_list = []        # list of Intra_domain_path
        
    def insert_a_new_path(self, path):
        """input: [traf_id, route_type, cost, route(a list of node_id), common_avai_chnl]
           output: a bool indicates result
        """
        return abool

# data structure used for cross-domain path computation end

# timer

class LSP_msg_list:
    def __init__(self):
        self.lsp_id = 0
        self.route_type = 0
        self.msgs = []

class Timer:
    def __init__(self):
        self.traf_id = 0
        self.timer_type = 0
        self.end_time = 0
        self.lsp_msg_list = []  #a list of instances of class LSP_msg_list (only for south-bound timer use)
        
# timer end

# Global variables 
class Data:
    controller_list = Controller_list()
    phy_topo = Phy_topo()
    lsp_list = LSP_list()
    #unprovisioned_lsp_list = LSP_list()
    traf_list = Traffic_list()
    
    intra_domain_path_list = Intra_domain_path_list()       #for cross-domain path computation
    
    ip2datapath = dict()
    dpid2datapath = dict()
    
    lsp_id = 0
    message_id = 0
    north_timer = []
    eastwest_timer = []
    south_timer = []
    south_timer_no_response = []
    
    def __init__(self):
        pass
        
    @classmethod    
    def find_entry_of_next_domain(traf_id):
        """input: traf_id
           output: a list of [node_ip, node_port_id, route_type, cost, [common_avai_chnls]]
        """
        return a_list
        
# Global variables end
       