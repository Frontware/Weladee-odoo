# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import requests
import base64
import traceback
import subprocess
from datetime import datetime

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info 

def sync_employee_data_gender(weladee_emp):
    '''
    convert weladee employee gender to odoo
    '''
    if weladee_emp.employee.Gender == 'm':
        return 'male'
    elif weladee_emp.employee.Gender == 'f':        
        return 'female'
    else:
        return 'other'

def sync_employee_data_marital(weladee_emp):
    '''
    convert weladee employee marital to odoo
    '''
    return weladee_pb2.MaritalStatus.Name(weladee_emp.employee.MaritalStatus).lower()

def sync_employee_data_religion(weladee_emp):
    '''
    convert weladee employee religion to odoo
    '''
    return weladee_pb2.Religion.Name(weladee_emp.employee.Religion)

def sync_employee_data_military(weladee_emp):
    '''
    convert weladee employee military status to odoo
    '''
    return weladee_pb2.MilitaryStatus.Name(weladee_emp.employee.MilitaryStatus)

def new_employee_data_gender(gender):
    '''
    convert odoo employee gender to weladee
    '''
    if gender == 'male':
        return 'm'
    elif gender == 'female':
        return 'f'
    else:
        return 'u'

def new_employee_data_marital(marital):
    '''
    convert odoo employee marital to weladee
    '''
    for k in weladee_pb2.MaritalStatus.keys():
        if k.lower()  == marital:
           return weladee_pb2.MaritalStatus.Value(k)
    return False

def new_employee_data_religion(religion):
    '''
    convert odoo employee religion to weladee
    '''    
    return weladee_pb2.Religion.Value(religion)

def new_employee_data_military(military):
    '''
    convert odoo employee military to weladee
    '''
    return weladee_pb2.MilitaryStatus.Value(military)

