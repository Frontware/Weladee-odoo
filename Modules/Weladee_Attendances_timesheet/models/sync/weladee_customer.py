# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import traceback
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info,sync_clean_up

base_url = 'https://www.weladee.com/customer/'

def sync_customer_data(weladee_customer, req):
    '''
    customer data to sync
    '''
    data = {'name': weladee_customer.Customer.NameEnglish,
            'name_thai': weladee_customer.Customer.NameThai,
            'comment': weladee_customer.Customer.Note,
            'weladee_id': weladee_customer.Customer.ID,
            'weladee_url': base_url + str(weladee_customer.Customer.ID),
            'active':weladee_customer.Customer.active,
            'customer_rank': 1}    
    data['res-mode'] = 'create'
    prev_rec = req.customer_obj.search( [ ('name','=', data['name'] )],limit=1 )
    if prev_rec and prev_rec.id:
        data['res-mode'] = '' 
        sync_logdebug(req.context_sync, 'weladee > %s ' % weladee_customer)
        sync_logdebug(req.context_sync, 'odoo > %s ' % data)
        sync_logwarn(req.context_sync, 'this customer\'name record already exist for this %s exist, no change will apply' % data['name'])

    return data   

def sync_delete_customer(req):
    del_ids = req.customer_obj.search([('weladee_id','!=',False)])
    if del_ids: 
       del_ids.unlink()
       sync_logwarn(req.context_sync, 'remove all linked customers: %s record(s)' % len(del_ids))

def sync_customer(req):
    '''
    sync all customer from weladee (1 way from weladee)

    '''
    req.context_sync['stat-cus'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    odoo_cus = False
    weladee_customer = False

    sync_delete_customer(req)

    try:        
        sync_loginfo(req.context_sync,'[customer] updating changes from weladee-> odoo')
        for weladee_customer in stub.GetCustomers(weladee_pb2.Empty(), metadata=req.config.authorization):
            sync_stat_to_sync(req.context_sync['stat-cus'], 1)
            if not weladee_customer :
               sync_logwarn(req.context_sync,'weladee customer is empty')
               continue

            odoo_cus = sync_customer_data(weladee_customer, req)
            
            if odoo_cus and odoo_cus['res-mode'] == 'create':
                newid = req.customer_obj.create(sync_clean_up(odoo_cus))
                if newid and newid.id:
                    sync_logdebug(req.context_sync, "Insert customer '%s' to odoo" % odoo_cus )
                    sync_stat_create(req.context_sync['stat-cus'], 1)

                    req.customer_odoo_weladee_ids[weladee_customer.Customer.ID] = newid.id
                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_customer) 
                    sync_logerror(req.context_sync, "error while create odoo customer id %s of '%s' in odoo" % (odoo_cus['res-id'], odoo_cus) ) 
                    sync_stat_error(req.context_sync['stat-cus'], 1)

    except Exception as e:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        sync_logdebug(req.context_sync, 'odoo >> %s' % odoo_cus) 
        if sync_weladee_error(weladee_customer, 'customer', e, req.context_sync):
            return
    #stat
    sync_stat_info(req.context_sync,'stat-cus','[customer] updating changes from weladee-> odoo')