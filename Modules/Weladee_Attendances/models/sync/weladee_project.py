# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import datetime
import pytz

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info,sync_clean_up
from .weladee_log import get_emp_odoo_weladee_ids
from odoo.addons.Weladee_Attendances.library.weladee_lib import _convert_to_tz_time

def sync_project_data(weladee_project, req):
    '''
    customer data to sync
    '''
    data = {'name': weladee_project.Project.NameEnglish,
            'name_thai': weladee_project.Project.NameThai,
            'description': weladee_project.Project.Note,
            'weladee_id':  weladee_project.Project.ID,
            'active':weladee_project.Project.active,
            }    
    data['partner_id'] = req.customer_odoo_weladee_ids.get(weladee_project.Project.CustomerID, False)
    data['res-mode'] = 'create'
    prev_rec = req.project_obj.search( [ ('name','=', data['name'] )],limit=1 )
    if prev_rec and prev_rec.id:
        data['res-mode'] = '' 
        sync_logdebug(req.context_sync, 'weladee > %s ' % weladee_project)
        sync_logdebug(req.context_sync, 'odoo > %s ' % data)
        sync_logwarn(req.context_sync, 'this project\'name record already exist for this %s exist, no change will apply' % data['name'])

    return data   

def sync_delete_project(req):
    del_ids = req.project_obj.search([('weladee_id','!=',False)])
    if del_ids: 
       del_ids.unlink()
       sync_logwarn(req.context_sync, 'remove all linked project: %s record(s)' % len(del_ids))

def sync_project(req):
    '''
    sync all customer from weladee (1 way from weladee)

    '''
    req.context_sync['stat-proj'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    odoo_prj = False
    weladee_project = False

    sync_delete_project(req)

    try:        
        sync_loginfo(req.context_sync,'[log] updating changes from weladee-> odoo')
        for weladee_project in stub.GetProjects(weladee_pb2.Empty(), metadata=req.config.authorization):
            print(weladee_project)
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

                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_project) 
                    sync_logerror(req.context_sync, "error while create odoo project id %s of '%s' in odoo" % (odoo_prj['res-id'], odoo_prj) ) 
                    sync_stat_error(req.context_sync['stat-proj'], 1)

    except Exception as e:
        sync_logdebug(req.context_sync, 'odoo >> %s' % odoo_prj) 
        if sync_weladee_error(weladee_project, 'project', e, req.context_sync):
            return
    #stat
    sync_stat_info(req.context_sync,'stat-proj','[log] updating changes from weladee-> odoo')