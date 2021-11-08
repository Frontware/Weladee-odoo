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

def sync_project_data(self, weladee_project, prj_obj, odoo_weladee_ids, context_sync):
    '''
    customer data to sync
    '''
    data = {'name': weladee_project.Project.NameEnglish,
            'name_thai': weladee_project.Project.NameThai,
            'description': weladee_project.Project.Note,
            'weladee_id':  weladee_project.Project.ID,
            'active':weladee_project.Project.active,
            }    
    data['partner_id'] = odoo_weladee_ids.get('id', False)
    data['res-mode'] = 'create'
    prev_rec = prj_obj.search( [ ('name','=', data['name'] )],limit=1 )
    if prev_rec and prev_rec.id:
        data['res-mode'] = '' 
        sync_logdebug(context_sync, 'weladee > %s ' % weladee_project)
        sync_logdebug(context_sync, 'odoo > %s ' % data)
        sync_logwarn(context_sync, 'this project\'name record already exist for this %s exist, no change will apply' % data['name'])

    return data   

def sync_delete_project(self, context_sync):
    del_ids = self.env['project.project'].search([('weladee_id','!=',False)])
    if del_ids: 
       del_ids.unlink()
       sync_logwarn(context_sync, 'remove all linked project: %s record(s)' % len(del_ids))

def sync_project(self, prj_obj, authorization, context_sync, odoo_weladee_ids, to_email):
    '''
    sync all customer from weladee (1 way from weladee)

    '''
    context_sync['stat-proj'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    odoo_prj = False
    weladee_project = False

    sync_delete_project(self, context_sync)

    try:        
        sync_loginfo(context_sync,'[log] updating changes from weladee-> odoo')
        for weladee_project in stub.GetProjects(weladee_pb2.Empty(), metadata=authorization):
            print(weladee_project)
            sync_stat_to_sync(context_sync['stat-proj'], 1)
            if not weladee_project :
               sync_logwarn(context_sync,'weladee project is empty')
               continue

            odoo_prj = sync_project_data(self, weladee_project, prj_obj, odoo_weladee_ids, context_sync)
            
            if odoo_prj and odoo_prj['res-mode'] == 'create':
                newid = prj_obj.create(sync_clean_up(odoo_prj))
                if newid and newid.id:
                    sync_logdebug(context_sync, "Insert project '%s' to odoo" % odoo_prj )
                    sync_stat_create(context_sync['stat-proj'], 1)

                else:
                    sync_logdebug(context_sync, 'weladee > %s' % weladee_project) 
                    sync_logerror(context_sync, "error while create odoo project id %s of '%s' in odoo" % (odoo_prj['res-id'], odoo_prj) ) 
                    sync_stat_error(context_sync['stat-proj'], 1)

    except Exception as e:
        sync_logdebug(context_sync, 'odoo >> %s' % odoo_prj) 
        if sync_weladee_error(weladee_project, 'project', e, context_sync):
            return
    #stat
    sync_stat_info(context_sync,'stat-proj','[log] updating changes from weladee-> odoo')