def sync_employee_data(weladee_employee, req):
    '''
    employee data to sync

    remarks:

    2018-06-14 KPO sync qrcode from weladee
    '''    
    photoBase64 = ''
    if weladee_employee.employee.photo:
        bytese = False
        bytesa = False
        try :
            process = subprocess.Popen(['convert',
                                        '-',
                                        'png:-'],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)
            bytesa, bytese= process.communicate(input=requests.get(weladee_employee.employee.photo).content)
            photoBase64 = base64.b64encode(bytesa)

        except Exception as e:
            sync_logdebug(req.context_sync, "image : %s" % weladee_employee.employee.photo)
            sync_logerror(req.context_sync, "Error when load image %s : %s" % (weladee_employee.employee.photo,bytese or e or 'undefined'))
    
    #2018-06-07 KPO don't sync note back   
    #2018-06-21 KPO get team but don't sync back     
    data = { "name" : " ".join([weladee_employee.employee.first_name_english or '', weladee_employee.employee.last_name_english or "" ])
            ,"first_name_english":weladee_employee.employee.first_name_english
            ,"last_name_english":weladee_employee.employee.last_name_english
            ,"first_name_thai":weladee_employee.employee.first_name_thai
            ,"last_name_thai":weladee_employee.employee.last_name_thai
            ,"nick_name_english":weladee_employee.employee.nickname_english
            ,"nick_name_thai":weladee_employee.employee.nickname_thai
            ,"employee_code" : weladee_employee.employee.Code
            ,"weladee_profile" : "https://www.weladee.com/employee/%s" % weladee_employee.employee.ID
            ,"work_email":( weladee_employee.employee.email or weladee_employee.employee.user_name )
            ,"active": weladee_employee.employee.Active
            ,"receive_check_notification": weladee_employee.employee.receiveCheckNotification
            ,"can_request_holiday": weladee_employee.employee.CanRequestHoliday
            ,"hasToFillTimesheet": weladee_employee.employee.HasToFillTimesheet
            ,"weladee_id":weladee_employee.employee.ID
            ,"employee_team":weladee_employee.employee.TeamName
            ,"qr_code":weladee_employee.employee.QRCode
            ,"gender": sync_employee_data_gender(weladee_employee)
            ,"timesheet_cost":weladee_employee.employee.HourlyCost
            ,'send2-weladee':False}

    if weladee_employee.employee.Nationality:
        if len(weladee_employee.employee.Nationality) == 2 and weladee_employee.employee.Nationality in req.country :
            data["country_id"] = req.country[ weladee_employee.employee.Nationality ]
        else:
           data["country_name"] = weladee_employee.employee.Nationality

    #fixed contraint problem when empty
    if data['employee_code'] == '': data['employee_code'] = False
    if data['work_email'] == '': data['work_email'] = False

    if weladee_employee.employee.PositionID :
        job_datas = req.job_obj.search( [("weladee_id","=", weladee_employee.employee.PositionID )] )
        if job_datas :
            for jdatas in job_datas :
                data[ "job_id" ] = jdatas.id

    if weladee_employee.employee.Birthday > 0:
        data["birthday"] = datetime.fromtimestamp( weladee_employee.employee.Birthday )
    else:
        data["birthday"] = False

    data["passport_id"] = weladee_employee.employee.PassportNumber
    data["taxID"] = weladee_employee.employee.TaxID
    data["identification_id"] = weladee_employee.employee.NationalID

    if photoBase64:
        data["image_1920"] = photoBase64

    if weladee_employee.employee.Phones:
       data["work_phone"] = weladee_employee.employee.Phones[0]

    if weladee_employee.DepartmentID :
        dep_datas = req.department_obj.search( [("weladee_id","=", weladee_employee.DepartmentID )] )
        if dep_datas :
            for ddatas in dep_datas :
                data[ "department_id" ] = ddatas.id        
    else:
        data[ "department_id" ] = False

    if weladee_employee.Badge:
       data["barcode"] = weladee_employee.Badge

    #2018-05-29 KPO if active = false set barcode to false
    if not weladee_employee.employee.Active:
       data["barcode"] = False 
       
    #2018-06-01 KPO if application level >=2 > manager   
    #data["manager"] = weladee_employee.employee.application_level >= 2

    data["driving_license_number"] = weladee_employee.employee.DrivingLicenseNumber
    data["driving_license_place_issue"] = weladee_employee.employee.DrivingLicensePlaceIssue
    if weladee_employee.employee.DrivingLicenseDateIssue > 0:
        data["driving_license_date_issue"] = datetime.fromtimestamp( weladee_employee.employee.DrivingLicenseDateIssue )
    if weladee_employee.employee.DrivingLicenseExpirationDate > 0:
        data["driving_license_expiration_date"] = datetime.fromtimestamp( weladee_employee.employee.DrivingLicenseExpirationDate )    
    data["religion"] =  sync_employee_data_religion(weladee_employee)
    data["marital"] = sync_employee_data_marital(weladee_employee)
    data["military_status"] = sync_employee_data_military(weladee_employee)
    if weladee_employee.employee.ResignationDate > 0:
        data["resignation_date"] = datetime.fromtimestamp( weladee_employee.employee.ResignationDate )
    if weladee_employee.employee.ProbationDueDate > 0:
        data["probation_due_date"] = datetime.fromtimestamp( weladee_employee.employee.ProbationDueDate )
    data["resignation_reason"] = weladee_employee.employee.ResignationReason

    # look if there is odoo record with same weladee-id
    # if not found then create else update    
    odoo_employee = req.employee_obj.search([("weladee_id", "=", weladee_employee.employee.ID),'|',('active','=',False),('active','=',True)])
    if not odoo_employee.id:
       data['res-mode'] = 'create'
    else:
       data['res-mode'] = 'update'  
       data['res-id'] = odoo_employee.id
       if not weladee_employee.odoo.odoo_id:
          data['send2-weladee'] = True

    if data['res-mode'] == 'create':
       # check if there is same name, email
       # consider it same record 
       if data['work_email']:
          odoo_employee = req.employee_obj.search([('work_email','=',data['work_email']),'|',('active','=',False),('active','=',True)])
       else:
          odoo_employee = req.employee_obj.search([('last_name_english','=',data['last_name_english']),\
                                          ('first_name_english','=',data['first_name_english']),\
                                          '|',('active','=',False),('active','=',True)]) 
       if odoo_employee.id:
          #if there is weladee id, will update it 
          sync_logdebug(req.context_sync, 'odoo > %s' % odoo_employee)
          sync_logdebug(req.context_sync, 'weladee > %s' % weladee_employee)
          if odoo_employee.weladee_id:
             sync_logwarn(req.context_sync,'weladee id change for this employee %s, will replace old weladee id %s with new one %s' % (data['work_email'] or data['name'],odoo_employee.weladee_id, weladee_employee.employee.ID))      
          else:
             sync_logdebug(req.context_sync,'this employee %s is missing weladee link, will update with new one %s' % (data['work_email'] or data['name'],weladee_employee.employee.ID))      
          data['res-mode'] = 'update'
          data['res-id'] = odoo_employee.id

    return data   

