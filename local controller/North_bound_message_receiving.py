"""
Ryu Northbound Message Receiving app by Jiakai Yu

"""

from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from Common import *
import logging
import SocketServer
import urllib
import urllib2
import httplib
import requests
import json
import yaml
import pycurl
from webob import Response
from ryu.base import app_manager
from ryu.controller import ofp_event, event
import Custom_event
from ryu.controller import dpset
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto import ofproto_v1_2
from ryu.ofproto import ofproto_v1_3
from ryu.lib import ofctl_v1_0
from ryu.lib import ofctl_v1_2
from ryu.lib import ofctl_v1_3
from ryu.app.wsgi import ControllerBase, WSGIApplication
from ryu.lib.ip import ipv4_to_bin
from StringIO import StringIO 


LOG = logging.getLogger('ryu.app.NBMRrest')
RESTAPIobj = None

class North_bound_message_receive(ControllerBase):
    
    _EVENTS =  [Custom_event.North_CrossDomainTrafficRequestEvent,
                Custom_event.North_IntraDomainTrafficRequestEvent,
                Custom_event.North_IntraDomainTrafficTeardownRequestEvent,
                Custom_event.North_CrossDomainTrafficTeardownRequestEvent]
                
    def __init__(self, req, link, data, **config):
        ControllerBase.__init__(self,req, link, data, **config)
        #self.listening_thread = hub.spawn(self._listening)

    def handle_empty_request(self,req,**_kwargs):
        print '=========================================================='
        #print req
        #print '----------------------------------'
        
    #receve traffic and get the json format of it, and identify the link setup request class
    def handle_traffic_request(self, req, cmd, **_kwargs):
        json_str = req.body
        decoded = yaml.load(json_str)
        if cmd == 'add_device':
            print 'Add Device Successfully'
            return 'add device'
        #else:
            #return 'Try ADD'
        elif cmd == 'TrafficRequest':
            request_class = decoded['Request_Class']
            if request_class == 'TrafficRequestEvent':
                print req
                return 'TrafficRequestEvent'
            elif request_class == 'North_TrafficTeardownReplyEvent':
                print req
                return 'North_TrafficTeardownReplyEvent'
            elif request_class == 'North_TrafficStateUpdateEvent':
                print req
                return 'North_TrafficStateUpdateEvent'

            elif request_class == 'CorssDomainRequest' or request_class == 'CorssDomainRequest_rev':
                traffic_request = Custom_event.North_CrossDomainTrafficRequestEvent()
                if int(decoded['Source_Node'])<4:
                    traffic_request.src_node_ip = '192.168.1.'+ decoded['Source_Node']
                if int(decoded['Source_Node'])>3:
                    traffic_request.src_node_ip = '192.168.2.'+ str(int(decoded['Source_Node'])-3)
                if int(decoded['Destination_Node'])>3:
                    traffic_request.dst_node_ip = '192.168.2.'+ str(int(decoded['Destination_Node'])-3)
                if int(decoded['Destination_Node'])<4:
                    traffic_request.dst_node_ip = '192.168.1.'+ decoded['Destination_Node']
                traffic_request.traf_id = int(decoded['Msg_ID'])
                traffic_request.traf_stage = TRAFFIC_WORKING
                traffic_request.traf_state =TRAFFIC_RECEIVE_REQUEST         
                traffic_request.traf_type = TRAFFIC_CROSS_DOMAIN
                traffic_request.prot_type = TRAFFIC_REROUTING_RESTORATION
                traffic_request.up_time = None
                traffic_request.down_time = None
                traffic_request.bw_demand = 0
                traffic_request.OSNR_req = 0
                traffic_request.domain_num = 2
                if request_class == 'CorssDomainRequest':
                    traffic_request.domain_sequence = [1, 2]
                elif request_class == 'CorssDomainRequest_rev':
                    traffic_request.domain_sequence = [2, 1]
                    
                #send the event to RYU controller based on the ONOS forwarded request
                RESTAPIobj.send_event('Cross_domain_connection_ctrl', traffic_request)

                status_return = {'Result':'CorssDomainRequest Received',
                                 'Traf_ID': traffic_request.traf_id,
                                 'Source_Node':traffic_request.src_node_ip,
                                 'Destination_Node':traffic_request.dst_node_ip,
                                 'Traf_Stage': traffic_request.traf_stage,
                                 'Traf_State': traffic_request.traf_state,         
                                 'Traf_Type': traffic_request.traf_type,
                                 'Prot_Type': traffic_request.prot_type,
                                 'Up_Time': traffic_request.up_time,
                                 'Down_Time': traffic_request.down_time,
                                 'BW_Demand': traffic_request.bw_demand,
                                 'OSNR_Req': traffic_request.OSNR_req,
                                 'Domain_Num': traffic_request.domain_num,
                                 'Domain_Seq': traffic_request.domain_sequence,                        
                                }
                data_string = json.dumps(status_return)
                print '========================================================='
                print req
                print '.............................'
                print data_string
                return data_string
            
            elif request_class == 'IntraDomainRequest' or request_class == 'IntraDomainRequest_rev':
                traffic_request = Custom_event.North_IntraDomainTrafficRequestEvent()
                if int(decoded['Source_Node'])<4:
                    traffic_request.src_node_ip = '192.168.1.'+ decoded['Source_Node']
                if int(decoded['Source_Node'])>3:
                    traffic_request.src_node_ip = '192.168.2.'+ str(int(decoded['Source_Node'])-3)
                if int(decoded['Destination_Node'])>3:
                    traffic_request.dst_node_ip = '192.168.2.'+ str(int(decoded['Destination_Node'])-3)
                if int(decoded['Destination_Node'])<4:
                    traffic_request.dst_node_ip = '192.168.1.'+ decoded['Destination_Node']
                traffic_request.traf_id = int(decoded['Msg_ID'])
                traffic_request.traf_stage = TRAFFIC_WORKING
                traffic_request.traf_state = TRAFFIC_RECEIVE_REQUEST           
                traffic_request.traf_type = TRAFFIC_INTRA_DOMAIN
                traffic_request.prot_type = TRAFFIC_REROUTING_RESTORATION
                traffic_request.up_time = None
                traffic_request.down_time = None
                traffic_request.bw_demand = 0
                traffic_request.OSNR_req = 0
                traffic_request.domain_num = 1
                if request_class == 'IntraDomainRequest':
                    traffic_request.domain_sequence = [1, 1]
                if request_class == 'IntraDomainRequest_rev':
                    traffic_request.domain_sequence = [2, 2]
                RESTAPIobj.send_event('Intra_domain_connection_ctrl', traffic_request)
                status_return = {'Result':'IntraDomainRequest Received',
                                 'Traf_ID': traffic_request.traf_id,
                                 'Source_Node':traffic_request.src_node_ip,
                                 'Destination_Node':traffic_request.dst_node_ip,
                                 'Traf_Stage': traffic_request.traf_stage,
                                 'Traf_State': traffic_request.traf_state,         
                                 'Traf_Type': traffic_request.traf_type,
                                 'Prot_Type': traffic_request.prot_type,
                                 'Up_Time': traffic_request.up_time,
                                 'Down_Time': traffic_request.down_time,
                                 'BW_Demand': traffic_request.bw_demand,
                                 'OSNR_Req': traffic_request.OSNR_req,
                                 'Domain_Num': traffic_request.domain_num,
                                 'Domain_Seq': traffic_request.domain_sequence,                        
                                }
                data_string = json.dumps(status_return)
                print '========================================================='
                print req
                print '.............................'
                print data_string
                return data_string
            elif request_class == 'IntraDomainTearDown':
                traffic_request = Custom_event.North_IntraDomainTrafficTeardownRequestEvent()
                traffic_request.traf_id = decoded['TearTraf']
                status_return = {'Result':'IntraDomainTearDown Received',
                                 'TearTraf' : traffic_request.traf_id,
                                }
                data_string = json.dumps(status_return)
                print '========================================================='
                print req
                print '.............................'
                print data_string
                return data_string
            elif request_class == 'CrossDomainTearDown':
                traffic_request = Custom_event.North_CrossDomainTrafficTeardownRequestEvent()
                traffic_request.traf_id = decoded['TearTraf']
                status_return = {'Result':'CrossDomainTearDown Received',
                                 'TearTraf' : traffic_request.traf_id,
                                }
                data_string = json.dumps(status_return)
                print '========================================================='
                print req
                print '.............................'
                print data_string
                return data_string
            else:
                print '========================================================='
                print req
                print '.............................'
                print 'Wrong Request'
                return 'Wrong Request'
        else:
            print 'Try Other command'
            return 'Try Other command'

class RestStatsApi(app_manager.RyuApp):
    _EVENTS =  [Custom_event.North_CrossDomainTrafficRequestEvent,
                Custom_event.North_IntraDomainTrafficRequestEvent,
                Custom_event.North_IntraDomainTrafficTeardownRequestEvent,
                Custom_event.North_CrossDomainTrafficTeardownRequestEvent]
    _CONTEXTS = {
        'dpset': dpset.DPSet,
        'wsgi': WSGIApplication
    }

    #set up a Web Server Gateway Interface to receive message
    def __init__(self, *args, **kwargs):
        super(RestStatsApi, self).__init__(*args, **kwargs)
        wsgi = kwargs['wsgi']
        self.data = {}
        mapper = wsgi.mapper

        wsgi.registory['North_bound_message_receive'] = self.data
        newpath = ''
        uri = newpath +'/{cmd}'
        mapper.connect('stats','/',
                      controller=North_bound_message_receive, action='handle_empty_request',
                      conditions=dict(method=['POST','GET']))
        mapper.connect('stats',uri,
                      controller=North_bound_message_receive, action='handle_traffic_request',
                      conditions=dict(method=['POST','GET']))

        global RESTAPIobj
        RESTAPIobj = self
       

        
            
