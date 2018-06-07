# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import odoo
import logging
_logger = logging.getLogger(__name__)
import base64
import requests
import time
import threading
from datetime import datetime,date, timedelta

from odoo import osv
from odoo import models, fields, api, _
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError

from .grpcproto import odoo_pb2
from .grpcproto import odoo_pb2_grpc
from .grpcproto import weladee_pb2
from . import weladee_grpc
from . import weladee_employee

# Weladee grpc server address is hrpc.weladee.com:22443
stub = weladee_grpc.weladee_grpc_ctrl()
myrequest = weladee_pb2.EmployeeRequest()

def sync_position_data(weladee_position):
    '''
    position data to sync
    '''
    return {"name" : weladee_position.position.name_english,
            "weladee_id" : weladee_position.position.ID}

def sync_position(job_line_obj, myrequest, authorization):
    '''
    sync all positions from weladee

    '''
    #get change data from weladee
    try:
        for weladee_position in stub.GetPositions(myrequest, metadata=authorization):
            if weladee_position :
                if weladee_position.position.ID :
                    #search in odoo
                    #all active false,true and weladee match
                    job_line_ids = job_line_obj.search([("weladee_id", "=", weladee_position.position.ID)])
                    if not job_line_ids :
                        if weladee_position.position.name_english :
                            odoo_position = job_line_obj.search([('name','=',weladee_position.position.name_english )])
                            #_logger.info( "check this position '%s' in odoo %s, %s" % (position.position.name_english, chk_position, position.position.ID) )
                            if not odoo_position :
                                tmp = job_line_obj.create(sync_position_data(weladee_position))
                                _logger.info( "Insert position '%s' to odoo" % weladee_position.position.name_english )
                            else:
                                odoo_position.write({"weladee_id" : weladee_position.position.ID})
                        else:
                            _logger.error( "Error while create position '%s' to odoo: there is no english name")
                    else :
                        for odoo_position in job_line_ids :
                            odoo_position.write( sync_position_data(weladee_position) )
                            _logger.info( "Updated position '%s' to odoo" % weladee_position.position.name_english )
    except:
        raise UserError(_('Error while connect to GRPC Server, please check your connection or your Weladee API Key'))

    #scan in odoo if there is record with no weladee_id
    odoo_position_line_ids = job_line_obj.search([('weladee_id','=',False)])
    for positionData in odoo_position_line_ids:
        if positionData.name :
            if not positionData["weladee_id"] :
                newPosition = odoo_pb2.PositionOdoo()
                newPosition.odoo.odoo_id = positionData.id
                newPosition.odoo.odoo_created_on = int(time.time())
                newPosition.odoo.odoo_synced_on = int(time.time())

                newPosition.position.name_english = positionData.name
                newPosition.position.active = True
                #print(newPosition)
                try:
                    returnobj = stub.AddPosition(newPosition, metadata=authorization)
                    #print( result  )
                    positionData.write({'weladee_id':returnobj.id})
                    _logger.info("Added position to weladee : %s" % positionData.name)
                except Exception as e:
                    _logger.error("Add position '%s' failed : %s" % (positionData.name, e))

def sync_department_data(weladee_dept):
    '''
    department data to sync
    '''    
    return {"name" : weladee_dept.department.name_english,
            "weladee_id" : weladee_dept.department.ID
    }   

