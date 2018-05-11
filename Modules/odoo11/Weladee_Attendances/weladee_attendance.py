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
authorization = [("authorization", "183df053-eebe-42af-b9e0-9397b52e04c3")]
stub = odoo_pb2_grpc.OdooStub(channel)
iteratorAttendance = []

class weladee_attendance(models.TransientModel):
    _name="weladee_attendance.synchronous"
    _description="synchronous Employee, Department, Holiday and attences"

    @api.multi
    def synchronousBtn(self):
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





    
class weladee_settings(models.TransientModel):
    _name="weladee_attendance.synchronous.setting"
    _description="Weladee settings"

     
weladee_attendance()
#weladee_settings()