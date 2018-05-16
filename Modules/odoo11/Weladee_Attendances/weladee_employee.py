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
from odoo import osv
from odoo import models, fields, api
from datetime import datetime,date, timedelta
import grpc
from . import odoo_pb2
from . import odoo_pb2_grpc
from . import weladee_pb2
import logging
import base64
import requests
import time

certificate = """-----BEGIN CERTIFICATE-----
MIIEkjCCA3qgAwIBAgIQCgFBQgAAAVOFc2oLheynCDANBgkqhkiG9w0BAQsFADA/
MSQwIgYDVQQKExtEaWdpdGFsIFNpZ25hdHVyZSBUcnVzdCBDby4xFzAVBgNVBAMT
DkRTVCBSb290IENBIFgzMB4XDTE2MDMxNzE2NDA0NloXDTIxMDMxNzE2NDA0Nlow
SjELMAkGA1UEBhMCVVMxFjAUBgNVBAoTDUxldCdzIEVuY3J5cHQxIzAhBgNVBAMT
GkxldCdzIEVuY3J5cHQgQXV0aG9yaXR5IFgzMIIBIjANBgkqhkiG9w0BAQEFAAOC
AQ8AMIIBCgKCAQEAnNMM8FrlLke3cl03g7NoYzDq1zUmGSXhvb418XCSL7e4S0EF
q6meNQhY7LEqxGiHC6PjdeTm86dicbp5gWAf15Gan/PQeGdxyGkOlZHP/uaZ6WA8
SMx+yk13EiSdRxta67nsHjcAHJyse6cF6s5K671B5TaYucv9bTyWaN8jKkKQDIZ0
Z8h/pZq4UmEUEz9l6YKHy9v6Dlb2honzhT+Xhq+w3Brvaw2VFn3EK6BlspkENnWA
a6xK8xuQSXgvopZPKiAlKQTGdMDQMc2PMTiVFrqoM7hD8bEfwzB/onkxEz0tNvjj
/PIzark5McWvxI0NHWQWM6r6hCm21AvA2H3DkwIDAQABo4IBfTCCAXkwEgYDVR0T
AQH/BAgwBgEB/wIBADAOBgNVHQ8BAf8EBAMCAYYwfwYIKwYBBQUHAQEEczBxMDIG
CCsGAQUFBzABhiZodHRwOi8vaXNyZy50cnVzdGlkLm9jc3AuaWRlbnRydXN0LmNv
bTA7BggrBgEFBQcwAoYvaHR0cDovL2FwcHMuaWRlbnRydXN0LmNvbS9yb290cy9k
c3Ryb290Y2F4My5wN2MwHwYDVR0jBBgwFoAUxKexpHsscfrb4UuQdf/EFWCFiRAw
VAYDVR0gBE0wSzAIBgZngQwBAgEwPwYLKwYBBAGC3xMBAQEwMDAuBggrBgEFBQcC
ARYiaHR0cDovL2Nwcy5yb290LXgxLmxldHNlbmNyeXB0Lm9yZzA8BgNVHR8ENTAz
MDGgL6AthitodHRwOi8vY3JsLmlkZW50cnVzdC5jb20vRFNUUk9PVENBWDNDUkwu
Y3JsMB0GA1UdDgQWBBSoSmpjBH3duubRObemRWXv86jsoTANBgkqhkiG9w0BAQsF
AAOCAQEA3TPXEfNjWDjdGBX7CVW+dla5cEilaUcne8IkCJLxWh9KEik3JHRRHGJo
uM2VcGfl96S8TihRzZvoroed6ti6WqEBmtzw3Wodatg+VyOeph4EYpr/1wXKtx8/
wApIvJSwtmVi4MFU5aMqrSDE6ea73Mj2tcMyo5jMd6jmeWUHK8so/joWUoHOUgwu
X4Po1QYz+3dszkDqMp4fklxBwXRsW10KXzPMTZ+sOPAveyxindmjkW8lGy+QsRlG
PfZ+G6Z6h7mjem0Y+iWlkYcV4PIWL1iwBi8saCbGS5jN2p8M+X+Q7UNKEkROb3N6
KOqkqm57TH2H3eDJAkSnh6/DNFu0Qg==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIDSjCCAjKgAwIBAgIQRK+wgNajJ7qJMDmGLvhAazANBgkqhkiG9w0BAQUFADA/
MSQwIgYDVQQKExtEaWdpdGFsIFNpZ25hdHVyZSBUcnVzdCBDby4xFzAVBgNVBAMT
DkRTVCBSb290IENBIFgzMB4XDTAwMDkzMDIxMTIxOVoXDTIxMDkzMDE0MDExNVow
PzEkMCIGA1UEChMbRGlnaXRhbCBTaWduYXR1cmUgVHJ1c3QgQ28uMRcwFQYDVQQD
Ew5EU1QgUm9vdCBDQSBYMzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEB
AN+v6ZdQCINXtMxiZfaQguzH0yxrMMpb7NnDfcdAwRgUi+DoM3ZJKuM/IUmTrE4O
rz5Iy2Xu/NMhD2XSKtkyj4zl93ewEnu1lcCJo6m67XMuegwGMoOifooUMM0RoOEq
OLl5CjH9UL2AZd+3UWODyOKIYepLYYHsUmu5ouJLGiifSKOeDNoJjj4XLh7dIN9b
xiqKqy69cK3FCxolkHRyxXtqqzTWMIn/5WgTe1QLyNau7Fqckh49ZLOMxt+/yUFw
7BZy1SbsOFU5Q9D8/RhcQPGX69Wam40dutolucbY38EVAjqr2m7xPi71XAicPNaD
aeQQmxkqtilX4+U9m5/wAl0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNV
HQ8BAf8EBAMCAQYwHQYDVR0OBBYEFMSnsaR7LHH62+FLkHX/xBVghYkQMA0GCSqG
SIb3DQEBBQUAA4IBAQCjGiybFwBcqR7uKGY3Or+Dxz9LwwmglSBd49lZRNI+DT69
ikugdB/OEIKcdBodfpga3csTS7MgROSR6cz8faXbauX+5v3gTt23ADq1cEmv8uXr
AvHRAosZy5Q6XkjEGB5YGV8eAlrwDPGxrancWYaLbumR9YbK+rlmM6pZW87ipxZz
R8srzJmwN0jP41ZL9c8PDHIyh8bwRLtTcm1D9SZImlJnt1ir/md2cXjbDaJWFBM5
JDGFoqgCWjBH4d1QB7wCCZAA62RjYJsWvIjJEubSfZGL+T0yjWW06XyxV3bqxbYo
Ob8VZRzI9neWagqNdwvYkQsEjgfbKbYK7p2CNTUQ
-----END CERTIFICATE-----
"""
address = "grpc.weladee.com:22443"
creds = grpc.ssl_channel_credentials(certificate)
channel = grpc.secure_channel(address, creds)
myrequest = weladee_pb2.EmployeeRequest()
#authorization = [("authorization", "fed4af9a-eaa0-4640-ac7e-50f7186ecd8c")]
stub = odoo_pb2_grpc.OdooStub(channel)

