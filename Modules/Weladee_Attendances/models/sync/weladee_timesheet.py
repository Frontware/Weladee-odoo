# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import traceback
import datetime

from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info,sync_clean_up

def sync_timesheet_data(weladee_timesheet, req):
    '''
    timesheet data to sync
    '''
    data = {'weladee_id':  weladee_timesheet.Sheet.ID,
            'project_id':  req.project_odoo_weladee_ids.get(weladee_timesheet.Sheet.ProjectID, False),
            'task_id':  req.task_odoo_weladee_ids.get(weladee_timesheet.Sheet.TaskID, False),
            'employee_id':  req.employee_odoo_weladee_ids.get(str(weladee_timesheet.Sheet.EmployeeID), False),
            'name': weladee_timesheet.Sheet.Description,
            'date': datetime.datetime.utcfromtimestamp(weladee_timesheet.Sheet.Day),
            'unit_amount': weladee_timesheet.Sheet.TimeSpent / 60,
            'weladee_cost': weladee_timesheet.Sheet.Cost,
            'work_type_id': req.work_type_odoo_weladee_ids.get(str(weladee_timesheet.Sheet.WorkTypeID),False)
            }        
    data['res-mode'] = 'create'
    print(data)
    return data   

def sync_timesheet(req):
    '''
    sync all timesheet from weladee (1 way from weladee)

    '''
    req.context_sync['stat-timesheet'] = {'to-sync':0, "create":0, "update": 0, "error":0}

    req.work_type_odoo_weladee_ids = {}
    for ec in req.work_type_obj.search([('weladee_id','!=',False)]):
        req.work_type_odoo_weladee_ids[ec.weladee_id] = ec.id

    odoo_timesheet = False
    weladee_timesheet = False

    try:        
        sync_loginfo(req.context_sync,'[timesheet] updating changes from weladee-> odoo')
        for weladee_timesheet in stub.GetTimeSheets(weladee_pb2.Empty(), metadata=req.config.authorization):
            print(weladee_timesheet)
            sync_stat_to_sync(req.context_sync['stat-timesheet'], 1)
            if not weladee_timesheet :
               sync_logwarn(req.context_sync,'weladee timesheet is empty')
               continue

            odoo_timesheet = sync_timesheet_data(weladee_timesheet, req)
            
            if odoo_timesheet and odoo_timesheet['res-mode'] == 'create':
                newid = req.timesheet_obj.create(sync_clean_up(odoo_timesheet))
                if newid and newid.id:
                    sync_logdebug(req.context_sync, "Insert timesheet '%s' to odoo" % odoo_timesheet )
                    sync_stat_create(req.context_sync['stat-timesheet'], 1)

                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_timesheet) 
                    sync_logerror(req.context_sync, "error while create odoo timesheet id %s of '%s' in odoo" % (odoo_timesheet['res-id'], odoo_timesheet) ) 
                    sync_stat_error(req.context_sync['stat-timesheet'], 1)

    except Exception as e:
        print(traceback.format_exc())
        sync_logdebug(req.context_sync, 'odoo >> %s' % odoo_timesheet) 
        if sync_weladee_error(weladee_timesheet, 'timesheet', e, req.context_sync):
            return
    #stat
    sync_stat_info(req.context_sync,'stat-timesheet','[timesheet] updating changes from weladee-> odoo')