# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import traceback
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info,sync_clean_up

base_url = 'https://www.weladee.com/project/'

def sync_project_data(weladee_project, req):
    '''
    project data to sync
    '''
    data = {'name': weladee_project.Project.NameEnglish,
            'name-th': weladee_project.Project.NameThai,
            'description': weladee_project.Project.DescriptionEnglish,
            'description-th': weladee_project.Project.DescriptionThai,
            'note': weladee_project.Project.Note,
            'url': weladee_project.Project.URL,
            'weladee_id':  weladee_project.Project.ID,
            'weladee_url': base_url + str(weladee_project.Project.ID),
            'active':weladee_project.Project.active,
            }    
    data['partner_id'] = req.customer_odoo_weladee_ids.get(weladee_project.Project.CustomerID, False)
    data['res-mode'] = 'create'

    # look if there is odoo record with same weladee-id
    # if not found then create else update
    prev_rec = req.project_obj.search( [ ('weladee_id','=', weladee_project.Project.ID ), '|', ('active','=',True), ('active','=',False)],limit=1 )
    if prev_rec and prev_rec.id:
        data['res-mode'] = 'update'  
        data['res-id'] = prev_rec.id
        sync_logdebug(req.context_sync, 'weladee > %s ' % weladee_project)
        sync_logdebug(req.context_sync, 'odoo > %s ' % data)
        #sync_logwarn(req.context_sync, 'this project\'name record already exist for this %s exist, no change will apply' % data['name'])
        # return data

    # check if there is same name
    # consider it same record
    # odoo_prj = req.project_obj.search( [ ('name','=', data['name'] ), '|', ('active','=',True), ('active','=',False)],limit=1 )
    # if odoo_prj.id:
    #     data['res-mode'] = 'update'
    #     data['res-id'] = odoo_prj.id
    #     sync_logdebug(req.context_sync, 'odoo > %s' % odoo_prj)
    #     sync_logdebug(req.context_sync, 'weladee > %s' % weladee_project)

    return data

def sync_delete_project(req):
    del_ids = req.project_obj.search([('weladee_id','!=',False)])
    if del_ids:         
       del_ids.unlink()
       sync_logwarn(req.context_sync, 'remove all linked project: %s record(s)' % len(del_ids))

def sync_delete_task(req):
    del_ids = req.task_obj.search([('weladee_id','!=',False)])
    if del_ids: 
       del_ids.unlink()
       sync_logwarn(req.context_sync, 'remove all linked task: %s record(s)' % len(del_ids))

def sync_delete_timesheet(req):
    del_ids = req.timesheet_obj.search([('weladee_id','!=',False)])
    if del_ids: 
       del_ids.unlink()
       sync_logwarn(req.context_sync, 'remove all linked timesheet: %s record(s)' % len(del_ids))

def sync_project(req):
    '''
    sync all project from weladee (1 way from weladee)

    '''
    req.context_sync['stat-proj'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    odoo_prj = False
    weladee_project = False

    try:        
        sync_loginfo(req.context_sync,'[project] updating changes from weladee-> odoo')
        for weladee_project in stub.GetProjects(weladee_pb2.Empty(), metadata=req.config.authorization):
            #print(weladee_project)
            sync_stat_to_sync(req.context_sync['stat-proj'], 1)
            if not weladee_project :
               sync_logwarn(req.context_sync,'weladee project is empty')
               continue

            odoo_prj = sync_project_data(weladee_project, req)
            
            if odoo_prj and odoo_prj['res-mode'] == 'create':
                newid = req.project_obj.create(sync_clean_up(odoo_prj))
                if newid and newid.id:
                    sync_logdebug(req.context_sync, "Insert project '%s' to odoo" % odoo_prj )
                    sync_stat_create(req.context_sync['stat-proj'], 1)

                    req.project_odoo_weladee_ids[weladee_project.Project.ID] = newid.id
                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_project) 
                    sync_logerror(req.context_sync, "error while create odoo project id %s of '%s' in odoo" % (odoo_prj['res-id'], odoo_prj) ) 
                    sync_stat_error(req.context_sync['stat-proj'], 1)

            elif odoo_prj and odoo_prj['res-mode'] == 'update':
                
                odoo_id = req.project_obj.search([('id','=',odoo_prj['res-id']),'|',('active','=',False),('active','=',True)])
                if odoo_id.id:
                #    odoo_id.write({'partner_id': odoo_prj.get('partner_id')})
                   odoo_id.write(sync_clean_up(odoo_prj))
                   sync_logdebug(req.context_sync, "Updated project '%s' to odoo" % odoo_prj['name'] )
                   sync_stat_update(req.context_sync['stat-proj'], 1)
                   
                   req.project_odoo_weladee_ids[weladee_project.Project.ID] = odoo_id.id
                else:
                   sync_logdebug(req.context_sync, 'weladee > %s' % weladee_project)
                   sync_logerror(req.context_sync, "Not found this odoo project id %s of '%s' in odoo" % (odoo_prj['res-id'], odoo_prj['name']) ) 
                   sync_stat_error(req.context_sync['stat-proj'], 1)

    except Exception as e:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        sync_logdebug(req.context_sync, 'odoo >> %s' % odoo_prj) 
        if sync_weladee_error(weladee_project, 'project', e, req.context_sync):
            return
    #stat
    sync_stat_info(req.context_sync,'stat-proj','[project] updating changes from weladee-> odoo')