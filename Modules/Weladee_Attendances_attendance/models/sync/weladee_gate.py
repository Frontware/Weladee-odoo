# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import traceback

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub, myrequest, sync_clean_up, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error, renew_connection, sync_image
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info

def sync_gate_data(weladee_gate, req):
    '''
    gate data to sync
    '''
    gate = {"name" : weladee_gate.gate.name_english,
           "name-th" : weladee_gate.gate.name_thai,
           "weladee_id" : weladee_gate.gate.ID,
           'weladee_url': 'https://www.weladee.com/gate/%s' % weladee_gate.gate.ID
            }

    # look if there is odoo record with same weladee-id
    # if not found then create else update    
    odoo_gate = req.gate_obj.search([("weladee_id", "=", weladee_gate.gate.ID)],limit=1) 
    if not odoo_gate.id:
       gate['res-mode'] = 'create'
    else:
       gate['res-mode'] = 'update'  
       gate['res-id'] = odoo_gate.id

    return gate          

def sync_gate(self, req):
    '''
    sync all gates from weladee

    '''
    req.context_sync['stat-gate'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    req.context_sync['stat-w-gate'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    #get change data from weladee
    try:
        weladee_gate = False
        sync_loginfo(req.context_sync,'[gate] updating changes from weladee-> odoo')
        for weladee_gate in stub.GetGates(weladee_pb2.Empty(), metadata=req.config.authorization,timeout=5):
            
            sync_stat_to_sync(req.context_sync['stat-gate'], 1)
            if not weladee_gate :
               sync_logwarn(req.context_sync,'weladee gate is empty')
               continue
            
            odoo_pos = sync_gate_data(weladee_gate, req)

            if odoo_pos and odoo_pos['res-mode'] == 'create':
               newid = req.gate_obj.sudo().create(sync_clean_up(odoo_pos))
               sync_logdebug(req.context_sync, "Insert gate '%s' to odoo" % odoo_pos['name'] )
               sync_stat_create(req.context_sync['stat-gate'], 1)

               req.gate_odoo_weladee_ids[str(weladee_gate.gate.ID)] = newid.id

            elif odoo_pos and odoo_pos['res-mode'] == 'update':
                odoo_id = req.gate_obj.sudo().search([('id','=',odoo_pos['res-id'])])
                if odoo_id.id:
                   odoo_id.sudo().write(sync_clean_up(odoo_pos))
                   sync_logdebug(req.context_sync, "Updated gate '%s' to odoo" % odoo_pos['name'] )
                   sync_stat_update(req.context_sync['stat-gate'], 1)

                   req.gate_odoo_weladee_ids[str(weladee_gate.gate.ID)] = odoo_id.id
                else:
                   sync_logdebug(req.context_sync, 'weladee > %s' % weladee_gate) 
                   sync_logerror(req.context_sync, "Not found this odoo gate id %s of '%s' in odoo" % (odoo_pos['res-id'], odoo_pos['name']) ) 
                   sync_stat_error(req.context_sync['stat-gate'], 1)

    except Exception as e:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        if sync_weladee_error(weladee_gate, 'gate', e, req.context_sync):
           return
    #stat
    sync_stat_info(req.context_sync,'stat-gate','[gate] updating changes from weladee-> odoo')