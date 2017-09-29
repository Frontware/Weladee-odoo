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
from openerp.osv import fields
from openerp.osv import osv
import grpc
import logging
import weladee_pb2
import weladee_pb2_grpc
import base64
import requests
import time
import datetime
import threading
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

# Weladee grpc server address is hrpc.weladee.com:22443
address = "grpc.weladee.com:22443"
creds = grpc.ssl_channel_credentials(certificate)
channel = grpc.secure_channel(address, creds)
myrequest = weladee_pb2.EmployeeRequest()
authorization = [("authorization", "183df053-eebe-42af-b9e0-9397b52e04c3")]
stub = weladee_pb2_grpc.OdooStub(channel)
iteratorAttendance = []

class weladee_attendance(osv.osv):
      _name="weladee_attendance.synchronous"
      _description="synchronous Employee, Department, Holiday and attences"

      #purpose : synchronous data
      #remarks :
      #2017-07-18 CKA created
      def synchronousBtn(self, cr, uid, ids, context=None):
          print("synchronous datas")

          line_obj = self.pool.get('weladee_attendance.synchronous.setting')
          line_ids = line_obj.search(cr, uid, [])
          holiday_status_id = False

          for sId in line_ids:
              dataSet = line_obj.browse(cr, uid,sId, context=context)
              if dataSet.holiday_status_id :
                  holiday_status_id = dataSet.holiday_status_id

          if not holiday_status_id :
              raise osv.except_osv(('Error'), ('Must to be set Leave Type on Weladee setting'))
          else :
              #List all position
              weladeePositions = {}
              odooPositions = {}
              weladeePositionName = {}

              print("Positions")
              if True :
                  for position in stub.GetPositions(myrequest, metadata=authorization):
                      if position :
                          if position.position.name_english :
                              weladeePositions[ position.position.name_english ] = position.position.id
                              weladeePositionName[ position.position.id ] = position.position.name_english
                              chk_position = self.pool.get('hr.job').search(cr, uid, [('name','=',position.position.name_english)])
                              if not chk_position :
                                  data = {"name" : position.position.name_english,
                                          "no_of_recruitment" : 1}
                                  odoo_id_position = self.pool.get("hr.job").create(cr, uid, data, context=None)


                  position_line_obj = self.pool.get('hr.job')
                  position_line_ids = position_line_obj.search(cr, uid, [])
                  for posId in position_line_ids:
                      positionData = position_line_obj.browse(cr, uid,posId, context=context)
                      if positionData.name :
                          odooPositions[ positionData.name ] = positionData.id
                          if not positionData.name in weladeePositions :
                              newPosition = weladee_pb2.PositionOdoo()
                              newPosition.odoo.odoo_id = positionData.id
                              newPosition.odoo.odoo_created_on = int(time.time())
                              newPosition.odoo.odoo_synced_on = int(time.time())

                              newPosition.position.name_english = positionData.name
                              newPosition.position.active = True

                              print(newPosition)
                              try:
                                  result = stub.AddPosition(newPosition, metadata=authorization)
                                  weladeePositions[ positionData.name ] = result
                                  weladeePositionName[ result ] = positionData.name
                                  print( result  )
                                  print ("Add position : %s" % positionData.name)
                              except Exception as e:
                                  print("Add position failed",e)


              # List all departments
              sDepartment = []
              print("Departments")
              if True :
                  # sync data from Weladee to odoo if department don't have odoo id
                  for dept in stub.GetDepartments(myrequest, metadata=authorization):
                      if dept:
                          print("------------------------------")
                          if dept.odoo :
                              if not dept.odoo.odoo_id :
                                  if dept.department :
                                      if dept.department.name_english:
                                          departmentName = dept.department.name_english
                                          odoo_id_department = False
                                          data = {"name" : departmentName
                                                  }
                                          odoo_id_department = self.pool.get("hr.department").create(cr, uid, data, context=None)
                                          print("Add department : %s to odoo the department id is %s" % (departmentName, odoo_id_department))
                                          sDepartment.append( odoo_id_department )
                                          # update odoo id
                                          updateDepartment = weladee_pb2.DepartmentOdoo()
                                          updateDepartment.odoo.odoo_id = odoo_id_department
                                          updateDepartment.odoo.odoo_created_on = int(time.time())
                                          updateDepartment.odoo.odoo_synced_on = int(time.time())

                                          updateDepartment.department.id = dept.department.id
                                          updateDepartment.department.name_english = ( dept.department.name_english or "" )
                                          updateDepartment.department.name_thai = ( dept.department.name_thai or "" )
                                          if dept.department.managerid :
                                              updateDepartment.department.managerid = dept.department.managerid
                                          updateDepartment.department.active = ( dept.department.active or False )
                                          updateDepartment.department.code = ( dept.department.code or "" )
                                          updateDepartment.department.note = ( dept.department.note or "" )
                                          print( updateDepartment )
                                          try :
                                              result = stub.UpdateDepartment(updateDepartment, metadata=authorization)
                                              print ("Update odoo department id to Weladee : %s" % result.id)
                                          except Exception as e:
                                              print("Update odoo department id is failed",e)
                              else :
                                  sDepartment.append( dept.odoo.odoo_id )

                  # sync data from odoo to Weladee
                  if True :
                      department_line_obj = self.pool.get('hr.department')
                      department_line_ids = department_line_obj.search(cr, uid, [])
                      for deptId in department_line_ids:
                          deptData = department_line_obj.browse(cr, uid,deptId ,context=context)
                          if deptData.name:
                              if deptData.id:
                                  if not deptData.id in sDepartment:
                                      print( "%s don't have on Weladee" % deptData.name )
                                      newDepartment = weladee_pb2.DepartmentOdoo()
                                      newDepartment.odoo.odoo_id = deptData.id
                                      newDepartment.department.name_english = deptData.name
                                      print(newDepartment)
                                      try:
                                          result = stub.AddDepartment(newDepartment, metadata=authorization)
                                          print ("Weladee department id : %s" % result.id)
                                      except Exception as e:
                                          print("Add department failed",e)


              # List of employees
              print("Employees")
              sEmployees = {}
              wEidTooEid = {}
              if True :
                  odooIdEmps = []
                  employee_line_obj = self.pool.get('hr.employee')
                  employee_line_ids = employee_line_obj.search(cr, uid, [])
                  #check code Weladee on odoo
                  for emp in stub.GetEmployees(weladee_pb2.Empty(), metadata=authorization):
                      if emp :
                          if emp.odoo :
                              if not emp.odoo.odoo_id :
                                  print("------------------------------")
                                  if emp.employee:
                                      if emp.employee.ID:
                                        sEmployees[ emp.odoo.odoo_id ] = emp.employee
                                        photoBase64 = ''
                                        if emp.employee.photo:
                                            print("photo url : %s" % emp.employee.photo)
                                            photoBase64 = base64.b64encode(requests.get(emp.employee.photo).content)
                                        data = { "name" : ( emp.employee.first_name_english or "" ) + " " + ( emp.employee.last_name_english or "" )
                                                ,"identification_id" :(emp.employee.code or "" )
                                                ,"notes": ( emp.employee.note or "" )
                                                ,"work_email":( emp.employee.email or "" )
                                              }
                                        if emp.employee.positionid :
                                            if weladeePositionName[ emp.employee.positionid ] :
                                                posName = weladeePositionName[ emp.employee.positionid ]
                                                if odooPositions[ posName ] :
                                                    data[ "job_id" ] = odooPositions[ posName ]
                                        if photoBase64:
                                            data["image"] = photoBase64
                                        odoo_employeeId = self.pool.get("hr.employee").create(cr, uid, data, context=None)

                                        odooIdEmps.append( odoo_employeeId )
                                        wEidTooEid[ emp.employee.ID ] = odoo_employeeId

                                        if odoo_employeeId :

                                            newEmployee = weladee_pb2.EmployeeOdoo()
                                            newEmployee.odoo.odoo_id = odoo_employeeId
                                            newEmployee.odoo.odoo_created_on = int(time.time())
                                            newEmployee.odoo.odoo_synced_on = int(time.time())

                                            if emp.employee.ID :
                                                newEmployee.employee.ID = emp.employee.ID
                                            if emp.employee.email :
                                                newEmployee.employee.email = emp.employee.email
                                            if emp.employee.user_name :
                                                newEmployee.employee.user_name = emp.employee.user_name
                                            if emp.employee.last_name_english :
                                                newEmployee.employee.last_name_english = emp.employee.last_name_english
                                            if emp.employee.first_name_english :
                                                newEmployee.employee.first_name_english = emp.employee.first_name_english
                                            if emp.employee.first_name_thai :
                                                newEmployee.employee.first_name_thai = emp.employee.first_name_thai
                                            if emp.employee.last_name_thai :
                                                newEmployee.employee.last_name_thai = emp.employee.last_name_thai
                                            if emp.employee.managerID :
                                                newEmployee.employee.managerID = emp.employee.managerID
                                            if emp.employee.lineID :
                                                newEmployee.employee.lineID = emp.employee.lineID
                                            if emp.employee.nickname_english :
                                                newEmployee.employee.nickname_english = emp.employee.nickname_english
                                            if emp.employee.nickname_thai :
                                                newEmployee.employee.nickname_thai = emp.employee.nickname_thai
                                            if emp.employee.FCMtoken :
                                                newEmployee.employee.FCMtoken = emp.employee.FCMtoken
                                            if emp.employee.phone_model :
                                                newEmployee.employee.phone_model = emp.employee.phone_model
                                            if emp.employee.phone_serial :
                                                newEmployee.employee.phone_serial = emp.employee.phone_serial
                                            if emp.employee.code :
                                                newEmployee.employee.code = emp.employee.code
                                            if emp.employee.created_by :
                                                newEmployee.employee.created_by = emp.employee.created_by
                                            if emp.employee.updated_by :
                                                newEmployee.employee.updated_by = emp.employee.updated_by
                                            if emp.employee.active :
                                                newEmployee.employee.active = emp.employee.active
                                            if emp.employee.note :
                                                newEmployee.employee.note = emp.employee.note
                                            if emp.employee.photo :
                                                newEmployee.employee.photo = emp.employee.photo
                                            if emp.employee.lg :
                                                newEmployee.employee.lg = emp.employee.lg
                                            if emp.employee.application_level :
                                                newEmployee.employee.application_level = emp.employee.application_level
                                            if emp.employee.positionid :
                                                newEmployee.employee.positionid = emp.employee.positionid
                                            if emp.employee.Phones :
                                                newEmployee.employee.Phones = emp.employee.Phones
                                            if emp.employee.rfid :
                                                newEmployee.employee.rfid = emp.employee.rfid
                                            if emp.employee.EmailValidated :
                                                newEmployee.employee.EmailValidated = emp.employee.EmailValidated
                                            if emp.employee.teamid :
                                                newEmployee.employee.teamid = emp.employee.teamid
                                            print( newEmployee )
                                            try:
                                                result = stub.UpdateEmployee(newEmployee, metadata=authorization)
                                                print ("Update odoo employee id : %s" % result.id)
                                            except Exception as e:
                                                print("Update odoo employee id is failed",e)
                              else :
                                  odooIdEmps.append( emp.odoo.odoo_id )
                                  wEidTooEid[ emp.employee.ID ] = emp.odoo.odoo_id
                                  sEmployees[ emp.odoo.odoo_id ] = emp.employee

                  #add new employee on odoo to Weladee
                  if True :
                      for empId in employee_line_ids:
                          emp = employee_line_obj.browse(cr, uid,empId ,context=context)
                          if emp.id:
                              print("------------------------------")
                              pos = False
                              if emp.job_id :
                                  if emp.job_id.name :
                                      pos = emp.job_id.name
                              if not emp.id in odooIdEmps :
                                  print("Add new employee %s with odoo id %s" % (emp.name, emp.id))
                                  newEmployee = weladee_pb2.EmployeeOdoo()
                                  newEmployee.odoo.odoo_id = emp.id
                                  newEmployee.employee.first_name_english = (emp.name).split(" ")[0]
                                  if len((emp.name).split(" ")) > 1 :
                                    newEmployee.employee.last_name_english = (emp.name).split(" ")[1]
                                  else :
                                      newEmployee.employee.last_name_english = ""
                                  newEmployee.employee.email = emp.work_email
                                  newEmployee.employee.note = emp.notes
                                  newEmployee.employee.lg = "en"
                                  newEmployee.employee.active = False
                                  if pos :
                                      if weladeePositions[ pos ] :
                                          newEmployee.employee.positionid = weladeePositions[ pos ]
                                  print(newEmployee)
                                  try:
                                    result = stub.AddEmployee(newEmployee, metadata=authorization)
                                    print ("Weladee id : %s" % result.id)
                                  except Exception as e:
                                    print("Add employee failed",e)

              #List of Company holiday
              print("Company Holiday")
              if True :
                  for chol in stub.GetCompanyHolidays(weladee_pb2.Empty(), metadata=authorization):
                      if chol :
                          if chol.odoo :
                              if not chol.odoo.odoo_id :
                                  if chol.Holiday :
                                      print("----------------------------------")
                                      print(chol.Holiday)
                                      if chol.Holiday.date :
                                          if len( str (chol.Holiday.date ) ) == 8 :
                                              dte = str( chol.Holiday.date )
                                              fdte = dte[:4] + "-" + dte[4:6] + "-" + dte[6:8]
                                              data = { "name" : chol.Holiday.name_english }
                                              if chol.Holiday.employeeid :
                                                  print("Employee holiday")

                                                  data["holiday_status_id"] = holiday_status_id.id
                                                  data["holiday_type"] = "employee"
                                                  data["date_from"] = fdte
                                                  data["date_to"] = fdte
                                                  data["message_follower_ids"] = []
                                                  data["message_ids"] = []
                                                  data["number_of_days_temp"] = 1.0
                                                  data["payslip_status"] = False
                                                  data["notes"] = "Import from weladee"
                                                  data["report_note"] = "Import from weladee"
                                                  data["department_id"] = False
                                                  if chol.Holiday.employeeid in wEidTooEid :
                                                      empId = wEidTooEid[ chol.Holiday.employeeid ]
                                                      data["employee_id"] = empId
                                                      dateid = self.pool.get("hr.holidays").create(cr, uid, data, context=None)
                                                      print("odoo id : %s" % dateid)

                                                      newHoliday = weladee_pb2.HolidayOdoo()
                                                      newHoliday.odoo.odoo_id = dateid
                                                      newHoliday.odoo.odoo_created_on = int(time.time())
                                                      newHoliday.odoo.odoo_synced_on = int(time.time())

                                                      newHoliday.Holiday.id = chol.Holiday.id
                                                      newHoliday.Holiday.name_english = chol.Holiday.name_english
                                                      newHoliday.Holiday.name_thai = chol.Holiday.name_english
                                                      newHoliday.Holiday.date = chol.Holiday.date
                                                      newHoliday.Holiday.active = True

                                                      newHoliday.Holiday.employeeid = chol.Holiday.employeeid

                                                      print(newHoliday)
                                                      try:
                                                          result = stub.UpdateHoliday(newHoliday, metadata=authorization)
                                                          print ("Created Employee holiday" )
                                                      except Exception as ee :
                                                          print("Error when Create Employee holiday : ",ee)



                                                  else :
                                                      print("** Don't have employee id **")
                                              else :
                                                  print("Company holiday")

                                                  data["enable"] = True
                                                  data["datefrom"] = fdte
                                                  data["dateto"] = fdte
                                                  dateid = self.pool.get("fw_company.holiday").create(cr, uid, data, context=None)
                                                  print("odoo id : %s" % dateid)

                                                  newHoliday = weladee_pb2.HolidayOdoo()
                                                  newHoliday.odoo.odoo_id = dateid
                                                  newHoliday.odoo.odoo_created_on = int(time.time())
                                                  newHoliday.odoo.odoo_synced_on = int(time.time())

                                                  newHoliday.Holiday.id = chol.Holiday.id
                                                  newHoliday.Holiday.name_english = chol.Holiday.name_english
                                                  newHoliday.Holiday.name_thai = chol.Holiday.name_english
                                                  newHoliday.Holiday.date = chol.Holiday.date
                                                  newHoliday.Holiday.active = True

                                                  newHoliday.Holiday.employeeid = 0

                                                  print(newHoliday)
                                                  try:
                                                      result = stub.UpdateHoliday(newHoliday, metadata=authorization)
                                                      print ("Created Company holiday" )
                                                  except Exception as ee :
                                                      print("Error when Create Company holiday : ",ee)



              # List of Holiday
              print("Holiday")
              if False :
                  employee_line_obj = self.pool.get('hr.employee')
                  employee_line_ids = employee_line_obj.search(cr, uid, [])
                  for empId in employee_line_ids:
                      emp = employee_line_obj.browse(cr, uid,empId ,context=context)
                      if emp :
                          if emp.id :
                              gEmp = weladee_pb2.OdooRequest()
                              gEmp.odoo_id = emp.id
                              try:
                                  result = stub.GetHolidays(gEmp, metadata=authorization)
                              except Exception as e:
                                  print("Error add holiday failed", e)

                              if result :
                                  for hol in stub.GetHolidays(gEmp, metadata=authorization):
                                      if hol :
                                          if hol.odoo :
                                              if not hol.odoo.odoo_id :
                                                  if hol.Holiday.employeeid :
                                                      if hol.Holiday.employeeid in wEidTooEid :
                                                          oEmp = wEidTooEid[ hol.Holiday.employeeid ]
                                                          if hol.Holiday.date :
                                                              if hol.Holiday.date :
                                                                  if len( str (hol.Holiday.date ) ) == 8 :
                                                                      dte = str( hol.Holiday.date )
                                                                      fdte = dte[:4] + "-" + dte[4:6] + "-" + dte[6:8]
                                                                      data = { "name" : hol.Holiday.name_english,
                                                                               "datefrom" : fdte,
                                                                               "dateto"   :  fdte,
                                                                               "enable": True,
                                                                               "employee" : oEmp
                                                                               }
                                                                      print(data)
                                                                      hid = self.pool.get("hr.holidays").create(cr, uid, data, context=None)

              # List of Attendances
              print("Attendances")
              if True :
                  #self.manageAttendance(cr, uid, wEidTooEid)
                  self.manageAttendance(cr, uid, wEidTooEid)
                  ge = self.generators()
                  a = stub.SyncAttendance( ge , metadata=authorization )
                  print(a)
                  #for a in attendances:
                      #print a

      def generators(self):
          for i in iteratorAttendance :
              yield i

      def manageAttendance(self, cr, uid, wEidTooEid):
          att_line_obj = self.pool.get('hr.attendance')
          testCount = 0
          for att in stub.GetNewAttendance(weladee_pb2.Empty(), metadata=authorization):
              #if testCount <= 5 :
                  #testCount = testCount + 1
                  newAttendance = False
                  if att :
                      if att.odoo :
                          attendanceData = False
                          if not att.odoo.odoo_id :
                              newAttendance = True
                          else :
                              attendanceData = att_line_obj.browse(cr, uid, att.odoo.odoo_id, context=None)

                          if att.logevent :
                              try:
                                  #print(att.logevent)
                                  ac = False
                                  if att.logevent.action == "i" :
                                      ac = "sign_in"
                                  if att.logevent.action == "o" :
                                      ac = "sign_out"
                                  dte = datetime.datetime.fromtimestamp(
                                      att.logevent.timestamp
                                  ).strftime('%Y-%m-%d %H:%M:%S')
                                  acEid = False
                                  if att.logevent.employeeid in wEidTooEid :
                                     acEid = wEidTooEid[ att.logevent.employeeid ]
                                  packet = {"employee_id" : acEid,
                                            "name" : dte,
                                            "action" : ac}
                                  if acEid :
                                      if newAttendance :
                                          aid = False
                                          try :
                                              aid = self.pool.get("hr.attendance").create(cr, uid, packet, context=None)
                                              print ("Created log event on odoo with odoo id : %s" % aid)
                                          except Exception as e:
                                              print("Create log event is failed",e)
                                          #print(packet)
                                          # update odoo id
                                          if aid :
                                              syncLogEvent = weladee_pb2.LogEventOdooSync()
                                              syncLogEvent.odoo.odoo_id = aid
                                              syncLogEvent.odoo.odoo_created_on = int(time.time())
                                              syncLogEvent.odoo.odoo_synced_on = int(time.time())
                                              syncLogEvent.logid = att.logevent.id
                                              iteratorAttendance.append(syncLogEvent)

                                      else :
                                          if attendanceData :
                                              try :
                                                  self.pool.get("hr.attendance").write(cr, uid, att.odoo.odoo_id, packet, context=None)
                                                  print ("Updated log event on odoo")
                                              except Exception as e:
                                                  print("Updated log event is failed",e)

                              except Exception as e:
                                  print("Found problem when create attendance on odoo",e)
              #else :
                  #break


class weladee_settings(osv.osv):
    _name="weladee_attendance.synchronous.setting"
    _description="Weladee settings"

    '''
    purpose : get default holiday_status_id
    remarks :
    2017-09-26 CKA created
    '''
    def _get_holiday_status(self, cr, uid, context=None):
        line_obj = self.pool.get('weladee_attendance.synchronous.setting')
        line_ids = line_obj.search(cr, uid, [])
        holiday_status_id = False

        for sId in line_ids:
            dataSet = line_obj.browse(cr, uid,sId, context=context)
            if dataSet.holiday_status_id :
                holiday_status_id = dataSet.holiday_status_id

        return holiday_status_id


    _columns = {
        'holiday_status_id': fields.many2one("hr.holidays.status", "Leave Type",required=True),

    }

    _defaults = {

        'holiday_status_id': _get_holiday_status
    }

    def saveBtn(self, cr, uid, ids, context=None):
        print("--------Save-----------")





weladee_attendance()
weladee_settings()