def sync_department(department_obj, myrequest, authorization):
    '''
    sync department with odoo and return the list
    '''    
    sDepartment = []
    #get change data from weladee
    for weladee_dept in stub.GetDepartments(myrequest, metadata=authorization):
        if weladee_dept :
            if weladee_dept.department.ID :
                #search in odoo
                odoo_department_ids = department_obj.search([("weladee_id", "=", weladee_dept.department.ID),'|',('active','=',False),('active','=',True)])
                if not odoo_department_ids :
                    if weladee_dept.department.name_english :
                        odoo_department = department_obj.search([('name','=',weladee_dept.department.name_english ),'|',('active','=',False),('active','=',True)])
                        if not odoo_department :
                            tmp = department_obj.create(sync_department_data(weladee_dept))
                            _logger.info( "Insert department '%s' to odoo" % weladee_dept.department.name_english )
                        else:
                            odoo_department.write({"weladee_id" : weladee_dept.department.ID})
                    else:
                        _logger.error( "Error while create department '%s' to odoo: there is no english name")
                else :
                    for odoo_department in odoo_department_ids :
                        odoo_department.write( sync_department_data(weladee_dept) )
                        _logger.info( "Updated department '%s' to odoo" % weladee_dept.department.name_english )

    #scan in odoo if there is record with no weladee_id
    odoo_department_ids = department_obj.search([('weladee_id','=',False),'|',('active','=',False),('active','=',True)])
    for odoo_department in odoo_department_ids:
        if odoo_department.name :
            if not odoo_department["weladee_id"] :
                newDepartment = odoo_pb2.DepartmentOdoo()
                newDepartment.odoo.odoo_id = odoo_department.id
                newDepartment.odoo.odoo_created_on = int(time.time())
                newDepartment.odoo.odoo_synced_on = int(time.time())

                newDepartment.department.name_english = odoo_department.name
                newDepartment.department.active = True
                #print(newPosition)
                try:
                    returnobj = stub.AddDepartment(newDepartment, metadata=authorization)
                    #print( result  )
                    odoo_department.write({'weladee_id':returnobj.id})
                    _logger.info("Added department to weladee : %s" % odoo_department.name)
                except Exception as e:
                    _logger.error("Add department '%s' failed : %s" % (odoo_department.name, e))

    return  sDepartment

def sync_employee_data(emp, job_obj, department_obj, country):
    '''
    employee data to sync
    '''    
    photoBase64 = ''
    if emp.employee.photo:
        try :
            photoBase64 = base64.b64encode(requests.get(emp.employee.photo).content)
        except Exception as e:
            _logger.error("Error when load image : %s" % e)
    
    #2018-06-07 KPO don't sync note back        
    data = { "name" : ( emp.employee.first_name_english or "" ) + " " + ( emp.employee.last_name_english or "" )
            ,"employee_code" :(emp.employee.code or "" )
            ,"weladee_profile" : "https://www.weladee.com/employee/" + str(emp.employee.ID)
            ,"work_email":( emp.employee.email or "" )
            ,"first_name_english":emp.employee.first_name_english
            ,"last_name_english":emp.employee.last_name_english
            ,"first_name_thai":emp.employee.first_name_thai
            ,"last_name_thai":emp.employee.last_name_thai
            ,"nick_name_english":emp.employee.nickname_english
            ,"nick_name_thai":emp.employee.nickname_thai
            ,"active": emp.employee.Active
            ,"receive_check_notification": emp.employee.receiveCheckNotification
            ,"can_request_holiday": emp.employee.canRequestHoliday
            ,"hasToFillTimesheet": emp.employee.hasToFillTimesheet
            ,"weladee_id":emp.employee.ID
            }
    
    if emp.employee.passportNumber :
        data["passport_id"] = emp.employee.passportNumber
    if emp.employee.taxID :
        data["taxID"] = emp.employee.taxID
    if emp.employee.nationalID :
        data["nationalID"] = emp.employee.nationalID
        
    if emp.employee.positionid :
        job_datas = job_obj.search( [("weladee_id","=", emp.employee.positionid )] )
        if job_datas :
            for jdatas in job_datas :
                data[ "job_id" ] = jdatas.id
    
    if emp.DepartmentID :
        dep_datas = department_obj.search( [("weladee_id","=", emp.DepartmentID ),'|',('active','=',False),('active','=',True)] )
        if dep_datas :
            for ddatas in dep_datas :
                data[ "department_id" ] = ddatas.id

    if photoBase64:
        data["image"] = photoBase64

    if emp.Badge:
        data["barcode"] = emp.Badge

    #2018-05-29 KPO if active = false set barcode to false
    if not emp.employee.Active:
       data["barcode"] = False 

    if emp.employee.Nationality:
        if emp.employee.Nationality.lower() in country :
            data["country_id"] = country[ emp.employee.Nationality.lower() ]
    #print (emp.employee)
    if emp.employee.Phones:
       data["work_phone"] = emp.employee.Phones[0]
       #print(emp.employee.Phones)
       #print(emp.employee.Phones[0])
       
    #2018-06-01 KPO if application level >=2 > manager   
    data["manager"] = emp.employee.application_level >= 2

    return data

