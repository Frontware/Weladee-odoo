# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from .weladee_base import sync_loginfo, sync_logerror 

def sync_manager(employee_obj, weladee_managers, authorization, context_sync):
    '''
    sync employee's manager
    '''
    context_sync['request-synced'].append('updating manager''s changes from weladee-> odoo')
    #look only changed employees
    odoo_emps_change = [x for x in weladee_managers]

    odoo_emps = employee_obj.search(['|',('id','in',odoo_emps_change),('active','=',False),('active','=',True)])
    for odoo_emp in odoo_emps :
        if odoo_emp.id and odoo_emp.id in weladee_managers :

            odoo_manager = employee_obj.search( [("weladee_id","=", weladee_managers[odoo_emp.id] ),'|',("active","=",False),("active","=",True)] )

            try:
                __ = odoo_emp.write( {"parent_id": int(odoo_manager.id) } )
                sync_loginfo(context_sync, "Updated manager of %s" % odoo_emp.name)
            except Exception as e:
                sync_logerror(context_sync, "Update manager of %s failed : %s" % (odoo_emp.name, e))   