# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import traceback
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info,sync_clean_up

def sync_task_data(weladee_task, req):
    '''
    task data to sync
    '''
    data = {'name': weladee_task.Task.NameEnglish,
            'name_thai': weladee_task.Task.NameThai,
            'description': weladee_task.Task.Note,
            'weladee_id':  weladee_task.Task.ID,
            'active':weladee_task.Task.active,
            }        
    data['partner_id'] = req.customer_odoo_weladee_ids.get(weladee_task.Task.CustomerID, False)
    data['project_id'] = req.project_odoo_weladee_ids.get(weladee_task.Task.ProjectID, False)
    if not data['partner_id']:
       data['partner_id'] = req.project_obj.browse(data['project_id']).partner_id.id 

    data['res-mode'] = 'create'
    prev_rec = req.task_obj.search( [ ('name','=', data['name'] )],limit=1 )
    if prev_rec and prev_rec.id:
        data['res-mode'] = '' 
        sync_logdebug(req.context_sync, 'weladee > %s ' % weladee_task)
        sync_logdebug(req.context_sync, 'odoo > %s ' % data)
        sync_logwarn(req.context_sync, 'this task\'name record already exist for this %s exist, no change will apply' % data['name'])

    return data   

def sync_task(req):
    '''
    sync all task from weladee (1 way from weladee)

    '''
    req.context_sync['stat-task'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    odoo_task = False
    weladee_task = False

    try:        
        sync_loginfo(req.context_sync,'[task] updating changes from weladee-> odoo')
        for weladee_task in stub.GetTasks(weladee_pb2.Empty(), metadata=req.config.authorization):
            print(weladee_task)
            sync_stat_to_sync(req.context_sync['stat-task'], 1)
            if not weladee_task :
               sync_logwarn(req.context_sync,'weladee task is empty')
               continue

            odoo_task = sync_task_data(weladee_task, req)
            
            if odoo_task and odoo_task['res-mode'] == 'create':
                newid = req.task_obj.create(sync_clean_up(odoo_task))
                if newid and newid.id:
                    sync_logdebug(req.context_sync, "Insert task '%s' to odoo" % odoo_task )
                    sync_stat_create(req.context_sync['stat-task'], 1)

                    req.task_odoo_weladee_ids[weladee_task.Task.ID] = newid.id
                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_task) 
                    sync_logerror(req.context_sync, "error while create odoo task id %s of '%s' in odoo" % (odoo_task['res-id'], odoo_task) ) 
                    sync_stat_error(req.context_sync['stat-task'], 1)

    except Exception as e:
        print(traceback.format_exc())
        sync_logdebug(req.context_sync, 'odoo >> %s' % odoo_task) 
        if sync_weladee_error(weladee_task, 'task', e, req.context_sync):
            return
    #stat
    sync_stat_info(req.context_sync,'stat-task','[task] updating changes from weladee-> odoo')