def sync_employee(job_obj, employee_obj, department_obj, country, authorization, return_managers):
    '''
    sync data from employee
    '''
    #get change data from weladee
    for weladee_emp in stub.GetEmployees(weladee_pb2.Empty(), metadata=authorization):
        if weladee_emp and weladee_emp.employee:
            #TODO: Debug
            #if weladee_emp.employee.code != 'TCO-W01157': continue

            #search in odoo
            odoo_emp_ids = employee_obj.search([("weladee_id", "=", weladee_emp.employee.ID),'|',('active','=',False),('active','=',True)])
            if not odoo_emp_ids :
                newid = employee_obj.create( sync_employee_data(weladee_emp, job_obj, department_obj, country) ) 
                return_managers[ newid.id ] = weladee_emp.employee.managerID

                _logger.info( "Insert employee '%s' to odoo" % weladee_emp.employee.user_name )
            else :
                for odoo_emp_id in odoo_emp_ids :
                    odoo_emp_id.write( sync_employee_data(weladee_emp, job_obj, department_obj, country) )
                    return_managers[ odoo_emp_id.id ] = weladee_emp.employee.managerID
                    _logger.info( "Updated employee '%s' to odoo" % weladee_emp.employee.user_name )

    #scan in odoo if there is record with no weladee_id
    odoo_emp_ids = employee_obj.search([('weladee_id','=',False),'|',('active','=',False),('active','=',True)])
    for odoo_emp_id in odoo_emp_ids:
        if not odoo_emp_id["weladee_id"] :

            newEmployee = odoo_pb2.EmployeeOdoo()
            newEmployee.odoo.odoo_id = odoo_emp_id.id
            newEmployee.odoo.odoo_created_on = int(time.time())
            newEmployee.odoo.odoo_synced_on = int(time.time())

            newEmployee.employee.first_name_english = odoo_emp_id.first_name_english or ''
            newEmployee.employee.last_name_english = odoo_emp_id.last_name_english or ''
            newEmployee.employee.first_name_thai = odoo_emp_id.first_name_thai or ''
            newEmployee.employee.last_name_thai = odoo_emp_id.last_name_thai or ''
            
            newEmployee.employee.email = odoo_emp_id.work_email or ''
            #2018-06-07 KPO don't sync note back
            newEmployee.employee.lg = "en"
            newEmployee.employee.Active = odoo_emp_id.active
            if odoo_emp_id.work_phone:
               newEmployee.employee.Phones[:] = [odoo_emp_id.work_phone]

            if odoo_emp_id.job_id and odoo_emp_id.job_id.weladee_id:
                newEmployee.employee.positionid = int(odoo_emp_id.job_id.weladee_id or '0')

            try:
                result = stub.AddEmployee(newEmployee, metadata=authorization)
                
                odoo_emp_id.write({'weladee_id':result.id})
                _logger.info("Added employee to weladee : %s" % odoo_emp_id.name)
            except Exception as e:
                _logger.error("Add employee '%s' failed : %s" % (odoo_emp_id.name, e))
    
