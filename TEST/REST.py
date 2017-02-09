########### PCE... ##########



import logging
##import MySQLdb
import SocketServer

import json
##import yaml
##import pycurl
from webob import Response

from ryu.base import app_manager
from ryu.controller import ofp_event, event
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

#from nc_demo_2_class_no_pronto import PW, BW, path, Node, wavelength, meter_flow, olt

LOG = logging.getLogger('ryu.app.ofctl_rest')

# REST API
#

# Retrieve the switch stats
#
# get the list of all switches
# GET /stats/switches
#
# get the desc stats of the switch
# GET /stats/desc/<dpid>
#
# get flows stats of the switch
# GET /stats/flow/<dpid>
#
# get flows stats of the switch filtered by the fields
# POST /stats/flow/<dpid>
#
# get ports stats of the switch
# GET /stats/port/<dpid>
#
# get meter features stats of the switch
# GET /stats/meterfeatures/<dpid>
#
# get meter config stats of the switch
# GET /stats/meterconfig/<dpid>
#
# get meters stats of the switch
# GET /stats/meter/<dpid>
#
# get group features stats of the switch
# GET /stats/groupfeatures/<dpid>
#
# get groups desc stats of the switch
# GET /stats/groupdesc/<dpid>
#
# get groups stats of the switch
# GET /stats/group/<dpid>
#
# get ports description of the switch
# GET /stats/portdesc/<dpid>

# Update the switch stats
#
# add a flow entry
# POST /stats/flowentry/add
#
# modify all matching flow entries
# POST /stats/flowentry/modify
#
# modify flow entry strictly matching wildcards and priority
# POST /stats/flowentry/modify_strict
#
# delete all matching flow entries
# POST /stats/flowentry/delete
#
# delete flow entry strictly matching wildcards and priority
# POST /stats/flowentry/delete_strict
#
# delete all flow entries of the switch
# DELETE /stats/flowentry/clear/<dpid>
#
# add a meter entry
# POST /stats/meterentry/add
#
# modify a meter entry
# POST /stats/meterentry/modify
#
# delete a meter entry
# POST /stats/meterentry/delete
#
# add a group entry
# POST /stats/groupentry/add
#
# modify a group entry
# POST /stats/groupentry/modify
#
# delete a group entry
# POST /stats/groupentry/delete
#
# modify behavior of the physical port
# POST /stats/portdesc/modify

RESTAPIobj = None

class StatsController(ControllerBase):
##    _EVENTS =  [custom_event.TrafficRequestEvent]
    def __init__(self, req, link, data, **config):
        ControllerBase.__init__(self,req, link, data, **config)
##        super(StatsController, self).__init__(req, link, data, **config)
    #    self.dpset = data['dpset']
    #    self.waiters = data['waiters']


    ### Add, release, modify service
    def handle_traffic_request(self, req, cmd, **_kwargs):
##        print req,cmd

        if cmd == 'add':
            print req
            print 'Hi'
        else:
            return 'Hello World'

            

class RestStatsApi(app_manager.RyuApp):
##    _EVENTS =  [custom_event.TrafficRequestEvent]
    _CONTEXTS = {
        'dpset': dpset.DPSet,
        'wsgi': WSGIApplication
    }

    def __init__(self, *args, **kwargs):
        super(RestStatsApi, self).__init__(*args, **kwargs)
##        self.dpset = kwargs['dpset']
        wsgi = kwargs['wsgi']
       # self.waiters = {}
        self.data = {}
##        self.data['dpset'] = self.dpset
##        self.data['waiters'] = {}
        mapper = wsgi.mapper

        wsgi.registory['StatsController'] = self.data
        newpath = '/PCE'
        uri = newpath +'/channel/{cmd}'
        mapper.connect('stats',uri,
                      controller=StatsController, action='handle_traffic_request',
                      conditions=dict(method=['POST','GET']))
        global RESTAPIobj
        RESTAPIobj = self
       


