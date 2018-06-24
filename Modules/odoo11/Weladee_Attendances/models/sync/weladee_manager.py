# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from .weladee_base import sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info

def sync_manager_dep(dep_obj, weladee_managers, authorization, context_sync):
    '''
    sync department's manager
    '''
    context_sync['stat-d-manager'] = {'to-sync':0, "create":0, "update": 0, "error":0}

    sync_loginfo(context_sync,'[department-manager] updating manager''s changes from weladee-> odoo')
    #look only changed employees
    odoo_change = [x for x in weladee_managers]

    odoo_deps = dep_obj.search([('id','in',odoo_change),'|',('active','=',False),('active','=',True)])
    for odoo_dep in odoo_deps :
        sync_stat_to_sync(context_sync['stat-d-manager'], 1)
        if odoo_dep.id and odoo_dep.id in weladee_managers :

            odoo_manager = dep_obj.search( [("weladee_id","=", weladee_managers[odoo_dep.id] ),\
                                                '|',("active","=",False),("active","=",True)] )

            try:
                __ = odoo_dep.write( {"manager_id": int(odoo_manager.id) } )
                sync_logdebug(context_sync,"Updated manager of %s" % odoo_dep.name)
                sync_stat_update(context_sync['stat-d-manager'], 1)
            except Exception as e:
                sync_logdebug(context_sync, 'odoo > %s' % odoo_dep)
                sync_logerror(context_sync, "Update manager of %s failed : %s" % (odoo_dep.name, e))   
                sync_stat_error(context_sync['stat-d-manager'], 1)
    #stat
    sync_stat_info(context_sync,'stat-d-manager','[department-manager] updating manager''s changes from weladee-> odoo')

def sync_manager_emp(employee_obj, weladee_managers, authorization, context_sync):
    '''
    sync employee's manager
    '''
    context_sync['stat-e-manager'] = {'to-sync':0, "create":0, "update": 0, "error":0}

    sync_loginfo(context_sync,'[employee-manager] updating manager''s changes from weladee-> odoo')
    #look only changed employees
    odoo_emps_change = [x for x in weladee_managers]

    odoo_emps = employee_obj.search([('id','in',odoo_emps_change),'|',('active','=',False),('active','=',True)])
    for odoo_emp in odoo_emps :
        sync_stat_to_sync(context_sync['stat-e-manager'], 1)
        if odoo_emp.id and odoo_emp.id in weladee_managers :

            odoo_manager = employee_obj.search( [("weladee_id","=", weladee_managers[odoo_emp.id] ),\
                                                '|',("active","=",False),("active","=",True)] )

            try:
                __ = odoo_emp.write( {"parent_id": int(odoo_manager.id) } )
                sync_logdebug(context_sync,"Updated manager of %s" % odoo_emp.name)
                sync_stat_update(context_sync['stat-e-manager'], 1)
            except Exception as e:
                sync_logdebug(context_sync, 'odoo > %s' % odoo_emp)
                sync_logerror(context_sync, "Update manager of %s failed : %s" % (odoo_emp.name, e))   
                sync_stat_error(context_sync['stat-e-manager'], 1)
    #stat
    sync_stat_info(context_sync,'stat-e-manager','[employee-manager] updating manager''s changes from weladee-> odoo')