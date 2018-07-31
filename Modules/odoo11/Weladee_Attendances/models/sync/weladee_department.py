# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error 
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info

def sync_department_data(weladee_department, dept_obj, context_sync):
    '''
    department data to sync
    '''
    dept = {"name" : weladee_department.department.name_english,
            "weladee_id" : weladee_department.department.ID,
            'send2-weladee':False}

    # look if there is odoo record with same weladee-id
    # if not found then create else update    
    odoo_department = dept_obj.search([("weladee_id", "=", weladee_department.department.ID),'|',('active','=',False),('active','=',True)],limit=1) 
    if not odoo_department.id:
       dept['res-mode'] = 'create'
    else:
       dept['res-mode'] = 'update'  
       dept['res-id'] = odoo_department.id
       if not weladee_department.odoo.odoo_id:
          dept['send2-weladee'] = True
    
    if dept['res-mode'] == 'create':
       # check if there is same name
       # consider it same record 
       odoo_department = dept_obj.search([('name','=',weladee_department.department.name_english ),'|',('active','=',False),('active','=',True)],limit=1) 
       if odoo_department.id:
          #if there is weladee id, will update it 
          sync_logdebug(context_sync, 'odoo > %s' % odoo_department)
          sync_logdebug(context_sync, 'weladee > %s' % weladee_department)
          if odoo_department.weladee_id:
             sync_logwarn(context_sync,'will replace old weladee id %s with new one %s' % (odoo_department.weladee_id, weladee_department.department.ID))      
          else:
             sync_logdebug(context_sync,'missing weladee link, will update with new one %s' % weladee_department.department.ID)      
          dept['res-mode'] = 'update'
          dept['res-id'] = odoo_department.id
    
    return dept

def sync_department(department_obj, authorization, dep_managers, context_sync):
    '''
    sync department with odoo and return the list
    '''
    context_sync['stat-department'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    context_sync['stat-w-department'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    odoo_dept = False
    try:
        weladee_department = False
        sync_loginfo(context_sync,'[department] updating changes from weladee-> odoo')
        for weladee_department in stub.GetDepartments(myrequest, metadata=authorization):
            sync_stat_to_sync(context_sync['stat-department'], 1)
            if not weladee_department :
               sync_logwarn(context_sync,'weladee department is empty')
               continue
           
            odoo_dept = sync_department_data(weladee_department, department_obj, context_sync)
            
            if odoo_dept and odoo_dept['res-mode'] == 'create':
               newid = department_obj.create(odoo_dept)
               sync_logdebug(context_sync, "Insert department '%s' to odoo" % odoo_dept['name'] )
               sync_stat_create(context_sync['stat-department'], 1)
               #check manager
               if newid.id:
                  dep_managers[ newid.id ] = weladee_department.department.managerID

            elif odoo_dept and odoo_dept['res-mode'] == 'update':
                odoo_id = department_obj.search([('id','=',odoo_dept['res-id']),'|',('active','=',False),('active','=',True)])
                if odoo_id.id:
                   odoo_id.write(odoo_dept)
                   sync_logdebug(context_sync, "Updated department '%s' to odoo" % odoo_dept['name'] )
                   sync_stat_update(context_sync['stat-department'], 1)
                   #check manager
                   if not odoo_id.manager_id.id: dep_managers[ odoo_id.id ] = weladee_department.department.managerID
                   if odoo_id.manager_id.id and odoo_id.manager_id.weladee_id != weladee_department.department.managerID: 
                       dep_managers[ odoo_id.id ] = weladee_department.department.managerID   
                   #print(odoo_id.manager_id)
                   #print(weladee_department)
                else:
                   sync_logdebug(context_sync, 'weladee > %s' % weladee_department) 
                   sync_logerror(context_sync, "Not found this odoo department id %s of '%s' in odoo" % (odoo_dept['res-id'], odoo_dept['name']) ) 
                   sync_stat_error(context_sync['stat-department'], 1)

    except Exception as e:
        sync_logdebug(context_sync, 'odoo >> %s' % odoo_dept) 
        if sync_weladee_error(weladee_department, 'department', e, context_sync):
           return
    
    #stat
    sync_stat_info(context_sync,'stat-department','[department] updating changes from weladee-> odoo')

    #scan in odoo if there is record with no weladee_id
    sync_loginfo(context_sync, '[department] updating new changes from odoo -> weladee')
    odoo_department_ids = department_obj.search([('weladee_id','=',False),'|',('active','=',False),('active','=',True)])
    for odoo_department in odoo_department_ids:
        sync_stat_to_sync(context_sync['stat-w-department'], 1)
        if not odoo_department.name :
           sync_logdebug(context_sync, 'odoo > %s' % odoo_department) 
           sync_logwarn(context_sync, 'do not send empty odoo department name')
           continue
        
        newDepartment = odoo_pb2.DepartmentOdoo()
        newDepartment.odoo.odoo_id = odoo_department.id
        newDepartment.odoo.odoo_created_on = int(time.time())
        newDepartment.odoo.odoo_synced_on = int(time.time())

        newDepartment.department.name_english = odoo_department.name
        newDepartment.department.name_thai = odoo_department.name
        newDepartment.department.active = True
        if odoo_department.manager_id:
            newDepartment.department.managerID = int(odoo_department.manager_id.weladee_id)
          
        try:
            returnobj = stub.AddDepartment(newDepartment, metadata=authorization)
            #print( result  )
            odoo_department.write({'weladee_id':returnobj.id})
            sync_logdebug(context_sync, "Added department to weladee : %s" % odoo_department.name)
            sync_stat_create(context_sync['stat-w-department'], 1)
        except Exception as e:
            sync_logdebug(context_sync, 'odoo > %s' % odoo_department)
            sync_logerror(context_sync, "Add department '%s' failed : %s" % (odoo_department.name, e))
            sync_stat_error(context_sync['stat-w-department'], 1)
    #stat
    sync_stat_info(context_sync,'stat-w-department','[department] updating new changes from odoo -> weladee',newline=True)