# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import traceback
from .weladee_base import sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info

def sync_manager_dep(req):
    '''
    sync department's manager
    '''
    req.context_sync['stat-d-manager'] = {'to-sync':0, "create":0, "update": 0, "error":0}

    sync_loginfo(req.context_sync,'[department-manager] updating manager''s changes from weladee-> odoo')
    #look only changed employees
    odoo_change = [x for x in req.department_managers]

    odoo_deps = req.department_obj.search([('id','in',odoo_change),'|',('active','=',False),('active','=',True)])
    for odoo_dep in odoo_deps :
        sync_stat_to_sync(req.context_sync['stat-d-manager'], 1)
        if odoo_dep.id and odoo_dep.id in req.department_managers :

            odoo_manager = req.employee_obj.search( [("weladee_id","=", req.department_managers[odoo_dep.id] ),\
                                                '|',("active","=",False),("active","=",True)] )

            try:
                __ = odoo_dep.write( {"send2-weladee": False,"manager_id": int(odoo_manager.id) } )
                sync_logdebug(req.context_sync,"Updated manager of %s" % odoo_dep.name)
                sync_stat_update(req.context_sync['stat-d-manager'], 1)
            except Exception as e:
                print(traceback.format_exc())
                sync_logdebug(req.context_sync, 'odoo > %s' % odoo_dep)
                sync_logerror(req.context_sync, "Update manager of %s failed : %s" % (odoo_dep.name, e))   
                sync_stat_error(req.context_sync['stat-d-manager'], 1)
    #stat
    sync_stat_info(req.context_sync,'stat-d-manager','[department-manager] updating manager''s changes from weladee-> odoo')

def sync_manager_emp(req):
    '''
    sync employee's manager
    '''
    req.context_sync['stat-e-manager'] = {'to-sync':0, "create":0, "update": 0, "error":0}

    sync_loginfo(req.context_sync,'[employee-manager] updating manager''s changes from weladee-> odoo')
    #look only changed employees
    odoo_emps_change = [x for x in req.employee_managers]
    
    odoo_emps = req.employee_obj.search([('id','in',odoo_emps_change),'|',('active','=',False),('active','=',True)])
    for odoo_emp in odoo_emps :
        sync_stat_to_sync(req.context_sync['stat-e-manager'], 1)
        if odoo_emp.id and odoo_emp.id in req.employee_managers :

            odoo_manager = req.employee_obj.search( [("weladee_id","=", req.employee_managers[odoo_emp.id] ),\
                                                '|',("active","=",False),("active","=",True)] )

            try:
                __ = odoo_emp.write( {"send2-weladee": False, "parent_id": int(odoo_manager.id) } )
                sync_logdebug(req.context_sync,"Updated manager of %s" % odoo_emp.name)
                sync_stat_update(req.context_sync['stat-e-manager'], 1)
            except Exception as e:
                print(traceback.format_exc())
                sync_logdebug(req.context_sync, 'odoo > %s' % odoo_emp)
                sync_logerror(req.context_sync, "Update manager of %s failed : %s" % (odoo_emp.name, e))   
                sync_stat_error(req.context_sync['stat-e-manager'], 1)
    #stat
    sync_stat_info(req.context_sync,'stat-e-manager','[employee-manager] updating manager''s changes from weladee-> odoo')