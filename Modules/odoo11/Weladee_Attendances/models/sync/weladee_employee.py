# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import requests
import base64

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info 

def sync_employee_data_gender(weladee_emp):
    '''
    convert weladee employee gender to odoo
    '''
    if weladee_emp.employee.gender == '':
        return 'male'
    elif weladee_emp.employee.gender == '':        
        return 'female'
    else:
        return 'other'

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

def sync_employee_data(weladee_employee, emp_obj, job_obj, department_obj, country, context_sync):
    '''
    employee data to sync

    remarks:

    2018-06-14 KPO sync qrcode from weladee
    '''    
    photoBase64 = ''
    if weladee_employee.employee.photo:
        try :
            photoBase64 = base64.b64encode(requests.get(weladee_employee.employee.photo).content)
        except Exception as e:
            sync_logdebug(context_sync, "image : %s" % weladee_employee.employee.photo)
            sync_logerror(context_sync, "Error when load image : %s" % e)
    
    #2018-06-07 KPO don't sync note back   
    #2018-06-21 KPO get team but don't sync back     
    data = { "name" : " ".join([weladee_employee.employee.first_name_english or '', weladee_employee.employee.last_name_english or "" ])
            ,"employee_code" :(weladee_employee.employee.code or "" )
            ,"weladee_profile" : "https://www.weladee.com/employee/%s" % weladee_employee.employee.ID
            ,"work_email":( weladee_employee.employee.email or "" )
            ,"first_name_english":weladee_employee.employee.first_name_english
            ,"last_name_english":weladee_employee.employee.last_name_english
            ,"first_name_thai":weladee_employee.employee.first_name_thai
            ,"last_name_thai":weladee_employee.employee.last_name_thai
            ,"nick_name_english":weladee_employee.employee.nickname_english
            ,"nick_name_thai":weladee_employee.employee.nickname_thai
            ,"active": weladee_employee.employee.Active
            ,"receive_check_notification": weladee_employee.employee.receiveCheckNotification
            ,"can_request_holiday": weladee_employee.employee.canRequestHoliday
            ,"hasToFillTimesheet": weladee_employee.employee.hasToFillTimesheet
            ,"weladee_id":weladee_employee.employee.ID
            ,"qr_code":weladee_employee.employee.QRCode
            ,"gender": sync_employee_data_gender(weladee_employee)
            ,"employee_team":weladee_employee.employee.TeamName
            ,'send2-weladee':False}

    if weladee_employee.employee.passportNumber :
        data["passport_id"] = weladee_employee.employee.passportNumber
    if weladee_employee.employee.taxID :
        data["taxID"] = weladee_employee.employee.taxID
    if weladee_employee.employee.nationalID :
        data["nationalID"] = weladee_employee.employee.nationalID
        
    if weladee_employee.employee.positionid :
        job_datas = job_obj.search( [("weladee_id","=", weladee_employee.employee.positionid )] )
        if job_datas :
            for jdatas in job_datas :
                data[ "job_id" ] = jdatas.id
    
    if weladee_employee.DepartmentID :
        dep_datas = department_obj.search( [("weladee_id","=", weladee_employee.DepartmentID ),'|',('active','=',False),('active','=',True)] )
        if dep_datas :
            for ddatas in dep_datas :
                data[ "department_id" ] = ddatas.id

    if photoBase64:
        data["image"] = photoBase64

    if weladee_employee.Badge:
        data["barcode"] = weladee_employee.Badge

    #2018-05-29 KPO if active = false set barcode to false
    if not weladee_employee.employee.Active:
       data["barcode"] = False 

    if weladee_employee.employee.Nationality:
        if weladee_employee.employee.Nationality.lower() in country :
            data["country_id"] = country[ weladee_employee.employee.Nationality.lower() ]
     
    if weladee_employee.employee.Phones:
       data["work_phone"] = weladee_employee.employee.Phones[0]
       
    #2018-06-01 KPO if application level >=2 > manager   
    data["manager"] = weladee_employee.employee.application_level >= 2

    # look if there is odoo record with same weladee-id
    # if not found then create else update    
    odoo_employee = emp_obj.search([("weladee_id", "=", weladee_employee.employee.ID)])
    if not odoo_employee.id:
       data['res-mode'] = 'create'
    else:
       data['res-mode'] = 'update'  
       data['res-id'] = odoo_employee.id
       if not weladee_employee.odoo.odoo_id:
          data['send2-weladee'] = True

    if data['res-mode'] == 'create':
       # check if there is same name
       # consider it same record 
       odoo_employee = emp_obj.search([('work_email','=',data['work_email']),'|',('active','=',False),('active','=',True)])
       if odoo_employee.id:
          #if there is weladee id, will update it 
          sync_logdebug(context_sync, 'odoo > %s' % odoo_employee)
          sync_logdebug(context_sync, 'weladee > %s' % weladee_employee)
          if odoo_employee.weladee_id:
             sync_logwarn(context_sync,'will replace old weladee id %s with new one %s' % (odoo_employee.weladee_id, weladee_employee.employee.ID))      
          else:
             sync_logdebug(context_sync,'missing weladee link, will update with new one %s' % weladee_employee.employee.ID)      
          data['res-mode'] = 'update'
          data['res-id'] = odoo_employee.id

    return data   