class weladee_employee(models.Model):
  _description="synchronous Employeeto weladee"
  _inherit = 'hr.employee'

  work_email = fields.Char(string="Work Email", required=True)
  job_id = fields.Many2one('hr.job',string="Job Title", required=True)
  identification_id = fields.Char(string="Identification No", required=True)

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

    authorization = False
    authorization = self.get_api_key()
    #print("API : %s" % authorization)
    if authorization :
      if True :
          wPos = {}
          for position in stub.GetPositions(myrequest, metadata=authorization):
            if position :
              if position.position.name_english :
                wPos[ position.position.name_english ] = position.position.id

          newEmployee = odoo_pb2.EmployeeOdoo()
          newEmployee.odoo.odoo_id = eid.id
          newEmployee.odoo.odoo_created_on = int(time.time())
          newEmployee.odoo.odoo_synced_on = int(time.time())

          newEmployee.employee.first_name_english = ( vals["name"] ).split(" ")[0]
          newEmployee.employee.last_name_english = ( vals["name"] ).split(" ")[1]

          newEmployee.employee.lg = "en"
          newEmployee.employee.active = False

          if vals["identification_id"] :
            newEmployee.employee.code = vals["identification_id"]
          if vals["notes"] :
            newEmployee.employee.note = vals["notes"]
          if vals["work_email"] :
            newEmployee.employee.email = vals["work_email"]
          if vals["job_id"] :
            positionData = self.env['hr.job'].browse( vals["job_id"] )
            if positionData :
              pName = positionData.name
              if pName in wPos :
                newEmployee.employee.positionid = wPos[ pName ]

                print(newEmployee)

                try:
                  result = stub.AddEmployee(newEmployee, metadata=authorization)
                  print ("Weladee id : %s" % result.id)
                except Exception as e:
                  print("Add employee failed",e)

      return eid

  def write(self, vals):
    authorization = False
    authorization = self.get_api_key()
    #print("API : %s" % authorization)
    if authorization :
      if True :
        print("----------")
        oldData = self.env['hr.employee'].browse( self.id )
        WeladeeData =False
        for emp in stub.GetEmployees(weladee_pb2.Empty(), metadata=authorization):
          if emp :
            if emp.odoo :
              if emp.odoo.odoo_id :
                if emp.odoo.odoo_id == self.id :
                  WeladeeData = emp.employee
        if WeladeeData :
          wPos = {}
          for position in stub.GetPositions(myrequest, metadata=authorization):
            if position :
              if position.position.name_english :
                wPos[ position.position.name_english ] = position.position.id

          newEmployee = odoo_pb2.EmployeeOdoo()
          newEmployee.odoo.odoo_id = self.id
          newEmployee.odoo.odoo_created_on = int(time.time())
          newEmployee.odoo.odoo_synced_on = int(time.time())

          if "name" in vals :
            newEmployee.employee.first_name_english = ( vals["name"] ).split(" ")[0]
            newEmployee.employee.last_name_english = ( vals["name"] ).split(" ")[1]
          else :
            newEmployee.employee.first_name_english = ( oldData["name"] ).split(" ")[0]
            newEmployee.employee.last_name_english = ( oldData["name"] ).split(" ")[1]

          if "identification_id" in vals :
            newEmployee.employee.code = vals["identification_id"]
          else :
            newEmployee.employee.code = oldData["identification_id"] or ""
          if "notes" in vals :
            newEmployee.employee.note = vals["notes"]
          else :
            newEmployee.employee.note = oldData["notes"] or ""

          if "work_email" in vals :
            newEmployee.employee.email = vals["work_email"]
          else :
            newEmployee.employee.email = oldData["work_email"] or ""

          jid = False
          if "job_id" in vals :
            positionData = self.env['hr.job'].browse( vals["job_id"] )
            if positionData :
              pName = positionData.name
              if pName in wPos :
                newEmployee.employee.positionid = wPos[ pName ]
                jid = True
              else :
                newEmployee.employee.positionid = WeladeeData.positionid
          else :
            newEmployee.employee.positionid = oldData["job_id"]["id"] or ""
            jid = True

          if WeladeeData.ID :
            newEmployee.employee.ID = WeladeeData.ID
          if WeladeeData.user_name :
            newEmployee.employee.user_name = WeladeeData.user_name
          if WeladeeData.first_name_thai :
            newEmployee.employee.first_name_thai = WeladeeData.first_name_thai
          if WeladeeData.last_name_thai :
            newEmployee.employee.last_name_thai = WeladeeData.last_name_thai
          if WeladeeData.managerID :
            newEmployee.employee.managerID = WeladeeData.managerID
          if WeladeeData.lineID :
            newEmployee.employee.lineID = WeladeeData.lineID
          if WeladeeData.nickname_english :
            newEmployee.employee.nickname_english = WeladeeData.nickname_english
          if WeladeeData.nickname_thai :
            newEmployee.employee.nickname_thai = WeladeeData.nickname_thai
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
          if WeladeeData.active :
            newEmployee.employee.active = WeladeeData.active
          if WeladeeData.photo :
            newEmployee.employee.photo = WeladeeData.photo
          if WeladeeData.lg :
            newEmployee.employee.lg = WeladeeData.lg
          if WeladeeData.application_level :
            newEmployee.employee.application_level = WeladeeData.application_level
          #if WeladeeData.positionid :
            #newEmployee.employee.positionid = WeladeeData.positionid
          if WeladeeData.Phones :
            newEmployee.employee.Phones = WeladeeData.Phones
          if WeladeeData.rfid :
            newEmployee.employee.rfid = WeladeeData.rfid
          if WeladeeData.EmailValidated :
            newEmployee.employee.EmailValidated = WeladeeData.EmailValidated
          if WeladeeData.teamid :
            newEmployee.employee.teamid = WeladeeData.teamid

          print(newEmployee)


          if jid :
              try:
                wid = stub.UpdateEmployee(newEmployee, metadata=authorization)
                print ("Updated Weladee Employee" )
              except Exception as e:
                print("Update employee failed",e)

    return super(weladee_employee, self).write( vals )
weladee_employee()

class weladee_job(models.Model):
  _description="synchronous position to weladee"
  _inherit = 'hr.job'

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

    authorization = False
    authorization = self.get_api_key()
    #print("API : %s" % authorization)
    if authorization :
      if True :
        weladeePositions = {}
        for position in stub.GetPositions(myrequest, metadata=authorization):
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
            newPosition.odoo.odoo_id = pid.id
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
        except Exception as e:
          print("Create department failed",e)
    return dId

  def write(self, vals ):
    oldData = self.env['hr.department'].browse( self.id )
    authorization = False
    authorization = self.get_api_key()
    #print("API : %s" % authorization)
    if authorization :
      if True :
        dept = False
        for dpm in stub.GetDepartments(weladee_pb2.Empty(), metadata=authorization):
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


