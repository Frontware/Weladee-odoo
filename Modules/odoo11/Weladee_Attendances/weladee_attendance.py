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
#authorization = [("authorization", "fed4af9a-eaa0-4640-ac7e-50f7186ecd8c")]
stub = odoo_pb2_grpc.OdooStub(channel)
iteratorAttendance = []

class weladee_attendance(models.TransientModel):
    _name="weladee_attendance.synchronous"
    _description="synchronous Employee, Department, Holiday and attences"

    @api.multi
    def synchronousBtn(self):

        line_obj = self.env['weladee_attendance.synchronous.setting']
        line_ids = line_obj.search([])
        holiday_status_id = False
        authorization = False

        for sId in line_ids:
            dataSet = line_obj.browse(sId.id)
            if dataSet.holiday_status_id :
                holiday_status_id = dataSet.holiday_status_id
            if dataSet.api_key :
                authorization = [("authorization", dataSet.api_key)]

        
        if not holiday_status_id or not authorization :
            raise osv.except_osv(('Error'), ('Must to be set Leave Type on Weladee setting'))
        else:
            print( "Authorization : %s" % authorization )
            #List all position
            weladeePositions = {}
            odooPositions = {}
            weladeePositionName = {}

            print("-------------Positions")
            if True :
                for position in stub.GetPositions(myrequest, metadata=authorization):
                    if position :
                        if position.position.name_english :
                            weladeePositions[ position.position.name_english ] = position.position.id
                            weladeePositionName[ position.position.id ] = position.position.name_english
                            chk_position = self.env['hr.job'].search([ ('name','=',position.position.name_english )])
                            if not chk_position :
                                data = {"name" : position.position.name_english,
                                        "no_of_recruitment" : 1}
                                odoo_id_position = self.env['hr.job'].create(data)
                                print( "Insert position '%s' to odoo", position.position.name_english )

                position_line_obj = self.env['hr.job']
                position_line_ids = position_line_obj.search([])
                for posId in position_line_ids:
                    positionData = position_line_obj.browse(posId.id)
                    if positionData.name :
                        odooPositions[ positionData.name ] = positionData.id
                        if not positionData.name in weladeePositions :
                            newPosition = odoo_pb2.PositionOdoo()
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
            print("-------------Departments")
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
                                        odoo_id_department = self.env['hr.department'].create(data)
                                        
                                        print("Add department : %s to odoo the department id is %s" % (departmentName, odoo_id_department.id))
                                        sDepartment.append( odoo_id_department )
                                        # update odoo id
                                        updateDepartment = odoo_pb2.DepartmentOdoo()
                                        updateDepartment.odoo.odoo_id = odoo_id_department.id
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
                    department_line_obj = self.env['hr.department']
                    department_line_ids = department_line_obj.search([])
                    for deptId in department_line_ids:
                        deptData = department_line_obj.browse(deptId.id)
                        if deptData.name:
                            if deptData.id:
                                if not deptData.id in sDepartment:
                                    print( "%s don't have on Weladee" % deptData.name )
                                    newDepartment = odoo_pb2.DepartmentOdoo()
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
                employee_line_obj = self.env['hr.employee']
                employee_line_ids = employee_line_obj.search([])
                #check code Weladee on odoo
                for emp in stub.GetEmployees(weladee_pb2.Empty(), metadata=authorization):
                    if emp :
                        if emp.odoo :
                            if not emp.odoo.odoo_id :
                                print("------------------------------")
                                if emp.employee:
                                    if emp.employee.ID:
                                        photoBase64 = ''
                                        if emp.employee.photo:
                                            try :
                                                photoBase64 = base64.b64encode(requests.get(emp.employee.photo).content)
                                            except Exception as e:
                                                print("Error when load image : ",e)
                                            
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

                                        if emp.Badge:
                                            data["barcode"] = emp.Badge

                                        odoo_employee_id = False
                                        try:
                                            odoo_employee_id = self.env["hr.employee"].create( data )
                                        except Exception as e:
                                            print("photo url : %s" % emp.employee.photo)
                                            print( 'Error when import employee : %s' % e )

                                        if odoo_employee_id :
                                            odooIdEmps.append( odoo_employee_id.id )
                                            wEidTooEid[ emp.employee.ID ] = odoo_employee_id.id

                                            if odoo_employee_id.id :
                                                sEmployees[ odoo_employee_id.id ] = emp.employee
                                                newEmployee = odoo_pb2.EmployeeOdoo()
                                                newEmployee.odoo.odoo_id = odoo_employee_id.id
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
                        emp = employee_line_obj.browse(empId.id)
                        if emp.id:
                            print("------------------------------")
                            pos = False
                            if emp.job_id :
                                if emp.job_id.name :
                                    pos = emp.job_id.name
                            if not emp.id in odooIdEmps :
                                print("Add new employee %s with odoo id %s" % (emp.name, emp.id))
                                newEmployee = odoo_pb2.EmployeeOdoo()
                                newEmployee.odoo.odoo_id = emp.id
                                newEmployee.employee.first_name_english = (emp.name).split(" ")[0]
                                if len((emp.name).split(" ")) > 1 :
                                    newEmployee.employee.last_name_english = (emp.name).split(" ")[1]
                                else :
                                    newEmployee.employee.last_name_english = ""
                                if emp.work_email:
                                    newEmployee.employee.email = emp.work_email
                                if emp.notes:
                                    newEmployee.employee.note = emp.notes
                                if emp.work_email:
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
                                                    dateid = self.env["hr.holidays"].create( data )
                                                    print("odoo id : %s" % dateid.id)

                                                    newHoliday = odoo_pb2.HolidayOdoo()
                                                    newHoliday.odoo.odoo_id = dateid.id
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
                                                if False:
                                                    print("Company holiday")

                                                    data["enable"] = True
                                                    data["datefrom"] = fdte
                                                    data["dateto"] = fdte
                                                    dateid = self.env["fw_company.holiday"].create( data )
                                                    print("odoo id : %s" % dateid.id)

                                                    newHoliday = odoo_pb2.HolidayOdoo()
                                                    newHoliday.odoo.odoo_id = dateid.id
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



    
class weladee_settings(models.TransientModel):
    _name="weladee_attendance.synchronous.setting"
    _description="Weladee settings"

    '''
    purpose : get default holiday_status_id
    remarks :
    2017-09-26 CKA created
    '''
    def _get_holiday_status(self):
        line_obj = self.env['weladee_attendance.synchronous.setting']
        line_ids = line_obj.search([])
        holiday_status_id = False

        for sId in line_ids:
            dataSet = line_obj.browse(sId.id)
            if dataSet.holiday_status_id :
                holiday_status_id = dataSet.holiday_status_id

        return holiday_status_id

    def _get_api_key(self):
        line_obj = self.env['weladee_attendance.synchronous.setting']
        line_ids = line_obj.search([])
        api_key = False

        for sId in line_ids:
            dataSet = line_obj.browse(sId.id)
            if dataSet.api_key :
                api_key = dataSet.api_key

        return api_key


    holiday_status_id = fields.Many2one("hr.holidays.status", String="Leave Type",required=True,default=_get_holiday_status )
    api_key = fields.Char(string="API Key", required=True,default=_get_api_key )

    def saveBtn(self):
        print("--------Save-----------")

weladee_settings()
weladee_attendance()
