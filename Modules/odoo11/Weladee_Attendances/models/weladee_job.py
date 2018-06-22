# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

import base64
import requests
import time
import webbrowser

from odoo import osv
from odoo import models, fields, api
from datetime import datetime,date, timedelta
from odoo import exceptions

from .grpcproto import odoo_pb2
from .grpcproto import odoo_pb2_grpc
from .grpcproto import weladee_pb2
from . import weladee_grpc
from . import weladee_employee
from .sync.weladee_base import stub, myrequest

class weladee_job(models.Model):
  _description="synchronous position to weladee"
  _inherit = 'hr.job'

  weladee_id = fields.Char(string="Weladee ID")

  @api.model
  def create(self, vals) :
    pid = super(weladee_job,self).create( vals )
    
    if not "weladee_id" in vals:

      authorization, __, __ = weladee_employee.get_api_key(self)
      #print("API : %s" % authorization)
      if authorization :
        if True :
          weladeePositions = {}
          odooRequest = odoo_pb2.OdooRequest()
          odooRequest.Force = True
          for position in stub.GetPositions(odooRequest, metadata=authorization):
            if position :
              if position.position.NameEnglish :
                weladeePositions[ position.position.NameEnglish ] = position.position.ID

          if not vals["name"] in weladeePositions :
            newPosition = odoo_pb2.PositionOdoo()
            newPosition.odoo.odoo_id = pid.id
            newPosition.odoo.odoo_created_on = int(time.time())
            newPosition.odoo.odoo_synced_on = int(time.time())

            newPosition.position.NameEnglish = vals["name"]
            newPosition.position.active = True

            print(newPosition)
            try:
              result = stub.AddPosition(newPosition, metadata=authorization)
              print ("Added position on Weladee : %s" % result.id)
            except Exception as e:
              print("Add position failed",e)

    return pid

  def write(self, vals):
    pid = super(weladee_job, self).write( vals )
    authorization, __, __ = weladee_employee.get_api_key(self)
    #print("API : %s" % authorization)
    if not "weladee_id" in vals :
      if authorization :
        if True :
          if "name" in vals:
            weladeePositions = {}
            for position in stub.GetPositions(metadata=authorization):
              if position :
                if position.position.NameEnglish :
                  weladeePositions[ position.position.NameEnglish ] = position.position.ID

            if not vals["name"] in weladeePositions :
              newPosition = odoo_pb2.PositionOdoo()
              newPosition.odoo.odoo_id = self.id
              newPosition.odoo.odoo_created_on = int(time.time())
              newPosition.odoo.odoo_synced_on = int(time.time())

              newPosition.position.NameEnglish = vals["name"]
              newPosition.position.active = True

              print(newPosition)
              try:
                result = stub.AddPosition(newPosition, metadata=authorization)
                print ("Added position on Weladee")
              except Exception as e:
                print("Add position failed",e)

    return pid
weladee_job()