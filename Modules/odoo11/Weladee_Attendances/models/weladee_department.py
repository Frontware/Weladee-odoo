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

class weladee_department(models.Model):
  _description="synchronous department to weladee"
  _inherit = 'hr.department'

  weladee_id = fields.Char(string="Weladee ID")

  @api.model
  def create(self, vals ) :
    dId = super(weladee_department,self).create( vals )
    if not "weladee_id" in vals:
      authorization = False
      authorization, holiday_status_id = weladee_employee.get_api_key(self)
      #print("API : %s" % authorization)
      if authorization :
        if True :
          newDepartment = odoo_pb2.DepartmentOdoo()
          newDepartment.odoo.odoo_id = dId.id
          newDepartment.odoo.odoo_created_on = int(time.time())
          newDepartment.odoo.odoo_synced_on = int(time.time())
          newDepartment.department.name_english = vals["name"]
          newDepartment.department.name_thai = vals["name"]
          print(newDepartment)
          try:
            result = stub.AddDepartment(newDepartment, metadata=authorization)
            print ("Create Weladee department id : %s" % result.id)
            dId.write( {"weladee_id" : str( result.id )} )
          except Exception as e:
            print("Create department failed",e)
    return dId

  def write(self, vals ):
    oldData = self.env['hr.department'].browse( self.id )
    authorization = False
    authorization, holiday_status_id = weladee_employee.get_api_key(self)
    #print("API : %s" % authorization)
    if not "weladee_id" in vals :
      
      if authorization :
        if True :
          dept = False
          odooRequest = odoo_pb2.OdooRequest()
          odooRequest.odoo_id = int(self.id)
          for dpm in stub.GetDepartments(odooRequest, metadata=authorization):
            if dpm :
              if dpm.odoo :
                if dpm.odoo.odoo_id :
                  if dpm.odoo.odoo_id ==  self.id :
                    dept = dpm
          if dept :
            updateDepartment = odoo_pb2.DepartmentOdoo()
            updateDepartment.odoo.odoo_id = self.id
            updateDepartment.odoo.odoo_created_on = int(time.time())
            updateDepartment.odoo.odoo_synced_on = int(time.time())
          if "name" in vals :
            updateDepartment.department.name_english = vals["name"]
          else :
            updateDepartment.department.name_english = oldData["name"]
          updateDepartment.department.id = dept.department.id
          updateDepartment.department.name_thai = updateDepartment.department.name_english
          if dept.department.managerid :
            updateDepartment.department.managerid = dept.department.managerid
          updateDepartment.department.active = ( dept.department.active or False )
          updateDepartment.department.code = ( dept.department.code or "" )
          updateDepartment.department.note = ( dept.department.note or "" )
          print( updateDepartment )
          try :
            result = stub.UpdateDepartment(updateDepartment, metadata=authorization)
            print ("Updated odoo department id to Weladee")
          except Exception as e:
            print("Update odoo department id is failed",e)
    
    return super(weladee_department, self).write( vals )
weladee_department()