def sync_manager(employee_obj, weladee_managers, authorization):
    '''
    sync employee's manager
    '''
    #look only changed employees
    odoo_emps_change = [x for x in weladee_managers]

    odoo_emps = employee_obj.search(['|',('id','in',odoo_emps_change),('active','=',False),('active','=',True)])
    for odoo_emp in odoo_emps :
        if odoo_emp.id and odoo_emp.id in weladee_managers :

            odoo_manager = employee_obj.search( [("weladee_id","=", weladee_managers[odoo_emp.id] ),'|',("active","=",False),("active","=",True)] )

            try:
                tmp = odoo_emp.write( {"parent_id": int(odoo_manager.id) } )
                _logger.info("Updated manager of %s" % odoo_emp.name)
            except Exception as e:
                _logger.error("Update manager of %s failed : %s" % (odoo_emp.name, e))
                            

def sync_holiday(employee_line_obj, managers, authorization):
    pass
'''
#List of Company holiday
print("Company Holiday And Employee holiday")
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
                                    #if chol.Holiday.employeeid in wEidTooEid :
                                        #empId = wEidTooEid[ chol.Holiday.employeeid ]
                                    if self.weladeeEmpIdToOdooId( chol.Holiday.employeeid  ) :
                                        empId =  self.weladeeEmpIdToOdooId( chol.Holiday.employeeid  )
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
                                    if True:
                                        print("Company holiday")
                                        holiday_line_obj = self.env['weladee_attendance.company.holidays']
                                        holiday_line_ids = holiday_line_obj.search( [ ('company_holiday_date','=', fdte )] )

                                        if not holiday_line_ids :
                                            data = { 'company_holiday_description' :  chol.Holiday.name_english,
                                                    'company_holiday_active' : True,
                                                    'company_holiday_date' : fdte
                                            }
                                            dateid = self.env["weladee_attendance.company.holidays"].create( data )
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
'''

