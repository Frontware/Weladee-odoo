# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
import traceback
from odoo.addons.Weladee_Attendances.models.grpcproto.job_pb2 import ApplicationRefused
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info,sync_clean_up

def sync_expense_data(weladee_expense, req):
    '''
    expense data to sync
    '''
    dd = datetime.datetime.fromtimestamp( weladee_expense.Expense.Date )
    data = {'weladee_id': weladee_expense.Expense.ID, 
            'quantity': 1, 
            'employee_id': req.employee_odoo_weladee_ids.get(str(weladee_expense.Expense.EmployeeID)), 
            'date': dd, 
            'product_id': req.config.expense_product_id,
            'unit_amount': weladee_expense.Expense.Amount / 100,
            'reference': weladee_expense.Expense.Ref,
            }        
    data['name'] = 'expense %s' % dd.strftime('%Y-%m-%d')
    # vendor
    vid = req.customer_obj.search([('name','=', weladee_expense.Expense.Vendor)])
    if vid and len(vid) > 0:
        data['bill_partner_id'] = vid[0].id
    else:
        vid = req.customer_obj.create({'name':weladee_expense.Expense.Vendor})    
        data['bill_partner_id'] = vid.id

    odoo_exp = req.expense_obj.search([("weladee_id", "=", weladee_expense.Expense.ID)],limit=1) 
    if not odoo_exp.id:
       data['res-mode'] = 'create'
    else:
       data['res-mode'] = 'update'  
       data['res-id'] = odoo_exp.id

    return data   

def sync_expense(req):
    '''
    sync all expense from weladee (1 way from weladee)

    '''
    req.context_sync['stat-expense'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    odoo_expense = False
    weladee_expense = False
    
    try:        
        sync_loginfo(req.context_sync,'[expense] updating changes from weladee-> odoo')
        for weladee_expense in stub.GetExpenses(weladee_pb2.Empty(), metadata=req.config.authorization):
            print(weladee_expense)
            sync_stat_to_sync(req.context_sync['stat-expense'], 1)
            if not weladee_expense :
               sync_logwarn(req.context_sync,'weladee expense is empty')
               continue

            odoo_expense = sync_expense_data(weladee_expense, req)
            
            if odoo_expense and odoo_expense['res-mode'] == 'create':
                newid = req.expense_obj.create(sync_clean_up(odoo_expense))
                if newid and newid.id:
                    sync_logdebug(req.context_sync, "Insert expense '%s' to odoo" % odoo_expense )
                    sync_stat_create(req.context_sync['stat-expense'], 1)

                    req.attach_obj.create({
                        'type': 'url',
                        'url': weladee_expense.Expense.IPFS,
                        'name': newid.name,
                        'res_model': 'hr.expense',
                        'res_id': newid.id
                    })

                    req.expense_sheet_obj.create({
                        'name': newid.name,
                        'employee_id': newid.employee_id.id,
                        'expense_line_ids': [(6,0,[newid.id])],
                    })

                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_expense) 
                    sync_logerror(req.context_sync, "error while create odoo expense id %s of '%s' in odoo" % (odoo_expense['res-id'], odoo_expense) ) 
                    sync_stat_error(req.context_sync['stat-expense'], 1)

            elif odoo_expense and odoo_expense['res-mode'] == 'update':
                odoo_id = req.expense_obj.browse(odoo_expense['res-id'])
                if odoo_id.id:
                   odoo_id.write(sync_clean_up(odoo_expense))
                   sync_logdebug(req.context_sync, "Updated expense '%s' to odoo" % odoo_expense['name'] )
                   sync_stat_update(req.context_sync['stat-expense'], 1)
                else:
                   sync_logdebug(req.context_sync, 'weladee > %s' % weladee_expense) 
                   sync_logerror(req.context_sync, "Not found this odoo expense id %s of '%s' in odoo" % (odoo_expense['res-id'], odoo_expense['name']) ) 
                   sync_stat_error(req.context_sync['stat-expense'], 1)


    except Exception as e:
        print(traceback.format_exc())
        sync_logdebug(req.context_sync, 'odoo >> %s' % odoo_expense) 
        if sync_weladee_error(weladee_expense, 'expense', e, req.context_sync):
            return
    #stat
    sync_stat_info(req.context_sync,'stat-expense','[expense] updating changes from weladee-> odoo')