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

# Weladee grpc server address is hrpc.weladee.com:22443
stub = weladee_grpc.weladee_grpc_ctrl()
myrequest = weladee_pb2.EmployeeRequest()

def get_api_key(self):
  '''
  get api key from settings

  '''
  line_obj = self.env['weladee_attendance.synchronous.setting']
  line_ids = line_obj.search([])
  authorization = False
  holiday_status_id = False

  for sId in line_ids:
      dataSet = line_obj.browse(sId.id)
      if dataSet.api_key :
          authorization = [("authorization", dataSet.api_key)]
      if dataSet.holiday_status_id :
          holiday_status_id = dataSet.holiday_status_id
  return authorization, holiday_status_id

def get_weladee_employee(weladee_id, authorization):
    '''
    get weladee employeeodoo from weladee_id
    '''
    odooRequest = odoo_pb2.OdooRequest()
    odooRequest.ID = int(weladee_id or '0')
    for emp in stub.GetEmployees(odooRequest, metadata=authorization):
        if emp and emp.employee :
           return emp

    return False

class weladee_employee(models.Model):
  _description="synchronous Employee to weladee"
  _inherit = 'hr.employee'

  #contact info
  work_email = fields.Char(required=True)

  #position
  job_id = fields.Many2one(required=True)

  #citizenship
  country_id = fields.Many2one(string="Nationality (Country)", required=True)
  taxID = fields.Char(string="TaxID")
  nationalID = fields.Char(string="NationalID")
  
  #main
  first_name_english = fields.Char(string="English First Name")
  last_name_english = fields.Char(string="English Last Name")
  first_name_thai = fields.Char(string="Thai First Name")
  last_name_thai = fields.Char(string="Thai Last Name")
  nick_name_english = fields.Char(string="English Nick Name")
  nick_name_thai = fields.Char(string="Thai Nick Name")

  #weladee link
  weladee_profile = fields.Char(string="Weladee Url",default="")
  weladee_id = fields.Char(string="Weladee ID")
  receive_check_notification = fields.Boolean(string="Receive Check Notification")
  can_request_holiday = fields.Boolean(string="Can Request Holiday")
  hasToFillTimesheet = fields.Boolean(string="Has To Fill Timesheet")

  #other 
  employee_code = fields.Char(string='Employee Code')

  @api.model
  def create(self, vals):
      '''
      create employee (to sync back to weladee)

      remarks:
      2018-05-28 KPO clean up
      '''
      eid = super(weladee_employee,self).create(vals)

      if not "weladee_id" in vals:
         _logger.info("Create new request to weladee...")
         authorization, _ = get_api_key(self)
         if not authorization :
            _logger.error("Your Odoo is not authroize to use weladee")

         else:  

            WeladeeData = odoo_pb2.EmployeeOdoo()
            WeladeeData.odoo.odoo_id = eid.id
            WeladeeData.odoo.odoo_created_on = int(time.time())
            WeladeeData.odoo.odoo_synced_on = int(time.time())

            if "first_name_english" in vals :
              WeladeeData.employee.first_name_english = vals["first_name_english"] or ''
            if "last_name_english" in vals :
              WeladeeData.employee.last_name_english = vals["last_name_english"] or ''

            # default from name
            if not "first_name_english" in vals and not "last_name_english" in vals :
               if vals["name"]:
                  WeladeeData.employee.first_name_english = ( vals["name"] ).split(" ")[0]
                  if len( ( vals["name"] ).split(" ") ) > 1 :
                    WeladeeData.employee.last_name_english = ( vals["name"] ).split(" ")[1]
                  else :
                    WeladeeData.employee.last_name_english = " "

            if "first_name_thai" in vals :
              WeladeeData.employee.first_name_thai = vals["first_name_thai"] or ''
            if "last_name_thai" in vals :
              WeladeeData.employee.last_name_thai = vals["last_name_thai"] or ''

            if "nick_name_english" in vals :
              WeladeeData.employee.nickname_english = vals["nick_name_english"] or ''
            if "nick_name_thai" in vals :
              WeladeeData.employee.nickname_thai = vals["nick_name_thai"] or ''

            #2018-05-28 KPO change to employee_code
            if "employee_code" in vals :
              WeladeeData.employee.code = vals["employee_code"] or ''

            if vals["country_id"] :
              c_line_obj = self.env['res.country']
              cdata = c_line_obj.browse( vals["country_id"] )
              if cdata :
                if cdata.name :
                  WeladeeData.employee.Nationality = cdata.name

            if vals["notes"] :
              WeladeeData.employee.note = vals["notes"] or ''

            if vals["work_email"] :
              WeladeeData.employee.email = vals["work_email"] or ''
            
            if "parent_id" in vals :
              manager = self.env['hr.employee'].browse( vals["parent_id"] )
              if manager :
                WeladeeData.employee.managerID = int(manager.weladee_id)

            if vals["job_id"] :
              positionData = self.env['hr.job'].browse( vals["job_id"] )
              if positionData :
                if positionData.weladee_id :
                  WeladeeData.employee.positionid = int(positionData.weladee_id)

            #language not sync yet
            WeladeeData.employee.lg = "en"
            WeladeeData.employee.Active = vals["active"]
            WeladeeData.employee.receiveCheckNotification = vals["receive_check_notification"]
            WeladeeData.employee.canRequestHoliday = vals["can_request_holiday"]
            WeladeeData.employee.hasToFillTimesheet = vals["hasToFillTimesheet"]

            #2018-05-28 KPO use field from odoo
            if vals["passport_id"] :
              WeladeeData.employee.passportNumber = vals["passport_id"] or ''

            if vals["taxID"] :
              WeladeeData.employee.taxID = vals["taxID"] or ''
            
            if vals["nationalID"] :
              WeladeeData.employee.nationalID = vals["nationalID"] or ''

            if vals["image"] :
              WeladeeData.employee.photo = vals["image"] or ''

            if vals["work_phone"] :
              if len(WeladeeData.employee.Phones) == 0:
                 WeladeeData.employee.Phones[:] = [vals['work_phone']]
              else:  
                 WeladeeData.employee.Phones[0] = vals['work_phone']

            try:
              result = stub.AddEmployee(WeladeeData, metadata=authorization)
              print ("New Weladee id : %s" % result.id)
              eid.write( {"weladee_id" : str(result.id), "weladee_profile" : "https://www.weladee.com/employee/" + str(result.id)  } )              
              _logger.info("Created new employee in weladee: %s" % result.id)
            except Exception as e:
              print("Add employee failed", e)
              _logger.error("Error while add employee to weladee: %s" % e)

      return eid

  def write(self, vals):
      '''
      update employee (to sync back to weladee)

      remarks:
      2018-05-28 KPO clean up
      '''

      #get record from weladee
      WeladeeData = odoo_pb2.EmployeeOdoo()
      authorization, _ = get_api_key(self)
      if not authorization :
         _logger.error("Your Odoo is not authroize to use weladee")
      else:

        if self.weladee_id:
           WeladeeData = get_weladee_employee(self.weladee_id, authorization)
        
        #sync data
        #if has in input, take it
        #else if has in object, take it
        #else use from grpc
        if WeladeeData :

          #record to send grpc  
          WeladeeData.odoo.odoo_id = self.id
          WeladeeData.odoo.odoo_created_on = int(time.time())
          WeladeeData.odoo.odoo_synced_on = int(time.time())
          
          if "first_name_english" in vals :
            WeladeeData.employee.first_name_english = vals["first_name_english"] or ''
          else:
            WeladeeData.employee.first_name_english = self.first_name_english or ''

          if "last_name_english" in vals :
            WeladeeData.employee.last_name_english = vals["last_name_english"] or ''
          else:
            WeladeeData.employee.last_name_english = self.last_name_english or ''

          if "first_name_thai" in vals :
            WeladeeData.employee.first_name_thai = vals["first_name_thai"] or ''
          else:
            WeladeeData.employee.first_name_thai = self.first_name_thai or ''

          if "last_name_thai" in vals :
            WeladeeData.employee.last_name_thai = vals["last_name_thai"] or ''
          else:
            WeladeeData.employee.last_name_thai = self.last_name_thai or ''

          if "nick_name_english" in vals :
            WeladeeData.employee.nickname_english = vals["nick_name_english"] or ''
          else:
            WeladeeData.employee.nickname_english = self.nick_name_english or ''

          if "nick_name_thai" in vals :
            WeladeeData.employee.nickname_thai = vals["nick_name_thai"] or ''
          else:
            WeladeeData.employee.nickname_thai = self.nick_name_thai or ''

          if "active" in vals :
            WeladeeData.employee.Active = vals["active"]
          else:
            WeladeeData.employee.Active = self.active

          if "receive_check_notification" in vals :
            WeladeeData.employee.receiveCheckNotification = vals["receive_check_notification"]
          else :
            WeladeeData.employee.receiveCheckNotification = self.receive_check_notification

          if "can_request_holiday" in vals :
            WeladeeData.employee.canRequestHoliday = vals["can_request_holiday"]
          else :
            WeladeeData.employee.canRequestHoliday = self.can_request_holiday

          if "hasToFillTimesheet" in vals :
            WeladeeData.employee.hasToFillTimesheet = vals["hasToFillTimesheet"]
          else :
            WeladeeData.employee.hasToFillTimesheet = self.hasToFillTimesheet

          #2018-05-28 KPO use passport_id from odoo
          if "passport_id" in vals :
            WeladeeData.employee.passportNumber = vals["passport_id"] or ''
          else :
            WeladeeData.employee.passportNumber = self.passport_id or ''

          if "taxID" in vals :
            WeladeeData.employee.taxID = vals["taxID"] or ''
          else :
            WeladeeData.employee.taxID = self.taxID or ''

          if "nationalID" in vals :
            WeladeeData.employee.nationalID = vals["nationalID"] or ''
          else :
            WeladeeData.employee.nationalID = self.nationalID or ''
          
          #2018-05-28 KPO use employee_code
          if "employee_code" in vals :
            WeladeeData.employee.code = vals["employee_code"] or ''
          else:
            WeladeeData.employee.code = self.employee_code or ''
            
          if "notes" in vals :
            WeladeeData.employee.note = vals["notes"] or ''
          else:
            WeladeeData.employee.note = self.notes or ''

          if "parent_id" in vals :
              manager = self.env['hr.employee'].browse( vals["parent_id"] )
              if manager:
                 WeladeeData.employee.managerID = int(manager.weladee_id)
              else:
                 WeladeeData.employee.managerID = 0
          else : 
              if self.parent_id:
                 WeladeeData.employee.managerID = int(self.parent_id.weladee_id)

          if "work_email" in vals :
            WeladeeData.employee.email = vals["work_email"] or ''
          else:
            WeladeeData.employee.email = self.work_email or ''

          if "job_id" in vals :
            positionData = self.env['hr.job'].browse( vals["job_id"] )
            if positionData :
              if positionData.weladee_id :
                WeladeeData.employee.positionid = int(positionData.weladee_id)
          else :
            if self.job_id:
              WeladeeData.employee.positionid = int(self.job_id.weladee_id)

          if "country_id" in vals :
            countryData = self.env['res.country'].browse( vals["country_id"] )
            if countryData :
               WeladeeData.employee.Nationality = countryData.name

          if "image" in vals:
              WeladeeData.employee.photo = vals["image"] or ''

          if "work_phone" in vals:
              if len(WeladeeData.employee.Phones) == 0:
                 WeladeeData.employee.Phones[:] = [vals['work_phone']]
              else:  
                 WeladeeData.employee.Phones[0] = vals['work_phone']

          #2018-10-29 KPO we don't sync 
          #  department
          #  photo
          # back to weladee    

      is_has_weladee = (self.weladee_id or '') != ""
      if "weladee_id" in vals:
         is_has_weladee = True

      #update data in odoo
      ret = super(weladee_employee, self).write( vals )
      
      if not is_has_weladee:
          WeladeeData.employee.lg = "en"          
          try:         
            result = stub.AddEmployee(WeladeeData, metadata=authorization)
            print ("New Weladee id : %s" % result.id)
            ret.write( {"weladee_id" : str(result.id), "weladee_profile" : "https://www.weladee.com/employee/" + str(result.id)  } )              
            _logger.info("Created new employee in weladee: %s" % result.id)
          except Exception as e:
            print("Add employee failed", e)
            _logger.error("Error while add employee to weladee: %s" % e)
      else:
          #send to grpc      
          try:
            wid = stub.UpdateEmployee(WeladeeData, metadata=authorization)
            print ("Updated Weladee Employee %s" % wid )
            _logger.info("Updated Weladee Employee: %s" % wid)
          except Exception as e:
            print("Update Weladee employee failed ",e)
            _logger.error("Failed update Weladee Employee: %s %s" % (self.weladee_id, e))

      return ret
  
  def open_weladee_employee(self):
    '''
    open weladee employee url
    '''
    if self.weladee_profile :
       return {
            'name': _("Weladee Profile"),
            'type': 'ir.actions.act_url',
            'url': self.weladee_profile,
            'target': 'new'
        }
    else :
      raise exceptions.UserError("This employee don't have weladee url.")

weladee_employee()