class weladee_attendance(models.TransientModel):
    _name="weladee_attendance.synchronous"
    _description="synchronous Employee, Department, Holiday and attendance"

    @api.multi
    def synchronousBtn(self):
        _logger.info("Start sync..")
        authorization, holiday_status_id = weladee_employee.get_api_key(self)
                
        if not holiday_status_id or not authorization :
            raise exceptions.UserError('Must to be set Leave Type on Weladee setting')
        else:

            _logger.info("Start sync...")

            _logger.info("Start sync...Positions")
            job_obj = self.env['hr.job']    
            sync_position(job_obj, myrequest, authorization)

            _logger.info("Start sync...Departments")
            department_obj = self.env['hr.department']    
            sync_department(department_obj, myrequest, authorization)

            _logger.info("Loading...Countries")
            country = {}
            country_line_ids = self.env['res.country'].search([])
            for cu in country_line_ids:
                if cu.name :
                    country[ cu.name.lower() ] = cu.id

            _logger.info("Start sync...Employee")
            return_managers = {}
            emp_obj = self.env['hr.employee']    
            sync_employee(job_obj, emp_obj, department_obj, country, authorization, return_managers)

            _logger.info("Start sync...Manager")
            sync_manager(emp_obj, return_managers, authorization)
            
    def generators(self, iteratorAttendance):
          for i in iteratorAttendance :
              yield i

    def weladeeEmpIdToOdooId(self, weladeeId) :
        odooid = False
        line_obj = self.env['hr.employee']
        line_ids = line_obj.search([("weladee_id", "=", weladeeId)])
        for cu in line_ids:
             employee_datas = line_obj.browse( cu )
             if employee_datas :
                 odooid = employee_datas.id
        if odooid :
            return odooid.id
        else :
            return odooid

    def manageAttendance(self, wEidTooEid, authorization):
        iteratorAttendance = []
        att_line_obj = self.env['hr.attendance']
        testCount = 0
        lastAttendance = False
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
                            attendanceData = att_line_obj.browse( att.odoo.odoo_id )

                        if att.logevent :
                            try:
                                print("------------[ logevent ]----------------")
                                print(att.logevent)
                                print("----------------------------")
                                ac = False
                                if att.logevent.action == "i" :
                                    ac = "sign_in"
                                if att.logevent.action == "o" :
                                    ac = "sign_out"
                                dte = datetime.datetime.fromtimestamp(
                                    att.logevent.timestamp
                                ).strftime('%Y-%m-%d %H:%M:%S')
                                acEid = False
                                #if att.logevent.employeeid in wEidTooEid :
                                    #acEid = wEidTooEid[ att.logevent.employeeid ]
                                if self.weladeeEmpIdToOdooId( att.logevent.employeeid ) :
                                    acEid =  self.weladeeEmpIdToOdooId( att.logevent.employeeid )
                                packet = {"employee_id" : acEid}
                                if acEid :
                                    if newAttendance :                 
                                        aid = False
                                        try :
                                            attendace_odoo_id = False
                                            if att.logevent.action == "i" :
                                                packet["check_in"] = dte
                                                print( packet )
                                                check_dp = self.env['hr.attendance'].search( [ ('employee_id','=', acEid ),('check_in','=', dte ) ] )
                                                if not check_dp :
                                                    try :
                                                        aid = self.env["hr.attendance"].create( packet )
                                                        lastAttendance = aid
                                                        attendace_odoo_id = aid.id
                                                        print ("Created check in : %s" % aid.id)
                                                    except Exception as e:
                                                        print ("Error when create check in. : %s" %(e))
                                                else :
                                                    print ("Check in duplicate.")
                                            else :
                                                if lastAttendance :
                                                    oldAttendance = self.env["hr.attendance"].browse( lastAttendance.id )
                                                    if oldAttendance :
                                                        packet = {"check_in" : oldAttendance.check_in,
                                                                "check_out" : dte
                                                        }
                                                        try :
                                                            print( packet )
                                                            oldAttendance.write( packet )
                                                            attendace_odoo_id = lastAttendance.id
                                                            lastAttendance = False
                                                            print ("Updated check out.")
                                                        except Exception as e:
                                                            print ("Error when fill check out. : %s" %(e) )
                                                else :
                                                    print ("Receive checkout with lastAttendance is False")

                                            if attendace_odoo_id :
                                                print("Update odoo id")
                                                syncLogEvent = odoo_pb2.LogEventOdooSync()
                                                syncLogEvent.odoo.odoo_id = attendace_odoo_id
                                                syncLogEvent.odoo.odoo_created_on = int(time.time())
                                                syncLogEvent.odoo.odoo_synced_on = int(time.time())
                                                syncLogEvent.logid = att.logevent.id
                                                iteratorAttendance.append(syncLogEvent)

                                        except Exception as e:
                                            print("Create log event is failed",e)

                                    else :
                                        if attendanceData :
                                            if att.logevent.action == "i" :
                                                attendanceData["check_in"] = dte
                                            elif att.logevent.action == "o" :
                                                attendanceData["check_out"] = dte
                                            try :
                                                attendanceData.write( attendanceData )
                                                print ("Updated log event on odoo")
                                            except Exception as e:
                                                print("Updated log event is failed",e)

                                            print("Update odoo id")
                                            syncLogEvent = odoo_pb2.LogEventOdooSync()
                                            syncLogEvent.odoo.odoo_id = attendanceData.id
                                            syncLogEvent.odoo.odoo_created_on = int(time.time())
                                            syncLogEvent.odoo.odoo_synced_on = int(time.time())
                                            syncLogEvent.logid = att.logevent.id
                                            iteratorAttendance.append(syncLogEvent)

                            except Exception as e:
                                print("Found problem when create attendance on odoo",e)

        if len( iteratorAttendance ) > 0 :
            #print("CKAA %s" % (iteratorAttendance))
            ge = self.generators(iteratorAttendance)
            a = stub.SyncAttendance( ge , metadata=authorization )
            print(a)
    
weladee_attendance()
