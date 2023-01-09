# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import traceback
import datetime
from dateutil.relativedelta import relativedelta

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2, weladee_pb2
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error, sync_period
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info,sync_clean_up
from odoo.addons.Weladee_Attendances.models.sync.weladee_employee import get_emp_odoo_weladee_ids

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
            'account_id': req.config.timehsheet_account_analytic_id,
            'time_to_charge': weladee_timesheet.Sheet.TimeToCharge,
            'work_type_id': req.work_type_odoo_weladee_ids.get(str(weladee_timesheet.Sheet.WorkTypeID),False)
            }
    data['res-mode'] = 'create'

    # look if there is odoo record with same weladee-id
    # if not found then create else update
    prev_rec = req.timesheet_obj.search( [ ('weladee_id','=', weladee_timesheet.Sheet.ID )],limit=1 )
    if prev_rec and prev_rec.id:
        data['res-mode'] = 'update'
        data['res-id'] = prev_rec.id
        sync_logdebug(req.context_sync, 'weladee > %s ' % weladee_timesheet)
        sync_logdebug(req.context_sync, 'odoo > %s ' % data)

        # return data

    # check if there is same date, project and task
    # consider it same record
    # odoo_timesheet = req.timesheet_obj.search( [ ('date','=', data['date'] ), ('project_id','=', data['project_id'] ), ('task_id','=', data['task_id'] ) ],limit=1 )
    # if odoo_timesheet.id:
    #     data['res-mode'] = 'update'
    #     data['res-id'] = odoo_timesheet.id
    #     sync_logdebug(req.context_sync, 'odoo > %s' % odoo_timesheet)
    #     sync_logdebug(req.context_sync, 'weladee > %s' % weladee_timesheet)

    return data

def sync_timesheet(req):
    '''
    sync all timesheet from weladee (1 way from weladee)

    '''
    req.context_sync['stat-timesheet'] = {'to-sync':0, "create":0, "update": 0, "error":0}

    req.work_type_odoo_weladee_ids = {}
    for ec in req.work_type_obj.search([('weladee_id','!=',False)]):
        req.work_type_odoo_weladee_ids[ec.weladee_id] = ec.id

    #if empty, create one 
    if not req.employee_odoo_weladee_ids: 
        sync_logdebug(req.context_sync, 'getting all employee-weladee link') 
        req.employee_odoo_weladee_ids = get_emp_odoo_weladee_ids(req)

    odoo_timesheet = False
    weladee_timesheet = False

    try:        
        sync_loginfo(req.context_sync,'[timesheet] updating changes from weladee-> odoo')

        # Calculate period
        period = sync_period(req.config.timesheet_period, req.config.timesheet_period_unit)

        for weladee_timesheet in stub.GetTimeSheets(period, metadata=req.config.authorization):
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

            elif odoo_timesheet and odoo_timesheet['res-mode'] == 'update':
                odoo_id = req.timesheet_obj.search([('id','=',odoo_timesheet['res-id'])])
                if odoo_id.id:
                   odoo_id.write(sync_clean_up(odoo_timesheet))
                   sync_logdebug(req.context_sync, "Updated timesheet '%s' to odoo" % odoo_timesheet['name'] )
                   sync_stat_update(req.context_sync['stat-timesheet'], 1)
                else:
                   sync_logdebug(req.context_sync, 'weladee > %s' % weladee_timesheet)
                   sync_logerror(req.context_sync, "Not found this odoo timesheet id %s of '%s' in odoo" % (odoo_timesheet['res-id'], odoo_timesheet['name']) )
                   sync_stat_error(req.context_sync['stat-timesheet'], 1)

    except Exception as e:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        sync_logdebug(req.context_sync, 'odoo >> %s' % odoo_timesheet) 
        if sync_weladee_error(weladee_timesheet, 'timesheet', e, req.context_sync):
            return
    #stat
    sync_stat_info(req.context_sync,'stat-timesheet','[timesheet] updating changes from weladee-> odoo')