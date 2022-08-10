# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import traceback

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub, myrequest, sync_clean_up, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error, renew_connection, sync_image
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info

def sync_expense_type_data(weladee_expense_type, req):
    '''
    expense_type data to sync
    '''
    pos = {"name" : weladee_expense_type.ExpenseType.NameEnglish,
           "name-th" : weladee_expense_type.ExpenseType.NameThai,
           "weladee_id" : weladee_expense_type.ExpenseType.ID,
           'code': weladee_expense_type.ExpenseType.Code,
           'active': weladee_expense_type.ExpenseType.Active,
            }
    if weladee_expense_type.ExpenseType.Icon:
        pos['image_1920'] = sync_image(req, weladee_expense_type.ExpenseType.Icon)

    # look if there is odoo record with same weladee-id
    # if not found then create else update    
    odoo_expense_type = req.expense_type_obj.search([("weladee_id", "=", weladee_expense_type.ExpenseType.ID)],limit=1) 
    if not odoo_expense_type.id:
       pos['res-mode'] = 'create'
    else:
       pos['res-mode'] = 'update'  
       pos['res-id'] = odoo_expense_type.id

    return pos          

def sync_expense_type(req):
    '''
    sync all expense_types from weladee

    '''
    req.context_sync['stat-expense_type'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    req.context_sync['stat-w-expense_type'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    #get change data from weladee
    try:
        weladee_expense_type = False
        sync_loginfo(req.context_sync,'[expense_type] updating changes from weladee-> odoo')
        for weladee_expense_type in stub.GetExpenseTypes(myrequest, metadata=req.config.authorization,timeout=5):
            
            sync_stat_to_sync(req.context_sync['stat-expense_type'], 1)
            if not weladee_expense_type :
               sync_logwarn(req.context_sync,'weladee expense_type is empty')
               continue
            
            odoo_pos = sync_expense_type_data(weladee_expense_type, req)

            if odoo_pos and odoo_pos['res-mode'] == 'create':
               newid = req.expense_type_obj.create(sync_clean_up(odoo_pos))
               sync_logdebug(req.context_sync, "Insert expense_type '%s' to odoo" % odoo_pos['name'] )
               sync_stat_create(req.context_sync['stat-expense_type'], 1)

               req.expense_type_odoo_weladee_ids[str(weladee_expense_type.ExpenseType.ID)] = newid.id

            elif odoo_pos and odoo_pos['res-mode'] == 'update':
                odoo_id = req.expense_type_obj.search([('id','=',odoo_pos['res-id'])])
                if odoo_id.id:
                   odoo_id.write(sync_clean_up(odoo_pos))
                   sync_logdebug(req.context_sync, "Updated expense_type '%s' to odoo" % odoo_pos['name'] )
                   sync_stat_update(req.context_sync['stat-expense_type'], 1)

                   req.expense_type_odoo_weladee_ids[str(weladee_expense_type.ExpenseType.ID)] = odoo_id.id
                else:
                   sync_logdebug(req.context_sync, 'weladee > %s' % weladee_expense_type) 
                   sync_logerror(req.context_sync, "Not found this odoo expense_type id %s of '%s' in odoo" % (odoo_pos['res-id'], odoo_pos['name']) ) 
                   sync_stat_error(req.context_sync['stat-expense_type'], 1)

    except Exception as e:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        if sync_weladee_error(weladee_expense_type, 'expense_type', e, req.context_sync):
           return
    #stat
    sync_stat_info(req.context_sync,'stat-expense_type','[expense_type] updating changes from weladee-> odoo')