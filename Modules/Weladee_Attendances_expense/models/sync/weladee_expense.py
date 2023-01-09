# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
from dateutil.relativedelta import relativedelta
import traceback
import requests
import base64

from odoo.addons.Weladee_Attendances.models.grpcproto.job_pb2 import ApplicationRefused
from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2, weladee_pb2, expense_pb2
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error, sync_period
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info,sync_clean_up,sync_stat_skip
from odoo.addons.Weladee_Attendances.models.sync.weladee_employee import get_emp_odoo_weladee_ids

base_url = 'https://www.weladee.com/expense/req/'

def sync_expense_data(weladee_expense, req):
    '''
    expense data to sync
    '''
    dd = datetime.datetime.fromtimestamp( weladee_expense.Expense.Date )
    data = {'weladee_id': weladee_expense.Expense.ID,
            'weladee_url':base_url + str(weladee_expense.Expense.ID),
            'quantity': 1, 
            'employee_id': req.employee_odoo_weladee_ids.get(str(weladee_expense.Expense.EmployeeID)), 
            'date': dd, 
            'product_id': req.config.expense_product_id,
            'unit_amount': 1,
            'refuse_reason': weladee_expense.Expense.Reason,
            'quantity': weladee_expense.Expense.AmountToRefund / 100,
            'request_amount': weladee_expense.Expense.Amount / 100,
            'reference': weladee_expense.Expense.Ref,
            'expense_type_id': req.expense_type_odoo_weladee_ids.get(str(weladee_expense.Expense.ExTypeID), False),
            'journal_id': req.config.expense_journal_id,
            }    

    if weladee_expense.Expense.AmountToRefund == 0:
       data['quantity'] = weladee_expense.Expense.Amount / 100

    data['name'] = 'expense %s' % dd.strftime('%Y-%m-%d')
    # vendor
    vid = req.customer_obj.search([('name','=', weladee_expense.Expense.Vendor)])
    if vid and len(vid) > 0:
        data['bill_partner_id'] = vid[0].id
    else:
        vid = req.customer_obj.create({'name':weladee_expense.Expense.Vendor})    
        data['bill_partner_id'] = vid.id

    # check state
    if weladee_expense.Expense.Status == expense_pb2.ExpenseStatusApproved:
       data['state'] = 'approved' 
    elif weladee_expense.Expense.Status == expense_pb2.ExpenseStatusRefused:
       data['state'] = 'refused' 
    elif weladee_expense.Expense.Status == expense_pb2.ExpenseStatusRefunded:
       data['state'] = 'done' 

    ipfschange = True
    odoo_exp = req.expense_obj.search([("weladee_id", "=", weladee_expense.Expense.ID)],limit=1) 
    if not odoo_exp.id:
       data['res-mode'] = 'create'
    else:
       data['res-mode'] = 'update'  
       data['res-id'] = odoo_exp.id       
       if weladee_expense.Expense.IPFS:
          if odoo_exp.receipt_file_name == weladee_expense.Expense.IPFS:
             ipfschange = False

    if not data['employee_id']:
       data['res-mode'] = ''   
       sync_logwarn(req.context_sync, 'can''t find this weladee employee id %s in odoo' % weladee_expense.Expense.EmployeeID)
       sync_stat_skip(req.context_sync['stat-expense'], 1)
    
    if ipfschange:
        if weladee_expense.Expense.IPFS:
            try:
                r = requests.get(weladee_expense.Expense.IPFS)
                content = r.content
                data['receipt'] = base64.b64encode(content)
                data['receipt_file_name'] = data['name']
            except requests.Timeout as e:
                sync_logwarn(req.context_sync, 'request: %s' % e)
            except requests.RequestException as e:
                sync_logwarn(req.context_sync, 'request: %s' % e)
            except Exception as e:
                sync_logwarn(req.context_sync, 'Error: %s' % (e or 'undefined'))
        else:
            data['receipt_file_name'] = False
            data['receipt'] = False

    if not data['employee_id'] in req.employee_user:
       req.employee_user[str(data['employee_id'])] = req.employee_obj.browse(data['employee_id']).user_id

    return data

