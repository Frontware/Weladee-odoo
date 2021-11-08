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

def sync_customer_data(self, weladee_customer, cus_obj, context_sync):
    '''
    customer data to sync
    '''
    data = {'name': weladee_customer.Customer.NameEnglish or weladee_customer.Customer.NameThai,
            'comment': weladee_customer.Customer.Note,
            'weladee_id': weladee_customer.Customer.ID,
            'customer_rank': 1}    
    data['res-mode'] = 'create'
    prev_rec = cus_obj.search( [ ('name','=', data['name'] )],limit=1 )
    if prev_rec and prev_rec.id:
        data['res-mode'] = '' 
        sync_logdebug(context_sync, 'weladee > %s ' % weladee_customer)
        sync_logdebug(context_sync, 'odoo > %s ' % data)
        sync_logwarn(context_sync, 'this customer\'name record already exist for this %s exist, no change will appy' % data['name'])

    return data   

def sync_delete_customer(self, context_sync):
    del_ids = self.env['res.partner'].search([('weladee_id','!=',False)])
    if del_ids: 
       del_ids.unlink()
       sync_logwarn(context_sync, 'remove all linked customers: %s record(s)' % len(del_ids))

def sync_customer(self, cs_obj, authorization, context_sync, odoo_weladee_ids, to_email):
    '''
    sync all customer from weladee (1 way from weladee)

    '''
    context_sync['stat-cus'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    odoo_cus = False
    weladee_customer = False

    sync_delete_customer(self, context_sync)

    try:        
        sync_loginfo(context_sync,'[log] updating changes from weladee-> odoo')
        for weladee_customer in stub.GetCustomers(weladee_pb2.Empty(), metadata=authorization):
            sync_stat_to_sync(context_sync['stat-cus'], 1)
            if not weladee_customer :
               sync_logwarn(context_sync,'weladee customer is empty')
               continue

            odoo_cus = sync_customer_data(self, weladee_customer, cs_obj, context_sync)
            
            if odoo_cus and odoo_cus['res-mode'] == 'create':
                newid = cs_obj.create(sync_clean_up(odoo_cus))
                if newid and newid.id:
                    sync_logdebug(context_sync, "Insert customer '%s' to odoo" % odoo_cus )
                    sync_stat_create(context_sync['stat-cus'], 1)

                else:
                    sync_logdebug(context_sync, 'weladee > %s' % weladee_customer) 
                    sync_logerror(context_sync, "error while create odoo customer id %s of '%s' in odoo" % (odoo_cus['res-id'], odoo_cus) ) 
                    sync_stat_error(context_sync['stat-cus'], 1)

    except Exception as e:
        sync_logdebug(context_sync, 'odoo >> %s' % odoo_cus) 
        if sync_weladee_error(weladee_customer, 'customer', e, context_sync):
            return
    #stat
    sync_stat_info(context_sync,'stat-cus','[log] updating changes from weladee-> odoo')