# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import traceback

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub, myrequest, sync_clean_up, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error, renew_connection
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info

def sync_work_type_data(weladee_work_type, req):
    '''
    work_type data to sync
    '''
    pos = {"name" : weladee_work_type.WorkType.NameEnglish,
           "name_thai" : weladee_work_type.WorkType.NameThai,
           "weladee_id" : weladee_work_type.WorkType.ID,
           'default_description': weladee_work_type.WorkType.Note,
           'send2-weladee':False}

    # look if there is odoo record with same weladee-id
    # if not found then create else update    
    odoo_work_type = req.work_type_obj.search([("weladee_id", "=", weladee_work_type.WorkType.ID)],limit=1) 
    if not odoo_work_type.id:
       pos['res-mode'] = 'create'
    else:
       pos['res-mode'] = 'update'  
       pos['res-id'] = odoo_work_type.id
       if not weladee_work_type.odoo.odoo_id:
          pos['send2-weladee'] = True

    if pos['res-mode'] == 'create':
       # check if there is same name
       # consider it same record 
       odoo_work_type = req.work_type_obj.search([('name','=',pos['name'] )],limit=1) 
       if odoo_work_type.id:
          #if there is weladee id, will update it 
          sync_logdebug(req.context_sync, 'odoo > %s' % odoo_work_type)
          sync_logdebug(req.context_sync, 'weladee > %s' % weladee_work_type)
          if odoo_work_type.weladee_id:
             sync_logwarn(req.context_sync,'will replace old weladee id %s with new one %s' % (odoo_work_type.weladee_id, weladee_work_type.WorkType.ID))      
          else:
             sync_logdebug(req.context_sync,'missing weladee link, will update with new one %s' % weladee_work_type.WorkType.ID)      
          pos['res-mode'] = 'update'
          pos['res-id'] = odoo_work_type.id

    return pos          

def sync_work_type(req):
    '''
    sync all work_types from weladee

    '''
    req.context_sync['stat-work_type'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    req.context_sync['stat-w-work_type'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    #get change data from weladee
    try:
        weladee_work_type = False
        sync_loginfo(req.context_sync,'[work_type] updating changes from weladee-> odoo')
        for weladee_work_type in stub.GetWorkTypes(myrequest, metadata=req.config.authorization,timeout=5):
            sync_stat_to_sync(req.context_sync['stat-work_type'], 1)
            if not weladee_work_type :
               sync_logwarn(req.context_sync,'weladee work_type is empty')
               continue

            odoo_pos = sync_work_type_data(weladee_work_type, req)

            if odoo_pos and odoo_pos['res-mode'] == 'create':
               req.work_type_obj.create(sync_clean_up(odoo_pos))
               sync_logdebug(req.context_sync, "Insert work_type '%s' to odoo" % odoo_pos['name'] )
               sync_stat_create(req.context_sync['stat-work_type'], 1)

            elif odoo_pos and odoo_pos['res-mode'] == 'update':
                odoo_id = req.work_type_obj.search([('id','=',odoo_pos['res-id'])])
                if odoo_id.id:
                   odoo_id.write(sync_clean_up(odoo_pos))
                   sync_logdebug(req.context_sync, "Updated work_type '%s' to odoo" % odoo_pos['name'] )
                   sync_stat_update(req.context_sync['stat-work_type'], 1)
                else:
                   sync_logdebug(req.context_sync, 'weladee > %s' % weladee_work_type) 
                   sync_logerror(req.context_sync, "Not found this odoo work_type id %s of '%s' in odoo" % (odoo_pos['res-id'], odoo_pos['name']) ) 
                   sync_stat_error(req.context_sync['stat-work_type'], 1)

    except Exception as e:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        if sync_weladee_error(weladee_work_type, 'work_type', e, req.context_sync):
           return
    #stat
    sync_stat_info(req.context_sync,'stat-work_type','[work_type] updating changes from weladee-> odoo')