def _setstate(odoo_id, odoo_expense, req):
     if odoo_id.sheet_id:                                           
        # get state = done but old one is not
        if odoo_expense.get('state', False) == 'done' and odoo_id.sheet_id.state != odoo_expense.get('state', False):
           # check employee home address
           if not odoo_id.sheet_id.employee_id.address_home_id.id:
              user = req.employee_user.get(str(odoo_id.sheet_id.employee_id.id))  
              if user:
                 odoo_id.sheet_id.employee_id.with_context({'mail_create_nosubscribe':False,'send2-weladee': False}).address_home_id = user.partner_id.id
              else:
                 sync_logerror(req.context_sync, 'Error: no user define for this employee %s(%s)' % (odoo_id.sheet_id.employee_id.name, odoo_id.sheet_id.employee_id.id))
       
           if not odoo_id.sheet_id.employee_id.address_home_id.id: 
              raise Exception('Employee %s(%s) has no home address' % (odoo_id.sheet_id.employee_id.name, odoo_id.sheet_id.employee_id.id))

           # post first
           odoo_id.sheet_id.journal_id = odoo_expense['journal_id']
           # seem not to be sure to activate this
           #odoo_id.sheet_id.with_context({'mail_create_nosubscribe':False,'send2-weladee': False}).action_sheet_move_create()
           odoo_expense['state'] = 'approve'

        # change to state    
        sheetst = odoo_expense.get('state', False)
        if sheetst == 'refused': sheetst = 'cancel'
        elif sheetst == 'approved': sheetst = 'approve'
        odoo_id.sheet_id.with_context({'mail_create_nosubscribe':False,'send2-weladee': False}).write({'state': sheetst}) 

def sync_expense(req):
    '''
    sync all expense from weladee (1 way from weladee)

    '''
    req.context_sync['stat-expense'] = {'to-sync':0, "create":0, "update": 0, "error":0, 'skip': 0}
    odoo_expense = False
    weladee_expense = False

    #if empty, create one 
    if not req.employee_odoo_weladee_ids: 
        sync_logdebug(req.context_sync, 'getting all employee-weladee link') 
        req.employee_odoo_weladee_ids = get_emp_odoo_weladee_ids(req)
    
    try:        
        sync_loginfo(req.context_sync,'[expense] updating changes from weladee-> odoo')

        # Calculate period
        period = sync_period(req.config.expense_period, req.config.expense_period_unit)

        for weladee_expense in stub.GetExpenses(period, metadata=req.config.authorization):            
            
            sync_stat_to_sync(req.context_sync['stat-expense'], 1)
            if not weladee_expense :
               sync_logwarn(req.context_sync,'weladee expense is empty')
               continue

            odoo_expense = sync_expense_data(weladee_expense, req)
            
            if odoo_expense and odoo_expense['res-mode'] == 'create':
                newid = req.expense_obj.with_context({'mail_create_nosubscribe':False,'send2-weladee': False}).create(sync_clean_up(odoo_expense))
                if newid and newid.id:
                    sync_logdebug(req.context_sync, "Insert expense '%s' to odoo" % odoo_expense )
                    sync_stat_create(req.context_sync['stat-expense'], 1)

                    sheetst = odoo_expense.get('state', False)
                    if sheetst == 'done': sheetst = 'approve'
                    elif sheetst == 'refused': sheetst = 'cancel'
                    elif sheetst == 'approved': sheetst = 'approve'

                    req.expense_sheet_obj.with_context({'mail_create_nosubscribe':False,'send2-weladee': False}).create({
                        'name': newid.name,
                        'employee_id': newid.employee_id.id,
                        'expense_line_ids': [(6,0,[newid.id])],
                        'journal_id': odoo_expense['journal_id'],
                        'state': sheetst
                    })

                    _setstate(newid, odoo_expense, req) 
                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_expense) 
                    sync_logerror(req.context_sync, "error while create odoo expense id %s of '%s' in odoo" % (odoo_expense['res-id'], odoo_expense) ) 
                    sync_stat_error(req.context_sync['stat-expense'], 1)

            elif odoo_expense and odoo_expense['res-mode'] == 'update':
                odoo_id = req.expense_obj.browse(odoo_expense['res-id'])
                if odoo_id.id:
                   odoo_id.with_context({'mail_create_nosubscribe':False,'send2-weladee': False}).write(sync_clean_up(odoo_expense))
                   _setstate(odoo_id, odoo_expense, req) 

                   sync_logdebug(req.context_sync, "Updated expense '%s' to odoo" % odoo_expense['name'] )
                   sync_stat_update(req.context_sync['stat-expense'], 1)
                else:
                   sync_logdebug(req.context_sync, 'weladee > %s' % weladee_expense) 
                   sync_logerror(req.context_sync, "Not found this odoo expense id %s of '%s' in odoo" % (odoo_expense['res-id'], odoo_expense['name']) ) 
                   sync_stat_error(req.context_sync['stat-expense'], 1)


    except Exception as e:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        sync_logdebug(req.context_sync, 'odoo >> %s' % odoo_expense) 
        if sync_weladee_error(weladee_expense, 'expense', e, req.context_sync):
            return
    #stat
    sync_stat_info(req.context_sync,'stat-expense','[expense] updating changes from weladee-> odoo')