def sync_employee(req):
    '''
    sync data from employee
    '''
    req.context_sync['stat-employee'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    req.context_sync['stat-w-employee'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    try:
        weladee_employee = False
        sync_loginfo(req.context_sync,'[employee] updating changes from weladee-> odoo')
        for weladee_employee in stub.GetEmployees(weladee_pb2.Empty(), metadata=req.config.authorization):
            sync_stat_to_sync(req.context_sync['stat-employee'], 1)
            if not weladee_employee :
               sync_logwarn(req.context_sync,'weladee employee is empty')
               sync_logdebug(req.context_sync, "weladee employee is empty '%s'" % weladee_employee )
               continue
            
            odoo_emp = sync_employee_data(weladee_employee, req)
            sync_logdebug(req.context_sync, "weladee employee mode '%s'" % odoo_emp )

            if odoo_emp and odoo_emp['res-mode'] == 'create':
               newid = req.employee_obj.create(odoo_emp)
               # link weladee-manager and odoo employee
               if newid.id:
                  req.employee_managers[ newid.id ] = weladee_employee.employee.ManagerID
               sync_logdebug(req.context_sync, "Insert employee '%s' to odoo" % odoo_emp['name'] )
               sync_stat_create(req.context_sync['stat-employee'], 1)

            elif odoo_emp and odoo_emp['res-mode'] == 'update':
                
                odoo_id = req.employee_obj.search([('id','=',odoo_emp['res-id']),'|',('active','=',False),('active','=',True)])
                if odoo_id.id:
                   odoo_id.write(odoo_emp)
                   sync_logdebug(req.context_sync, "Updated employee '%s' to odoo" % odoo_emp['name'] )
                   sync_stat_update(req.context_sync['stat-employee'], 1)
                   # link weladee-manager and odoo employee
                   req.employee_managers[ odoo_id.id ] = weladee_employee.employee.ManagerID
                else:
                   sync_logdebug(req.context_sync, 'weladee > %s' % weladee_employee) 
                   sync_logerror(req.context_sync, "Not found this odoo employee id %s of '%s' in odoo" % (odoo_emp['res-id'], odoo_emp['name']) ) 
                   sync_stat_error(req.context_sync['stat-employee'], 1)

    except Exception as e:
        print(traceback.format_exc())
        if sync_weladee_error(weladee_employee, 'employee', e, req.context_sync):
           return
    
    #stat
    sync_stat_info(req.context_sync,'stat-employee','[employee] updating changes from weladee-> odoo')

    #scan in odoo if there is record with no weladee_id
    sync_loginfo(req.context_sync, '[employee] updating new changes from odoo -> weladee')
    odoo_employee_ids = req.employee_obj.search([('weladee_id','=',False),'|',('active','=',False),('active','=',True)])
    req.context_sync['stat-w-employee']['to-sync'] = len(odoo_employee_ids)
    for odoo_employee in odoo_employee_ids:
        if odoo_employee.id == 1: 
           #always skip administrator id = 1
           continue 
        sync_stat_to_sync(req.context_sync['stat-w-employee'], 1)
        if not odoo_employee.name:
           sync_logdebug(req.context_sync, 'odoo > %s' % odoo_employee) 
           sync_logwarn(req.context_sync, 'do not send empty odoo employee name')
           continue
        if not odoo_employee.work_email:
           sync_logdebug(req.context_sync, 'odoo > %s' % odoo_employee) 
           sync_logwarn(req.context_sync, 'do not send empty odoo employee email')
           continue
        
        newEmployee = odoo_pb2.EmployeeOdoo()
        newEmployee.odoo.odoo_id = odoo_employee.id
        newEmployee.odoo.odoo_created_on = int(time.time())
        newEmployee.odoo.odoo_synced_on = int(time.time())

        newEmployee.employee.first_name_english = odoo_employee.first_name_english or odoo_employee.name
        newEmployee.employee.last_name_english = odoo_employee.last_name_english or bytes()
        newEmployee.employee.first_name_thai = odoo_employee.first_name_thai or ''
        newEmployee.employee.last_name_thai = odoo_employee.last_name_thai or ''
        newEmployee.employee.nickname_english = odoo_employee.nick_name_english or ''
        newEmployee.employee.nickname_thai = odoo_employee.nick_name_thai or ''

        newEmployee.employee.Code = odoo_employee.employee_code or bytes()

        if odoo_employee.country_id:
            newEmployee.employee.Nationality = odoo_employee.country_id.code 

        newEmployee.employee.email = odoo_employee.work_email

        if odoo_employee.parent_id and odoo_employee.parent_id.weladee_id:
            newEmployee.employee.ManagerID = int(odoo_employee.parent_id.weladee_id or '0')

        if odoo_employee.job_id and odoo_employee.job_id.weladee_id:
            newEmployee.employee.PositionID = int(odoo_employee.job_id.weladee_id or '0')

        if odoo_employee.birthday:
            newEmployee.employee.Birthday = datetime.strptime(odoo_employee.birthday,'%Y-%m-%d').timestamp()

        #language not sync yet
        newEmployee.employee.lg = "en"
        newEmployee.employee.Active = odoo_employee.active
        newEmployee.employee.receiveCheckNotification = odoo_employee.receive_check_notification
        newEmployee.employee.CanRequestHoliday = odoo_employee.can_request_holiday
        newEmployee.employee.HasToFillTimesheet = odoo_employee.hasToFillTimesheet

        newEmployee.employee.PassportNumber = odoo_employee.passport_id or ''
        newEmployee.employee.TaxID = odoo_employee.taxID or ''
        newEmployee.employee.NationalID = odoo_employee.identification_id or ''

        if odoo_employee.image_1920:
            newEmployee.employee.photo = odoo_employee.image_1920

        if odoo_employee.work_phone:
            newEmployee.employee.Phones[:] = [odoo_employee.work_phone]
        
        newEmployee.employee.Gender = new_employee_data_gender(odoo_employee.gender)
        newEmployee.employee.HourlyCost = odoo_employee.timesheet_cost

        newEmployee.employee.DrivingLicenseNumber = odoo_employee.driving_license_number or ''
        newEmployee.employee.DrivingLicensePlaceIssue = odoo_employee.driving_license_place_issue or ''
        if odoo_employee.driving_license_date_issue:
           newEmployee.employee.DrivingLicenseDateIssue = int(datetime.strptime(odoo_employee.driving_license_date_issue.strftime('%Y-%m-%d'),'%Y-%m-%d').timestamp())
        if odoo_employee.driving_license_expiration_date:
           newEmployee.employee.DrivingLicenseExpirationDate = int(datetime.strptime(odoo_employee.driving_license_expiration_date.strftime('%Y-%m-%d'),'%Y-%m-%d').timestamp())
        newEmployee.employee.Religion = new_employee_data_religion(odoo_employee.religion)
        newEmployee.employee.MaritalStatus = new_employee_data_marital(odoo_employee.marital)

        newEmployee.employee.MilitaryStatus = new_employee_data_military( odoo_employee.military_status)
        if odoo_employee.resignation_date:
           newEmployee.employee.ResignationDate = int(datetime.strptime(odoo_employee.resignation_date.strftime('%Y-%m-%d'),'%Y-%m-%d').timestamp())
        if odoo_employee.probation_due_date:
           newEmployee.employee.ProbationDueDate = int(datetime.strptime(odoo_employee.probation_due_date.strftime('%Y-%m-%d'),'%Y-%m-%d').timestamp())
        newEmployee.employee.ResignationReason = odoo_employee.resignation_reason or ''

        #2018-06-07 KPO don't sync note back
        #2018-06-15 KPO don't sync badge

        try:
            returnobj = stub.AddEmployee(newEmployee, metadata=req.config.authorization)

            odoo_employee.write({'send2-weladee':False, 'weladee_id':returnobj.id})
            sync_logdebug(req.context_sync, "Added employee to weladee : %s" % odoo_employee.name)
            sync_stat_create(req.context_sync['stat-w-employee'], 1)

        except Exception as e:
            print(traceback.format_exc())
            sync_logdebug(req.context_sync, 'odoo > %s' % odoo_employee)
            sync_logerror(req.context_sync, "Add employee '%s' failed : %s" % (odoo_employee.name, e))
            sync_stat_error(req.context_sync['stat-w-employee'], 1)
    #stat
    sync_stat_info(req.context_sync,'stat-w-employee','[employee] updating new changes from odoo -> weladee',newline=True)