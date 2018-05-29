# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-Now Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import grpc
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

# Weladee grpc server address is hrpc.weladee.com:22443
creds = grpc.ssl_channel_credentials(weladee_grpc.weladee_certificate)
channel = grpc.secure_channel(weladee_grpc.weladee_address, creds)
stub = odoo_pb2_grpc.OdooStub(channel)
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
  #TODO: to remove
  identification_id = fields.Char(required=False)
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
            #2018-05-29 KPO when create weladee, employee can active only has password
            #WeladeeData.employee.Active = vals["active"]
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
    if self.weladee_profile :
      print("Url weladee profile is %s" % self.weladee_profile)
      webbrowser.open( self.weladee_profile )
    else :
      raise exceptions.UserError("This employee don't have weladee url.")

weladee_employee()

class weladee_job(models.Model):
  _description="synchronous position to weladee"
  _inherit = 'hr.job'

  weladee_id = fields.Char(string="Weladee ID")

  def get_api_key(self):
    line_obj = self.env['weladee_attendance.synchronous.setting']
    line_ids = line_obj.search([])
    authorization = False

    for sId in line_ids:
        dataSet = line_obj.browse(sId.id)
        if dataSet.api_key :
            authorization = [("authorization", dataSet.api_key)]
    return authorization

  @api.model
  def create(self, vals) :
    pid = super(weladee_job,self).create( vals )
    
    if not "weladee_id" in vals:

      authorization = get_api_key(self)
      #print("API : %s" % authorization)
      if authorization :
        if True :
          weladeePositions = {}
          odooRequest = odoo_pb2.OdooRequest()
          odooRequest.Force = True
          for position in stub.GetPositions(odooRequest, metadata=authorization):
            if position :
              if position.position.name_english :
                weladeePositions[ position.position.name_english ] = position.position.id

          if not vals["name"] in weladeePositions :
            newPosition = odoo_pb2.PositionOdoo()
            newPosition.odoo.odoo_id = pid.id
            newPosition.odoo.odoo_created_on = int(time.time())
            newPosition.odoo.odoo_synced_on = int(time.time())

            newPosition.position.name_english = vals["name"]
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
    authorization = get_api_key(self)
    #print("API : %s" % authorization)
    if not "weladee_id" in vals :
      if authorization :
        if True :
          if "name" in vals:
            weladeePositions = {}
            for position in stub.GetPositions(myrequest, metadata=authorization):
              if position :
                if position.position.name_english :
                  weladeePositions[ position.position.name_english ] = position.position.id

            if not vals["name"] in weladeePositions :
              newPosition = odoo_pb2.PositionOdoo()
              newPosition.odoo.odoo_id = self.id
              newPosition.odoo.odoo_created_on = int(time.time())
              newPosition.odoo.odoo_synced_on = int(time.time())

              newPosition.position.name_english = vals["name"]
              newPosition.position.active = True

              print(newPosition)
              try:
                result = stub.AddPosition(newPosition, metadata=authorization)
                print ("Added position on Weladee")
              except Exception as e:
                print("Add position failed",e)

    return pid
weladee_job()

class weladee_department(models.Model):
  _description="synchronous department to weladee"
  _inherit = 'hr.department'

  weladee_id = fields.Char(string="Weladee ID")

  def get_api_key(self):
    line_obj = self.env['weladee_attendance.synchronous.setting']
    line_ids = line_obj.search([])
    authorization = False

    for sId in line_ids:
        dataSet = line_obj.browse(sId.id)
        if dataSet.api_key :
            authorization = [("authorization", dataSet.api_key)]
    return authorization


  @api.model
  def create(self, vals ) :
    dId = super(weladee_department,self).create( vals )
    if not "weladee_id" in vals:
      authorization = False
      authorization = get_api_key(self)
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
    authorization = get_api_key(self)
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

