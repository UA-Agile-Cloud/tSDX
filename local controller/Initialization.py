"""
Used for initialize the database from files

Author:   Yao Li (yaoli@optics.arizona.edu.cn)
Created:  2017/01/11
Version:  2.0

Last modified by Yao: 2017/01/17

"""

from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls
import Common
import Database


class Initialization(app_manager.RyuApp):
                
    def __init__(self,*args,**kwargs):
        super(Initialization,self).__init__(*args,**kwargs)
        #	print 'Node'
        self.import_node_from_file("init_files/phy_node.txt")
        #	print 'Port'
        self.import_port_from_file("init_files/phy_node_port.txt")
        #	print 'Link'
        self.import_link_from_file("init_files/phy_link.txt")
        #	print 'Controller'
        self.import_controller_from_file("init_files/controller.txt")
        #	print 'Domain sequence'
        self.import_domain_sequence_from_file("init_files/domain_sequence.txt")
        


    def import_node_from_file(self, file_name):
        with open(file_name, 'r') as f:
            line = f.readline() 
            Database.Data.phy_topo.node_num =  int(line[0])
#            print Database.Data.phy_topo.node_num
            data = f.readlines()
            for line in data:  
                odom = line.split()        
                new_node = Database.Phy_node()
                new_node.node_ip = odom[0]
	              #print new_node.node_ip
                new_node.node_id = int(odom[1])
		            #print new_node.node_id
                new_node.node_type = int(odom[2])
		            #print new_node.node_type
                Database.Data.phy_topo.node_list.append(new_node)
#            for node in Database.Data.phy_topo.node_list:
#                print node.node_ip
#                print node.node_id
#                print node.node_type
                   
        
    def import_port_from_file(self, file_name):
        with open(file_name, 'r') as f:
            data = f.readlines()
            for line in data:  
                odom = line.split()
                for target_node in Database.Data.phy_topo.node_list:
                    if (target_node.node_ip == odom[0]):
                        target_node.port_num = int(odom[1])
#                        print target_node.port_num
                        it = 2;
                        for i in range(target_node.port_num):
                            target_node.ports[int(odom[it])] = int(odom[it+1])
                            it += 2
			                  #print target_node.node_ip
                        #print target_node.ports
                        break
#            for node in Database.Data.phy_topo.node_list:
#                print node.node_ip
#                print node.ports
    

    def import_link_from_file(self, file_name):    
        with open(file_name, 'r') as f:
            line = f.readline() 
            Database.Data.phy_topo.link_num =  int(line[0])
#            print Database.Data.phy_topo.link_num
            data = f.readlines()
            for line in data:  
                odom = line.split()        
                new_link = Database.Phy_link()
                new_link.link_id = int(odom[0])
                new_link.link_type = int(odom[1])
                new_link.src_node_ip = odom[2]
                new_link.src_port_id = int(odom[3])
                new_link.src_domain_id = int(odom[4])
                new_link.dst_node_ip = odom[5]
                new_link.dst_port_id = int(odom[6])
                new_link.dst_domain_id = int(odom[7])
                new_link.length = float(odom[8])
                new_link.ITU_Standards = int(odom[9])
                new_link.chnl_num = int(odom[10])
                for i in range(new_link.chnl_num):
                    new_link.chnl_ava[i+1] = 0
                Database.Data.phy_topo.link_list.append(new_link)
#            for link in Database.Data.phy_topo.link_list:
#                print link.link_id
#                print link.link_type
#                print link.src_node_ip
#                print link.src_port_id
#                print link.src_domain_id
#                print link.dst_node_ip
#                print link.dst_port_id
#                print link.dst_domain_id
#                print link.length
#                print link.ITU_Standards
#                print link.chnl_num
#                print link.chnl_ava
            
    
    
    def import_controller_from_file(self, file_name):
         with open(file_name, 'r') as f:
            line = f.readline() 
            odom = line.split() 
            Database.Data.controller_list.this_controller.controller_type =  int(odom[0])
            Database.Data.controller_list.this_controller.controller_ip =  odom[1]
            Database.Data.controller_list.this_controller.domain_id =  int(odom[2])
#            print Database.Data.controller_list.this_controller.controller_type
#            print Database.Data.controller_list.this_controller.controller_ip
#            print Database.Data.controller_list.this_controller.domain_id
            line = f.readline() 
            odom = line.split() 
            Database.Data.controller_list.central_controller.controller_type =  int(odom[0])
            Database.Data.controller_list.central_controller.controller_ip =  odom[1]
            Database.Data.controller_list.central_controller.domain_id =  int(odom[2])
#            print Database.Data.controller_list.central_controller.controller_type
#            print Database.Data.controller_list.central_controller.controller_ip
#            print Database.Data.controller_list.central_controller.domain_id
            data = f.readlines()
            for line in data: 
                odom = line.split()  
                new_ctrller = Database.Controller()
                new_ctrller.controller_type = int(odom[0])
                new_ctrller.controller_ip = odom[1]
                new_ctrller.domain_id = int(odom[2])
                Database.Data.controller_list.local_controllers.append(new_ctrller)
 #           for ctrller in Database.Data.controller_list.local_controllers:
 #               print ctrller.controller_type
 #               print ctrller.controller_ip
 #               print ctrller.domain_id
                
    
    def import_domain_sequence_from_file(self, file_name):
        with open(file_name, 'r') as f:
            line = f.readline() 
            Database.Data.controller_list.domain_sequence_num =  int(line[0])
#            print Database.Data.controller_list.domain_sequence_num
            data = f.readlines()
            for line in data: 
                odom = line.split()  
                new_list = []
                for i in range(int(odom[2])+1):
                    new_list.append(int(odom[i+3]))
                Database.Data.controller_list.domain_sequence_list[(int(odom[0]), int(odom[1]))] = new_list
#            print Database.Data.controller_list.domain_sequence_list
    
