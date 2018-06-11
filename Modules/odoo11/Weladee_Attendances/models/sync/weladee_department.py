# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, sync_loginfo, sync_logerror, myrequest  

def sync_department_data(weladee_dept):
    '''
    department data to sync
    '''    
    return {"name" : weladee_dept.department.name_english,
            "weladee_id" : weladee_dept.department.ID
    }   

def sync_department(department_obj, authorization, context_sync):
    '''
    sync department with odoo and return the list
    '''    
    sDepartment = []
    try:
        context_sync['request-logs'].append(['i','updating changes from weladee-> odoo'])
        #get change data from weladee
        for weladee_dept in stub.GetDepartments(myrequest, metadata=authorization):
            if not weladee_dept :
               context_sync['request-logs'].append(['d','>weladee department empty'])
            else:
                if not weladee_dept.department.ID :
                   context_sync['request-logs'].append(['d','>weladee department id empty'])
                else:
                    #search in odoo
                    odoo_department_ids = department_obj.search([("weladee_id", "=", weladee_dept.department.ID),'|',('active','=',False),('active','=',True)])
                    if not odoo_department_ids :
                        context_sync['request-logs'].append(['d','>not found weladee department id in odoo']) 
                        if weladee_dept.department.name_english :
                            odoo_department = department_obj.search([('name','=',weladee_dept.department.name_english ),'|',('active','=',False),('active','=',True)])
                            if not odoo_department :
                                __ = department_obj.create(sync_department_data(weladee_dept))
                                sync_loginfo(context_sync, "Insert department '%s' to odoo" % weladee_dept.department.name_english )
                            else:
                                odoo_department.write({"weladee_id" : weladee_dept.department.ID})
                                sync_loginfo(context_sync, "update weladee id to department '%s'" % weladee_dept.department.name_english )
                        else:
                            sync_logerror(context_sync,  "Error while create department '%s' to odoo: there is no english name")
                    else :
                        for odoo_department in odoo_department_ids :
                            odoo_department.write( sync_department_data(weladee_dept) )
                            sync_loginfo(context_sync,  "Updated department '%s' to odoo" % weladee_dept.department.name_english )

    except Exception as e:
        context_sync['request-error'] = True
        context_sync['request-logs'].append(['d','(department) Error while connect to grpc %s' % e])
        sync_logerror(context_sync, 'Error while connect to GRPC Server, please check your connection or your Weladee API Key')
        return

    #scan in odoo if there is record with no weladee_id
    context_sync['request-logs'].append(['i','updating new changes from odoo -> weladee'])
    odoo_department_ids = department_obj.search([('weladee_id','=',False),'|',('active','=',False),('active','=',True)])
    for odoo_department in odoo_department_ids:
        if not odoo_department.name :
           context_sync['request-logs'].append(['d','>not found odoo department name'])
        else:    
            if odoo_department["weladee_id"] :
               context_sync['request-logs'].append(['d','>strange case, found odoo weladee-id %s' % odoo_department["weladee_id"]]) 
            else:    
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
                    sync_loginfo(context_sync, "Added department to weladee : %s" % odoo_department.name)
                except Exception as e:
                    sync_logerror(context_sync, "Add department '%s' failed : %s" % (odoo_department.name, e))

    return  sDepartment