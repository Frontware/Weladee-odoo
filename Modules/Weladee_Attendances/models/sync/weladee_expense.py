# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import datetime
import pytz

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import expense_pb2
from .weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info,sync_clean_up
from .weladee_log import get_emp_odoo_weladee_ids
from odoo.addons.Weladee_Attendances.library.weladee_lib import _convert_to_tz_time

def create_odoo_type(self, data, context_sync):    
    '''
    create odoo with new connection to be able to continue
    '''
    ret = False
    try:
        ret = self.env['weladee_expense_type'].create(sync_clean_up(data))
    except Exception as e:
        pass
    return ret

def create_odoo_exp(self, data, context_sync):    
    '''
    create odoo with new connection to be able to continue
    '''
    ret = False
    try:
        ret = self.env['hr.expense'].create(sync_clean_up(data))
    except Exception as e:
        pass
    return ret

def sync_delete_type(self, context_sync):
    '''
    delete the hr attendance according filter
    '''    
    del_ids = self.env['weladee_expense_type'].search([])
    dt_delete_msg = 'remove all %s expense type from all records' % len(del_ids)
    if del_ids: 
       del_ids.unlink()
       sync_logwarn(context_sync, dt_delete_msg)

def sync_delete_expense(self, context_sync, period_settings):
    '''
    delete the hr expense according filter
    '''
    dt_today = datetime.datetime.today()
    dt_unit = int(period_settings["unit"])
    dt_from = False
    if period_settings["period"] == "w":
       dt_from = dt_today - datetime.timedelta(days=(dt_unit * 7))
    elif period_settings["period"] == "m":       
       dt_from = dt_today.replace(month=dt_today.month - dt_unit) 
    elif period_settings["period"] == "y":       
       dt_from = dt_today.replace(month=dt_today.year - dt_unit)             

    dt_from_utc = False
    dt_delete_msg = ''
    if period_settings["period"] == "all":
        del_ids = self.env['hr.expense'].search([])
        dt_delete_msg = 'remove all %s expense(s) from all records' % len(del_ids)
    else:
       dt_from_utc = _convert_to_tz_time(self, dt_from.strftime('%Y-%m-%d 00:00:00'))
       del_ids = self.env['hr.expense'].search([('date','>=', dt_from_utc.strftime('%Y-%m-%d 00:00:00'))])
       dt_delete_msg = 'remove all %s expense after this period (%s)' % (len(del_ids),dt_from.strftime('%Y-%m-%d 00:00:00'))

    if del_ids: 
       del_ids.unlink()
       sync_logwarn(context_sync, dt_delete_msg)

    return dt_from_utc 

def sync_expense(self, emp_obj, exp_obj, authorization, context_sync, odoo_weladee_ids, period_settings):
    '''
    sync all expense type from weladee

    '''
    context_sync['stat-log'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    context_sync['error-emp'] = {}
    context_sync['cursor'] = False
    
    sync_delete_type(self, context_sync)
    sync_delete_expense(self, context_sync, period_settings)

    odoo_type = False
    weladee_type = False

    has_error = False
    
    try:
        sync_loginfo(context_sync,'[expense type] updating changes from weladee-> odoo')
        ireq = 0
        for weladee_type in stub.GetExpenseTypes(weladee_pb2.Empty(), metadata=authorization):
            ireq +=1
            #print('%s %s'% (ireq, weladee_att))
            sync_stat_to_sync(context_sync['stat-log'], 1)
            if not weladee_type :
                sync_logwarn(context_sync,'weladee expense type is empty')
                continue
            
            odoo_type = {
                'weladee_code': weladee_type.ExpenseType.Code,
                'name_english': weladee_type.ExpenseType.NameEnglish,
                'name_thai': weladee_type.ExpenseType.NameEnglish
            }

            newid = create_odoo_type(self, odoo_type, context_sync)                
            if newid and newid.id:
               sync_logdebug(context_sync, "Insert expense type '%s' to odoo" % odoo_type )
               sync_stat_create(context_sync['stat-log'], 1)

    except Exception as e:
        sync_logdebug(context_sync, 'weladee >> %s' % weladee_type or '-') 
        sync_logdebug(context_sync, 'odoo >> %s' % odoo_type or '-') 
        if sync_weladee_error(weladee_type, 'expense type', e, context_sync):            
           return
        else:
           has_error = True

    # stop if sync type has error.
    if has_error:
       return

    #stat
    #del context_sync['cursor']
    sync_stat_info(context_sync,'stat-log','[expense type] updating changes from weladee-> odoo')

    context_sync['stat-log'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    odoo_ex = False
    weladee_ex = False
    try:
        sync_loginfo(context_sync,'[expense] updating changes from weladee-> odoo')
        ireq = 0
        for weladee_ex in stub.GetExpenses(weladee_pb2.Empty(), metadata=authorization):
            ireq +=1
            #print('%s %s'% (ireq, weladee_att))
            sync_stat_to_sync(context_sync['stat-log'], 1)
            if not weladee_ex :
                sync_logwarn(context_sync,'weladee expense is empty')
                continue
            
            odoo_ex = {
                "name" : weladee_ex.ExpenseOdoo.NameThai or weladee_ex.ExpenseOdoo.NameEnglish
            }

            newid = create_odoo_exp(self, odoo_ex, context_sync)                
            if newid and newid.id:
               sync_logdebug(context_sync, "Insert expense '%s' to odoo" % odoo_ex )
               sync_stat_create(context_sync['stat-log'], 1)

    except Exception as e:
        sync_logdebug(context_sync, 'weladee >> %s' % weladee_ex or '-') 
        sync_logdebug(context_sync, 'odoo >> %s' % odoo_ex or '-') 
        if sync_weladee_error(weladee_ex, 'expense', e, context_sync):
           return
    #stat
    del context_sync['cursor']
    sync_stat_info(context_sync,'stat-log','[expense] updating changes from weladee-> odoo')    