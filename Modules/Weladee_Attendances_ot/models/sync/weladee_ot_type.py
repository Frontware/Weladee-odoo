# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import traceback

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub, myrequest, sync_clean_up, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error, renew_connection, sync_image
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info

def sync_ot_type_data(weladee_ot_type, req):
    '''
    ot_type data to sync
    '''
    ot_type = {"name" : weladee_ot_type.OTType.NameEnglish,
           "name-th" : weladee_ot_type.OTType.NameThai,
           "weladee_id" : weladee_ot_type.OTType.ID,
           'ot_hourly_rate': weladee_ot_type.OTType.HourlyRatePct,
           'code': weladee_ot_type.OTType.Code,
           'active': weladee_ot_type.OTType.active,
           'note': weladee_ot_type.OTType.Note,
           'weladee_url': 'https://www.weladee.com/ot/type/%s' % weladee_ot_type.OTType.ID
            }

    # look if there is odoo record with same weladee-id
    # if not found then create else update    
    odoo_ot_type = req.ot_type_obj.search([("weladee_id", "=", weladee_ot_type.OTType.ID)],limit=1) 
    if not odoo_ot_type.id:
       ot_type['res-mode'] = 'create'
    else:
       ot_type['res-mode'] = 'update'  
       ot_type['res-id'] = odoo_ot_type.id

    return ot_type          

def sync_ot_type(req):
    '''
    sync all ot_types from weladee

    '''
    req.context_sync['stat-ot_type'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    req.context_sync['stat-w-ot_type'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    #get change data from weladee
    try:
        weladee_ot_type = False
        sync_loginfo(req.context_sync,'[ot_type] updating changes from weladee-> odoo')
        for weladee_ot_type in stub.GetOTTypes(weladee_pb2.Empty(), metadata=req.config.authorization,timeout=5):
            
            sync_stat_to_sync(req.context_sync['stat-ot_type'], 1)
            if not weladee_ot_type :
               sync_logwarn(req.context_sync,'weladee ot_type is empty')
               continue
            
            odoo_pos = sync_ot_type_data(weladee_ot_type, req)

            if odoo_pos and odoo_pos['res-mode'] == 'create':
               newid = req.ot_type_obj.create(sync_clean_up(odoo_pos))
               sync_logdebug(req.context_sync, "Insert ot_type '%s' to odoo" % odoo_pos['name'] )
               sync_stat_create(req.context_sync['stat-ot_type'], 1)

               req.ot_type_odoo_weladee_ids[str(weladee_ot_type.OTType.ID)] = newid.id

            elif odoo_pos and odoo_pos['res-mode'] == 'update':
                odoo_id = req.ot_type_obj.search([('id','=',odoo_pos['res-id'])])
                if odoo_id.id:
                   odoo_id.write(sync_clean_up(odoo_pos))
                   sync_logdebug(req.context_sync, "Updated ot_type '%s' to odoo" % odoo_pos['name'] )
                   sync_stat_update(req.context_sync['stat-ot_type'], 1)

                   req.ot_type_odoo_weladee_ids[str(weladee_ot_type.OTType.ID)] = odoo_id.id
                else:
                   sync_logdebug(req.context_sync, 'weladee > %s' % weladee_ot_type) 
                   sync_logerror(req.context_sync, "Not found this odoo ot_type id %s of '%s' in odoo" % (odoo_pos['res-id'], odoo_pos['name']) ) 
                   sync_stat_error(req.context_sync['stat-ot_type'], 1)

    except Exception as e:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        if sync_weladee_error(weladee_ot_type, 'ot_type', e, req.context_sync):
           return
    #stat
    sync_stat_info(req.context_sync,'stat-ot_type','[ot_type] updating changes from weladee-> odoo')