def sync_employee(job_obj, employee_obj, department_obj, country, authorization, return_managers, context_sync):
    '''
    sync data from employee
    '''
    context_sync['stat-employee'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    context_sync['stat-w-employee'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    try:
        weladee_employee = False
        sync_loginfo(context_sync,'[employee] updating changes from weladee-> odoo')
        for weladee_employee in stub.GetEmployees(weladee_pb2.Empty(), metadata=authorization):
            sync_stat_to_sync(context_sync['stat-employee'], 1)
            if not weladee_employee :
               sync_logwarn(context_sync,'weladee employee is empty')
               continue

            odoo_emp = sync_employee_data(weladee_employee, employee_obj, job_obj, department_obj, country, context_sync)

            if odoo_emp and odoo_emp['res-mode'] == 'create':
               employee_obj.create(odoo_emp)
               sync_logdebug(context_sync, "Insert employee '%s' to odoo" % odoo_emp['name'] )
               sync_stat_create(context_sync['stat-employee'], 1)

            elif odoo_emp and odoo_emp['res-mode'] == 'update':
                odoo_id = employee_obj.search([('id','=',odoo_emp['res-id'])])
                if odoo_id.id:
                   odoo_id.write(odoo_emp)
                   sync_logdebug(context_sync, "Updated employee '%s' to odoo" % odoo_emp['name'] )
                   sync_stat_update(context_sync['stat-employee'], 1)
                else:
                   sync_logdebug(context_sync, 'weladee > %s' % weladee_employee) 
                   sync_logerror(context_sync, "Not found this odoo employee id %s of '%s' in odoo" % (odoo_emp['res-id'], odoo_emp['name']) ) 
                   sync_stat_error(context_sync['stat-employee'], 1)

    except Exception as e:
        if sync_weladee_error(weladee_employee, 'employee', e, context_sync):
           return
    
    #stat
    sync_stat_info(context_sync,'stat-employee','[employee] updating changes from weladee-> odoo')

    #scan in odoo if there is record with no weladee_id
    sync_loginfo(context_sync, '[employee] updating new changes from odoo -> weladee')
    odoo_employee_ids = employee_obj.search([('weladee_id','=',False),'|',('active','=',False),('active','=',True)])
    for odoo_employee in odoo_employee_ids:
        sync_stat_to_sync(context_sync['stat-w-employee'], 1)
        if not odoo_employee.name :
           sync_logdebug(context_sync, 'odoo > %s' % odoo_employee) 
           sync_logwarn(context_sync, 'do not send empty odoo employee name')
           continue
        
        newEmployee = odoo_pb2.EmployeeOdoo()
        newEmployee.odoo.odoo_id = odoo_employee.id
        newEmployee.odoo.odoo_created_on = int(time.time())
        newEmployee.odoo.odoo_synced_on = int(time.time())

        newEmployee.employee.first_name_english = odoo_employee.first_name_english or ''
        newEmployee.employee.last_name_english = odoo_employee.last_name_english or ''
        newEmployee.employee.first_name_thai = odoo_employee.first_name_thai or ''
        newEmployee.employee.last_name_thai = odoo_employee.last_name_thai or ''
        newEmployee.employee.gender = new_employee_data_gender(odoo_employee.gender)
        newEmployee.employee.email = odoo_employee.work_email or ''
        newEmployee.employee.code = odoo_employee.employee_code or ''
        newEmployee.employee.nickname_english = odoo_employee.nick_name_english or ''
        newEmployee.employee.nickname_thai = odoo_employee.nick_name_thai or ''
        #2018-06-07 KPO don't sync note back
        newEmployee.employee.lg = "en"
        newEmployee.employee.Active = odoo_employee.active
        newEmployee.employee.receiveCheckNotification = odoo_employee.receive_check_notification
        newEmployee.employee.canRequestHoliday = odoo_employee.can_request_holiday
        newEmployee.employee.hasToFillTimesheet = odoo_employee.hasToFillTimesheet

        newEmployee.employee.passportNumber = odoo_employee.passport_id or ''
        newEmployee.employee.taxID = odoo_employee.taxID or ''
        newEmployee.employee.nationalID = odoo_employee.nationalID or ''
        #2018-06-15 KPO don't sync badge

        if odoo_employee.country_id:
            newEmployee.employee.Nationality = odoo_employee.country_id.name 

        if odoo_employee.image:
            newEmployee.employee.photo = odoo_employee.image

        if odoo_employee.work_phone:
            newEmployee.employee.Phones[:] = [odoo_employee.work_phone]

        if odoo_employee.job_id and odoo_employee.job_id.weladee_id:
            newEmployee.employee.positionid = int(odoo_employee.job_id.weladee_id or '0')

        if odoo_employee.parent_id and odoo_employee.parent_id.weladee_id:
            newEmployee.employee.managerID = int(odoo_employee.parent_id.weladee_id or '0')
          
        try:
            returnobj = stub.AddEmployee(newEmployee, metadata=authorization)
            #print( result  )
            odoo_employee.write({'weladee_id':returnobj.id})
            sync_logdebug(context_sync, "Added employee to weladee : %s" % odoo_employee.name)
            sync_stat_create(context_sync['stat-w-employee'], 1)
        except Exception as e:
            sync_logdebug(context_sync, 'odoo > %s' % odoo_employee)
            sync_logerror(context_sync, "Add employee '%s' failed : %s" % (odoo_employee.name, e))
            sync_stat_error(context_sync['stat-w-employee'], 1)
    #stat
    sync_stat_info(context_sync,'stat-w-employee','[employee] updating new changes from odoo -> weladee',newline=True)