class weladee_holidays(models.Model):
  _description="synchronous holidays to weladee"
  _inherit = 'hr.holidays'
  

  def get_api_key(self):
    line_obj = self.env['weladee_attendance.synchronous.setting']
    line_ids = line_obj.search([])
    authorization = False

    for sId in line_ids:
        dataSet = line_obj.browse(sId.id)
        if dataSet.api_key :
            authorization = [("authorization", dataSet.api_key)]
    return authorization

  @api.multi
  def action_validate( self ):
    mainHol = False
    authorization = get_api_key(self)
    #print("API : %s" % authorization)
    if authorization :
      if True :
        originHolidays = self.env['hr.holidays'].browse( self.id )
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        
        weladeeEmp = {}
        for emp in stub.GetEmployees(weladee_pb2.Empty(), metadata=authorization):
          if emp :
            if emp.odoo :
              if emp.odoo.odoo_id :
                if emp.employee :
                  weladeeEmp[ emp.odoo.odoo_id ] = emp.employee.ID

        if originHolidays :
          if originHolidays.date_from and originHolidays.date_to  :
            df = datetime.strptime( originHolidays.date_from, "%Y-%m-%d %H:%M:%S" )
            dt = datetime.strptime( originHolidays.date_to, "%Y-%m-%d %H:%M:%S" )

            delta = dt - df
            if delta.days + 1 > 1 :
              for i in range(delta.days + 1):
                odooDate = ( df + timedelta(days=i) ).strftime("%Y-%m-%d")
                weladeeDate = ( df + timedelta(days=i) ).strftime("%Y%m%d")
                if i == 0 :
                  if "date_from" in originHolidays :
                    vals = {"date_to" : originHolidays["date_from"],
                            "number_of_days_temp" : 1.0}

                    print(vals)
                    try:
                      mainHol = originHolidays.write( vals )
                      appr = super(weladee_holidays, self).action_validate( )
                      if appr :
                        newHoliday = odoo_pb2.HolidayOdoo()
                        newHoliday.odoo.odoo_id = self.id
                        newHoliday.odoo.odoo_created_on = int(time.time())
                        newHoliday.odoo.odoo_synced_on = int(time.time())

                        newHoliday.Holiday.name_english = originHolidays["name"]
                        newHoliday.Holiday.name_thai = originHolidays["name"]
                        newHoliday.Holiday.active = True

                        weladeeDate = ( df ).strftime("%Y%m%d")
                        newHoliday.Holiday.date = int( weladeeDate )
                        if originHolidays["employee_id"]["id"] in weladeeEmp :
                          newHoliday.Holiday.employeeid = weladeeEmp[ originHolidays["employee_id"]["id"] ]

                          print(newHoliday)
                          try:
                            result = stub.AddHoliday(newHoliday, metadata=authorization)
                            print ("Created Employee holiday" )
                          except Exception as ee :
                            print("Error when Create Employee holiday main : ",ee)
                        else :
                          print(weladeeEmp)
                          print(originHolidays["employee_id"]["id"])
                          print("Don't have emp id on Weladee")

                    except Exception as e:
                      print("Error on main approve : ",e)

                else :
                  vals = {}

                  vals["date_from"] = odooDate
                  vals["date_to"] = odooDate
                  vals["message_follower_ids"] = []
                  vals["message_ids"] = []
                  vals["number_of_days_temp"] = 1.0

                  if "name" in originHolidays :
                    vals["name"] = originHolidays["name"] + "(" + str(i+1) +")"
                  if "holiday_status_id" in originHolidays and "id" in originHolidays["holiday_status_id"] :
                    vals["holiday_status_id"] = originHolidays["holiday_status_id"]["id"]
                  if "employee_id" in originHolidays :
                    vals["employee_id"] = originHolidays["employee_id"]["id"]
                  if "payslip_status" in originHolidays :
                    vals["payslip_status"] = originHolidays["payslip_status"]
                  if "category_id" in originHolidays and "id" in originHolidays["category_id"] :
                    vals["category_id"] = originHolidays["category_id"]["id"]
                  if "type" in originHolidays :
                    vals["type"] = originHolidays["type"]
                  if "report_note" in originHolidays :
                    if originHolidays["report_note"] :
                      vals["notes"] = originHolidays["report_note"] + "\n*****\nSplit leave from " + originHolidays["name"] + "\n*****"
                    else :
                      vals["notes"] = "*****\nSplit leave from " + originHolidays["name"] + "\n*****"
                  else :
                    vals["notes"] = "*****\nSplit leave from " + originHolidays["name"] + "\n*****"

                  vals["report_note"] = vals["notes"]

                  if "department_id" in originHolidays  and "id" in originHolidays["department_id"] :
                    vals["department_id"] = originHolidays["department_id"]["id"]

                  try:
                    lid = self.env['hr.holidays'].create( vals )
                    appr = lid.action_validate( )
                    if appr :
                      newHoliday = odoo_pb2.HolidayOdoo()
                      newHoliday.odoo.odoo_id = lid.id
                      newHoliday.odoo.odoo_created_on = int(time.time())
                      newHoliday.odoo.odoo_synced_on = int(time.time())

                      newHoliday.Holiday.name_english = vals["name"]
                      newHoliday.Holiday.name_thai = vals["name"]
                      newHoliday.Holiday.date = int( weladeeDate )
                      newHoliday.Holiday.active = True

                      if vals["employee_id"] in weladeeEmp :
                        newHoliday.Holiday.employeeid = weladeeEmp[ vals["employee_id"] ]
                        print(newHoliday)
                        try:
                          result = stub.AddHoliday(newHoliday, metadata=authorization)
                          print ("Created Employee holiday" )
                        except Exception as ee :
                          print("Error when Create Employee holiday : ",ee)
                      else :
                        print("Don't have emp id on Weladee")

                  except Exception as e:
                      print("Error on submain approve : ",e)
            else :
              try:
                appr = super(weladee_holidays, self).action_validate( )
                if appr :
                  newHoliday = odoo_pb2.HolidayOdoo()
                  newHoliday.odoo.odoo_id = self.id
                  newHoliday.odoo.odoo_created_on = int(time.time())
                  newHoliday.odoo.odoo_synced_on = int(time.time())

                  newHoliday.Holiday.name_english = originHolidays["name"]
                  newHoliday.Holiday.name_thai = originHolidays["name"]
                  newHoliday.Holiday.active = True

                  weladeeDate = ( df ).strftime("%Y%m%d")
                  newHoliday.Holiday.date = int( weladeeDate )
                  if originHolidays["employee_id"]["id"] in weladeeEmp :
                    newHoliday.Holiday.employeeid = weladeeEmp[ originHolidays["employee_id"]["id"] ]

                    print(newHoliday)
                    try:
                      result = stub.AddHoliday(newHoliday, metadata=authorization)
                      print ("Created Employee holiday" )
                    except Exception as ee :
                      print("Error when Create Employee holiday main : ",ee)
                  else :
                    print(weladeeEmp)
                    print(originHolidays["employee_id"]["id"])
                    print("Don't have emp id on Weladee")

              except Exception as e:
                print("Error on main2 approve : ",e)



        return mainHol
weladee_holidays()

