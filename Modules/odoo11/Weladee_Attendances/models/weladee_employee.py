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

class weladee_employee(models.Model):
  _description="synchronous Employee to weladee"
  _inherit = 'hr.employee'

  weladee_profile = fields.Char(string="Weladee Url",default="")
  work_email = fields.Char(string="Work Email", required=True)
  job_id = fields.Many2one('hr.job',string="Job Title", required=True)
  identification_id = fields.Char(string="Identification No", required=True)
  weladee_id = fields.Char(string="Weladee ID")
  country_id = fields.Many2one('res.country',string="Nationality (Country)", required=True)
  first_name_english = fields.Char(string="English First Name")
  last_name_english = fields.Char(string="English Last Name")
  first_name_thai = fields.Char(string="Thai First Name")
  last_name_thai = fields.Char(string="Thai Last Name")
  nick_name_english = fields.Char(string="English Nick Name")
  nick_name_thai = fields.Char(string="Thai Nick Name")
  receive_check_notification = fields.Boolean(string="Receive Check Notification")
  can_request_holiday = fields.Boolean(string="Can Request Holiday")
  active_employee = fields.Boolean(string="Active Employee")
  hasToFillTimesheet = fields.Boolean(string="Has To Fill Timesheet")
  passportNumber = fields.Char(string="Passport Number")
  taxID = fields.Char(string="TaxID")
  nationalID = fields.Char(string="NationalID")
  

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
  def create(self, vals):
    eid = super(weladee_employee,self).create(vals)

    if not "weladee_id" in vals:
      authorization = False
      authorization = self.get_api_key()
      #print("API : %s" % authorization)
      if authorization :
        if True :

            newEmployee = odoo_pb2.EmployeeOdoo()
            newEmployee.odoo.odoo_id = eid.id
            newEmployee.odoo.odoo_created_on = int(time.time())
            newEmployee.odoo.odoo_synced_on = int(time.time())

            if "first_name_english" in vals :
              newEmployee.employee.first_name_english = vals["first_name_english"]
            if "last_name_english" in vals :
              newEmployee.employee.last_name_english = vals["last_name_english"]

            if not "first_name_english" in vals and not "last_name_english" in vals :
              newEmployee.employee.first_name_english = ( vals["name"] ).split(" ")[0]
              if len( ( vals["name"] ).split(" ") ) > 1 :
                newEmployee.employee.last_name_english = ( vals["name"] ).split(" ")[1]
              else :
                newEmployee.employee.last_name_english = " "

            if "first_name_thai" in vals :
              newEmployee.employee.first_name_thai = vals["first_name_thai"]
            if "last_name_thai" in vals :
              newEmployee.employee.last_name_thai = vals["last_name_thai"]

            if "nick_name_english" in vals :
              newEmployee.employee.nickname_english = vals["nick_name_english"]
            if "nick_name_thai" in vals :
              newEmployee.employee.nickname_thai = vals["nick_name_thai"]

            if "identification_id" in vals :
              newEmployee.employee.code = vals["identification_id"]

            if vals["country_id"] :
              c_line_obj = self.env['res.country']
              cdata = c_line_obj.browse( vals["country_id"] )
              if cdata :
                if cdata.name :
                  newEmployee.employee.Nationality = cdata.name

            if vals["notes"] :
              newEmployee.employee.note = vals["notes"]

            if vals["work_email"] :
              newEmployee.employee.email = vals["work_email"]
            
            if "parent_id" in vals :
              manager = self.env['hr.employee'].browse( vals["parent_id"] )
              if manager :
                newEmployee.employee.managerID = int(manager.weladee_id)

            if vals["job_id"] :
              positionData = self.env['hr.job'].browse( vals["job_id"] )
              if positionData :
                if positionData.weladee_id :
                  newEmployee.employee.positionid = int(positionData.weladee_id)

            newEmployee.employee.lg = "en"
            newEmployee.employee.active = vals["active"]
            newEmployee.employee.receiveCheckNotification = vals["receive_check_notification"]
            newEmployee.employee.canRequestHoliday = vals["can_request_holiday"]
            newEmployee.employee.hasToFillTimesheet = vals["hasToFillTimesheet"]

            if vals["passportNumber"] :
              newEmployee.employee.passportNumber = vals["passportNumber"]

            if vals["taxID"] :
              newEmployee.employee.taxID = vals["taxID"]
            
            if vals["nationalID"] :
              newEmployee.employee.email = vals["nationalID"]


            print(newEmployee)

            try:
              result = stub.AddEmployee(newEmployee, metadata=authorization)
              print ("Weladee id : %s" % result.id)
              eid.write( {"weladee_id" : str(result.id) ,"weladee_profile" : "https://www.weladee.com/employee/" + str(result.id)  } )              
            except Exception as e:
              print("Add employee failed",e)

    return eid

  def write(self, vals):
    authorization = False
    authorization = self.get_api_key()
    #print("API : %s" % authorization)
    if not "weladee_id" in vals:
      if authorization :
        if True :
          print("----------")

          oldData = self.env['hr.employee'].browse( self.id )
          WeladeeData = False
          odooRequest = odoo_pb2.OdooRequest()
          odooRequest.odoo_id = int(self.id)
          for emp in stub.GetEmployees(odooRequest, metadata=authorization):
            print("----------")
            if emp :
              if emp.employee :
                  print( emp )
                  if str(emp.employee.ID) == self.weladee_id :
                    WeladeeData = emp.employee
                    
          if WeladeeData :
            newEmployee = odoo_pb2.EmployeeOdoo()
            newEmployee.odoo.odoo_id = self.id
            newEmployee.odoo.odoo_created_on = int(time.time())
            newEmployee.odoo.odoo_synced_on = int(time.time())
            
            if "first_name_english" in vals :
              newEmployee.employee.first_name_english = vals["first_name_english"]
            elif self.first_name_english :
              newEmployee.employee.first_name_english = self.first_name_english
            else :
              newEmployee.employee.first_name_english = WeladeeData.first_name_english

            if "last_name_english" in vals :
              newEmployee.employee.last_name_english = vals["last_name_english"]
            elif self.last_name_english :
              newEmployee.employee.first_name_english = self.last_name_english
            else :
              newEmployee.employee.last_name_english = WeladeeData.last_name_english

            if "first_name_thai" in vals :
              newEmployee.employee.first_name_thai = vals["first_name_thai"]
            elif self.first_name_thai :
              newEmployee.employee.first_name_thai = self.first_name_thai
            else :
              newEmployee.employee.first_name_thai = WeladeeData.first_name_thai

            if "last_name_thai" in vals :
              newEmployee.employee.last_name_thai = vals["last_name_thai"]
            elif self.last_name_thai :
              newEmployee.employee.last_name_thai = self.last_name_thai
            else :
              newEmployee.employee.last_name_thai = WeladeeData.last_name_thai

            if "nick_name_english" in vals :
              newEmployee.employee.nickname_english = vals["nick_name_english"]
            elif self.nick_name_english :
              newEmployee.employee.nickname_english = self.nick_name_english
            else :
              newEmployee.employee.nickname_english = WeladeeData.nickname_english

            if "nick_name_thai" in vals :
              newEmployee.employee.nickname_thai = vals["nick_name_thai"]
            elif self.nick_name_thai :
              newEmployee.employee.nickname_thai = self.nick_name_thai
            else :
              newEmployee.employee.nickname_thai = WeladeeData.nickname_thai

            if "active" in vals :
              newEmployee.employee.active = vals["active"]
            else :
             newEmployee.employee.active = self.active or WeladeeData.active

            print(vals)
            if "receive_check_notification" in vals :
               newEmployee.employee.receiveCheckNotification = vals["receive_check_notification"]
            else :
              newEmployee.employee.receiveCheckNotification = self.receive_check_notification or WeladeeData.receiveCheckNotification

            if "can_request_holiday" in vals :
              newEmployee.employee.canRequestHoliday = vals["can_request_holiday"]
            else :
              newEmployee.employee.canRequestHoliday = self.can_request_holiday or WeladeeData.canRequestHoliday

            if "hasToFillTimesheet" in vals :
              newEmployee.employee.hasToFillTimesheet = vals["hasToFillTimesheet"]
            else :
              newEmployee.employee.hasToFillTimesheet = self.hasToFillTimesheet or WeladeeData.hasToFillTimesheet

            if "passportNumber" in vals :
              newEmployee.employee.passportNumber = vals["passportNumber"]
            else :
              newEmployee.employee.passportNumber = self.passportNumber or WeladeeData.passportNumber

            if "taxID" in vals :
              newEmployee.employee.taxID = vals["taxID"]
            else :
              newEmployee.employee.taxID = self.taxID or WeladeeData.taxID

            if "nationalID" in vals :
              newEmployee.employee.nationalID = vals["nationalID"]
            else :
              newEmployee.employee.nationalID = self.nationalID or WeladeeData.nationalID
            

            if "identification_id" in vals :
              newEmployee.employee.code = vals["identification_id"]
            elif self.identification_id :
              newEmployee.employee.code = self.identification_id
            else :
              newEmployee.employee.code = WeladeeData.code
              
            if "notes" in vals :
              newEmployee.employee.note = vals["notes"]
            elif self.notes :
              newEmployee.employee.note = self.notes
            else :
              newEmployee.employee.note = WeladeeData.note

            if "parent_id" in vals :
              manager = self.env['hr.employee'].browse( vals["parent_id"] )
              if manager :
                newEmployee.employee.managerID = int(manager.weladee_id)
              else :
                newEmployee.employee.managerID = WeladeeData.managerID
            else : 
              newEmployee.employee.managerID = WeladeeData.managerID


            if "work_email" in vals :
              newEmployee.employee.email = vals["work_email"]
            elif self.work_email :
              newEmployee.employee.email = self.work_email
            else :
              newEmployee.employee.email = WeladeeData.email

            if "job_id" in vals :
              positionData = self.env['hr.job'].browse( vals["job_id"] )
              if positionData :
                if positionData.weladee_id :
                  newEmployee.employee.positionid = int(positionData.weladee_id)
                else :
                  newEmployee.employee.positionid = WeladeeData.positionid
              else :
                  newEmployee.employee.positionid = WeladeeData.positionid
            else :
              newEmployee.employee.positionid = WeladeeData.positionid

            if WeladeeData.ID :
              newEmployee.employee.ID = WeladeeData.ID
            if WeladeeData.user_name :
              newEmployee.employee.user_name = WeladeeData.user_name
            if WeladeeData.lineID :
              newEmployee.employee.lineID = WeladeeData.lineID
            if WeladeeData.FCMtoken :
              newEmployee.employee.FCMtoken = WeladeeData.FCMtoken
            if WeladeeData.phone_model :
              newEmployee.employee.phone_model = WeladeeData.phone_model
            if WeladeeData.phone_serial :
              newEmployee.employee.phone_serial = WeladeeData.phone_serial
            if WeladeeData.created_by :
              newEmployee.employee.created_by = WeladeeData.created_by
            if WeladeeData.updated_by :
              newEmployee.employee.updated_by = WeladeeData.updated_by
            if WeladeeData.photo :
              newEmployee.employee.photo = WeladeeData.photo
            if WeladeeData.lg :
              newEmployee.employee.lg = WeladeeData.lg
            if WeladeeData.application_level :
              newEmployee.employee.application_level = WeladeeData.application_level
            if WeladeeData.Phones :
              newEmployee.employee.Phones = WeladeeData.Phones
            if WeladeeData.rfid :
              newEmployee.employee.rfid = WeladeeData.rfid
            if WeladeeData.EmailValidated :
              newEmployee.employee.EmailValidated = WeladeeData.EmailValidated
            if WeladeeData.teamid :
              newEmployee.employee.teamid = WeladeeData.teamid
            if WeladeeData.gender :
              newEmployee.employee.gender = WeladeeData.gender
            if WeladeeData.token :
                newEmployee.employee.token = WeladeeData.token
            if WeladeeData.CanCheckTeamMember :
                newEmployee.employee.CanCheckTeamMember = WeladeeData.CanCheckTeamMember
            if WeladeeData.QRCode :
                newEmployee.employee.QRCode = WeladeeData.QRCode
            if WeladeeData.Nationality :
                newEmployee.employee.Nationality = WeladeeData.Nationality

            print(newEmployee)

            try:
              wid = stub.UpdateEmployee(newEmployee, metadata=authorization)
              print ("Updated Weladee Employee" )
            except Exception as e:
              print("Update employee failed",e)

    return super(weladee_employee, self).write( vals )
  
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

      authorization = False
      authorization = self.get_api_key()
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
    authorization = False
    authorization = self.get_api_key()
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
      authorization = self.get_api_key()
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
    authorization = self.get_api_key()
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
    authorization = False
    authorization = self.get_api_key()
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

