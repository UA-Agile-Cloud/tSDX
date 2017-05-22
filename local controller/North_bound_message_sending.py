"""
send north-bound messages 

Author:   Yao Li (yaoli@optics.arizona.edu)
          Jiakai Yu (jiakaiyu@email.arizona.edu)
Created:  2017/01/18
Version:  2.0

Last modified by Yao: 2017/04/30

"""


from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
#import Common
#import Database


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

from ryu.lib import hub
import time

LOG = logging.getLogger('ryu.app.NBMSrest')
#RESTAPIobj = None
#global RESTAPIobj
#RESTAPIobj = 

class North_bound_message_send(app_manager.RyuApp):
    
    _EVENTS =  [Custom_event.North_TrafficReplyEvent,
                Custom_event.North_TrafficTeardownReplyEvent,
                Custom_event.North_TrafficStateUpdateEvent]
                
    def __init__(self,*args,**kwargs):
        super(North_bound_message_send,self).__init__(*args,**kwargs)
        self.listening_thread = hub.spawn(self._listening)
        
   # def __init__(self, req, link, data, **config):
    #    ControllerBase.__init__(self,req, link, data, **config)
    
    # added by Yao
    def _listening(self):
        while True:
            ready_remove = list()
            for this_timer in Database.Data.north_timer:
                if this_timer.end_time < time.time():
                    if this_timer.timer_type == TIMER_TRAFFIC_SETUP:
                        traf_setup_reply_ev = Custom_event.North_TrafficReplyEvent()
                        traf_setup_reply_ev.traf_id = this_timer.traf_id
                        traf_setup_reply_ev.result = TIMEOUT_TRAF_SETUP
                        traf_setup_reply_ev.traf_stage = TRAFFIC_STAGE_UNKNOWN
                        traf_setup_reply_ev.traf_state = TRAFFIC_STATE_UNKNOWN
                        self.send_event('North_bound_message_send', traf_setup_reply_ev)
                        ready_remove.append(this_timer)
                    elif this_timer.timer_type == TIMER_TRAFFIC_TEARDOWN:
                        traf_tear_reply_ev = Custom_event.North_TrafficTeardownReplyEvent()
                        traf_tear_reply_ev.traf_id = this_timer.traf_id
                        traf_tear_reply_ev.result = TIMEOUT_TRAF_TEARDOWN
                        traf_tear_reply_ev.traf_stage = TRAFFIC_STAGE_UNKNOWN
                        traf_tear_reply_ev.traf_state = TRAFFIC_STATE_UNKNOWN
                        self.send_event('North_bound_message_send', traf_tear_reply_ev)
                        ready_remove.append(this_timer)
                    else:
                        self.logger.info('Invalid north timer type! (North_bound_message_send: _listening)')
            for timer in ready_remove:
                Database.Data.north_timer.remove(timer)
            hub.sleep(0.1)
    # added by Yao end                

    @set_ev_cls(Custom_event.North_TrafficReplyEvent)
    def _handle_traffic_reply(self,ev):
        # added by Yao
        flag = False
        for this_timer in Database.Data.north_timer:
            if this_timer.traf_id == ev.traf_id and this_timer.timer_type == TIMER_TRAFFIC_SETUP:
                flag = True
                break
        if flag == False:
            self.logger.info('Cannot find this reply message in timer! (North_bound_message_send: _handle_traffic_reply)')
            return
        else:
            Database.Data.north_timer.remove(this_timer)
        # added by Yao end
        
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
        # added by Yao
        flag = False
        for this_timer in Database.Data.north_timer:
            if this_timer.traf_id == ev.traf_id and this_timer.timer_type == TIMER_TRAFFIC_TEARDOWN:
                flag = True
                break
        if flag == False:
            self.logger.info('Cannot find this reply message in timer! (North_bound_message_send: _handle_traffic_teardown_reply)')
            return
        else:
            Database.Data.north_timer.remove(this_timer)
        # added by Yao end
        
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
        




            
