"""
Ryu Northbound Message Sending app by Jiakai Yu

"""

# please install json, yaml, pycurl
from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
import json
import yaml
import pycurl
import json
import httplib
import logging
import requests
from ryu.base import app_manager
import Custom_event
from webob import Response
from ryu.app.wsgi import ControllerBase

LOG = logging.getLogger('ryu.app.NBMSrest')
#RESTAPIobj = None
#global RESTAPIobj
#RESTAPIobj = 


#receive the message from RYU controller and forward it in JSON format to ONOS RequestReceving app
class North_bound_message_send(app_manager.RyuApp):
    
    _EVENTS =  [Custom_event.North_TrafficReplyEvent,
                Custom_event.North_TrafficTeardownReplyEvent,
                Custom_event.North_TrafficStateUpdateEvent]
                
    def __init__(self,*args,**kwargs):
        super(North_bound_message_send,self).__init__(*args,**kwargs)
        

    @set_ev_cls(Custom_event.North_TrafficReplyEvent)
    def _handle_traffic_reply(self,ev):
        status_return = {'Request_Class': 'North_TrafficReplyEvent',
			 'Result': ev.result,
                         'Msg_ID': ev.traf_id,
                         'Traf_Stage': ev.traf_stage,
                         'Traf_State': ev.traf_state,                        
                         }
        data_string = json.dumps(status_return)
        #RESTAPIobj=data_string
        #print res
        print '========================================================='
        url = '/TrafficReply'
        conn = httplib.HTTPConnection('192.168.0.1:8888')
        conn.request(method="POST",url=url,body=data_string) 
        response = conn.getresponse()
        res= response
        print '.............................'
        print data_string
        return data_string
        
    @set_ev_cls(Custom_event.North_TrafficTeardownReplyEvent)
    def _handle_traffic_teardown_reply(self,ev):
        status_return = {'Request_Class': 'North_TrafficTeardownReplyEvent',
                         'Result': ev.result,
                         'Msg_ID': ev.traf_id,
                         'Traf_Stage': ev.traf_stage,
                         'Traf_State': ev.traf_state,                        
                         }
        data_string = json.dumps(status_return)
        print '========================================================='
        url = '/TrafficTeardownReply'
        conn = httplib.HTTPConnection('192.168.0.1:8888')
        conn.request(method="POST",url=url,body=data_string) 
        response = conn.getresponse()
        res= response
        print '.............................'
        print data_string
        return data_string
        
    @set_ev_cls(Custom_event.North_TrafficStateUpdateEvent)
    def _handle_traffic_state_update(self,ev):
        status_return = {'Request_Class': 'North_TrafficStateUpdateEvent',
                         'Msg_ID': ev.traf_id,                       
                         'Traf_Stage': ev.traf_stage,
                         'Traf_State': ev.traf_state,                        
                         }
        data_string = json.dumps(status_return)
        print '========================================================='
        url = '/TrafficStateUpdate'
        conn = httplib.HTTPConnection('192.168.0.1:8888')
        conn.request(method="POST",url=url,body=data_string) 
        response = conn.getresponse()
        res= response
        print '.............................'
        print data_string
        return data_string

 # the fowllowing codes are used for test
'''class RestStatsApi(app_manager.RyuApp):
    _EVENTS =  [Custom_event.North_TrafficReplyEvent,
                Custom_event.North_TrafficTeardownReplyEvent,
                Custom_event.North_TrafficStateUpdateEvent]
                
    def __init__(self, *args, **kwargs):
        super(RestStatsApi, self).__init__(*args, **kwargs)
        self.data = {}
        value={'Request_Class': 'TrafficRequestEvent','Msg_ID': 27, 'Traf_Stage': 'TRAFFIC_WORKING','Traf_State':'TRAFFIC_RECEIVE_REQUEST','Traf_Result':'SUCCESSFUL'}
        jdata=json.dumps(value)
        url = '/'
        conn = httplib.HTTPConnection('192.168.0.1:8888')
        conn.request(method="POST",url=url,body=jdata) 
        response = conn.getresponse()
        res= response
        print res'''
        




            
