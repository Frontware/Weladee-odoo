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

class weladee_attendance(osv.osv):
      _name="weladee_attendance.synchronous"
      _description="synchronous Employee, Department, Holiday and attences"

      #purpose : synchronous data
      #remarks :
      #2017-07-18 CKA created
      def synchronousBtn(self, cr, uid, ids, context=None):
          print("synchronous datas")
          # Certificate to be downloaded from https://git.frontware.co.th/raw/Weladee/proto.git/master/certificates!grpc.weladee.com.chain.crt

          # Weladee grpc server address is hrpc.weladee.com:22443
          address = "grpc.weladee.com:22443"

          # Define a secure channel with embedded public certificate

          creds = grpc.ssl_channel_credentials(certificate)

          channel = grpc.secure_channel(address, creds)

          myrequest = weladee_pb2.EmployeeRequest()

          # Connect from Odoo
          # Place here the token specific to each company. It's called api_key in table company

          authorization = [("authorization", "bc7f3c00-bfa4-4ac2-810b-a11dca5ec48e")]

          stub = weladee_pb2_grpc.OdooStub(channel)

          #List all position
          odooPositions = {}
          weladeePositions = []

          print("Positions")
          if True :
              position_line_obj = self.pool.get('hr.job')
              position_line_ids = position_line_obj.search(cr, uid, [])
              for posId in position_line_ids:
                  positionData = position_line_obj.browse(cr, uid,posId ,context=context)
                  if positionData.name :
                      odooPositions[ positionData.name ] = positionData.id

              for position in stub.GetPositions(myrequest, metadata=authorization):
                  if position :
                      if position.position.name_english :
                          weladeePositions.append( position.position.name_english )
                          if not position.position.name_english in odooPositions :
                              positionName = position.position.name_english
                              chk_position = self.pool.get('hr.job').search(cr, uid, [('name','=',positionName)])
                              if not chk_position :
                                  data = {"name" : positionName,
                                          "no_of_recruitment" : 1}
                                  odoo_id_position = self.pool.get("hr.job").create(cr, uid, data, context=None)
                                  print ("Add position : %s" % positionName)
                                  odooPositions[ positionName ] = odoo_id_position

              for pName in odooPositions:
                  if not pName in weladeePositions :
                      newPosition = weladee_pb2.PositionOdoo()
                      newPosition.odoo.odoo_id = odooPositions[pName]
                      newPosition.odoo.odoo_created_on = int(time.time())
                      newPosition.odoo.odoo_synced_on = int(time.time())

                      newPosition.position.name_english = pName
                      newPosition.position.active = True

                      print(newPosition)
                      try:
                          result = stub.AddPosition(newPosition, metadata=authorization)
                          print ("Add position : %s" % pName)
                      except Exception as e:
                          print("Add position failed",e)

          # List all departments
          sDepartment = []
          print("Departments")
          if True :
              department_line_obj = self.pool.get('hr.department')
              department_line_ids = department_line_obj.search(cr, uid, [])
              # sync data from Weladee to odoo if odoo don't haave that data
              for dept in stub.GetDepartments(myrequest, metadata=authorization):
                  if dept:
                      if dept.department:
                          if dept.department.name_english:
                              departmentName = dept.department.name_english
                              sDepartment.append( departmentName )
                              chk_did = self.pool.get('hr.department').search(cr, uid, [('name','=',departmentName)])
                              odoo_id_department = False
                              if not chk_did :
                                  data = {"name" : departmentName
                                  }
                                  odoo_id_department = self.pool.get("hr.department").create(cr, uid, data, context=None)
                                  print("Add department : %s to odoo the department id is %s" %s (departmentName, odoo_id_department))
                              else :
                                  print("Found department %s in odoo but don't found odoo id from Weladee" % departmentName)
                                  deptData = department_line_obj.browse(cr, uid,chk_did ,context=context)
                                  odoo_id_department = deptData.id

                              if odoo_id_department :
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
                                      print("Update odoo department id",e)


              # sync data from odoo to Weladee
              if False :
                  for deptId in department_line_ids:
                      deptData = department_line_obj.browse(cr, uid,deptId ,context=context)
                      if deptData.name:
                          if not deptData.name in sDepartment:
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
          if False :
              sEmployees = {}
              for emp in stub.GetEmployees(weladee_pb2.Empty(), metadata=authorization):
                  if emp :
                      #if emp.odoo :
                          #if not emp.odoo.odoo_id :
                              if emp.employee:
                                  if emp.employee.ID:
                                    sEmployees[ str(emp.employee.ID) ] = emp.employee
                                    chk_id = self.pool.get('hr.employee').search(cr, uid, [('identification_id','=',emp.employee.ID)])
                                    if not chk_id:
                                        photoBase64 = ''
                                        if emp.employee.photo:
                                            print("photo url : %s" % emp.employee.photo)
                                            photoBase64 = base64.b64encode(requests.get(emp.employee.photo).content)
                                        data = { "name" : ( emp.employee.first_name_english or "" ) + " " + ( emp.employee.last_name_english or "" )
                                                ,"identification_id" :emp.employee.ID
                                                ,"notes": ( emp.employee.note or "" )
                                                ,"work_email":( emp.employee.email or "" )
                                              }
                                        if photoBase64:
                                            data["image"] = photoBase64
                                        odoo_employeeId = self.pool.get("hr.employee").create(cr, uid, data, context=None)

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
                                                print("Update odoo employee id",e)

              if False :
                  employee_line_obj = self.pool.get('hr.employee')
                  employee_line_ids = employee_line_obj.search(cr, uid, [])
                  for empId in employee_line_ids:
                      emp = employee_line_obj.browse(cr, uid,empId ,context=context)
                      if emp.identification_id:
                          if not str( emp.identification_id ) in sEmployees :
                              print("Add new employee %s with odoo id %s" % (emp.name, emp.id))
                              newEmployee = weladee_pb2.EmployeeOdoo()
                              newEmployee.odoo.odoo_id = emp.id
                              newEmployee.employee.first_name_english = (emp.name).split(" ")[0]
                              newEmployee.employee.last_name_english = (emp.name).split(" ")[1]
                              newEmployee.employee.email = emp.work_email
                              newEmployee.employee.note = emp.notes
                              newEmployee.employee.lg = "en"
                              newEmployee.employee.active = False
                              print(newEmployee)
                              try:
                                result = stub.AddEmployee(newEmployee, metadata=authorization)
                                print ("Weladee id : %s" % result.id)
                              except Exception as e:
                                print("Add employee failed",e)


          # List of Holiday
          print("Holiday")
          if False :
              sHoliday = []
              for hol in stub.GetHolidays(weladee_pb2.Empty(), metadata=authorization):
                  print(hol)
                  if not hol is None:
                      if not hol.Holiday is None:
                          if not hol.Holiday.name_english is None:
                              chk_date = self.pool.get('hr.holidays').search(cr, uid, [('name','=',hol.Holiday.name_english), ('date_from','=',hol.Holiday.date)])
                              if not chk_date:
                                  data = { "name" : hol.Holiday.name_english
                                      ,"date_from" : hol.Holiday.date
                                      ,"date_to"   :  hol.Holiday.date
                                           }
                                  dateid = self.pool.get("hr.holidays").create(cr, uid, data, context=None)
                                  print("odoo id : %s" % dateid)
                              sHoliday.append( str(hol.Holiday.name_english) )

              holiday_line_obj = self.pool.get('hr.holidays')
              holiday_line_ids = holiday_line_obj.search(cr, uid, [])
              for holydayId in holiday_line_ids:
                  holy = holiday_line_obj.browse(cr, uid,holydayId ,context=context)
                  if holy.date_from:
                      print(holy.date_from)



          # List of Company holiday
          #print("Company Holiday")
          #sCHoliday = []
          #for chol in stub.GetCompanyHolidays(weladee_pb2.Empty(), metadata=authorization):
              #print(chol)
              #if not chol is None:
                  #if not chol.Holiday is None:
                      #if not chol.Holiday.date is None:
                          #chk_date = self.pool.get('fw_company.holiday').search(cr, uid, [('datefrom','=',chol.Holiday.date)])
                          #if not chk_date:
                              #data = { "name" : chol.Holiday.name_english
                              #    ,"datefrom" : chol.Holiday.date
                              #    ,"dateto"   :  chol.Holiday.date
                              #    ,"enable":chol.Holiday.active
                              #         }
                              #dateid = self.pool.get("fw_company.holiday").create(cr, uid, data, context=None)
                              #print("odoo id : %s" % dateid)
                          #sCHoliday.append( str(chol.Holiday.date) )

          #holiday_line_obj = self.pool.get('fw_company.holiday')
          #holiday_line_ids = holiday_line_obj.search(cr, uid, [])
          #for holydayId in holiday_line_ids:
              #holy = holiday_line_obj.browse(cr, uid,holydayId ,context=context)
              #if holy.datefrom:
                  #print(holy.datefrom)




weladee_attendance()