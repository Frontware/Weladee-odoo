# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
from dateutil.relativedelta import relativedelta
import traceback
import requests
import base64

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2, weladee_pb2, ot_pb2
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error, sync_period
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info,sync_clean_up,sync_stat_skip
from odoo.addons.Weladee_Attendances.models.sync.weladee_employee import get_emp_odoo_weladee_ids

base_url = 'https://www.weladee.com/ot/req/'

def sync_ot_data(weladee_ot, req):
    '''
    ot data to sync
    '''
    dd = datetime.datetime.fromtimestamp( weladee_ot.ot.Date )
    data = {'weladee_id': weladee_ot.ot.ID,
            'weladee_url':base_url + str(weladee_ot.ot.ID),
            'employee_id': req.employee_odoo_weladee_ids.get(str(weladee_ot.ot.EmployeeID)), 
            'date': dd, 
            'description': '',
            'type_id': 1,
            'time_start':1,
            'time_end':1,
            'duration': 1, 
            }    

    # check state
    if weladee_ot.ot.Status == ot_pb2.otStatusApproved:
       data['state'] = 'approved' 
    elif weladee_ot.ot.Status == ot_pb2.otStatusRefused:
       data['state'] = 'refused' 
    elif weladee_ot.ot.Status == ot_pb2.otStatusRefunded:
       data['state'] = 'done' 

    if not data['employee_id']:
       data['res-mode'] = ''   
       sync_logwarn(req.context_sync, 'can''t find this weladee employee id %s in odoo' % weladee_ot.ot.EmployeeID)
       sync_stat_skip(req.context_sync['stat-ot'], 1)   

    return data

def sync_ot(req):
    '''
    sync all ot from weladee (1 way from weladee)

    '''
    req.context_sync['stat-ot'] = {'to-sync':0, "create":0, "update": 0, "error":0, 'skip': 0}
    odoo_ot = False
    weladee_ot = False

    #if empty, create one 
    if not req.employee_odoo_weladee_ids: 
        sync_logdebug(req.context_sync, 'getting all employee-weladee link') 
        req.employee_odoo_weladee_ids = get_emp_odoo_weladee_ids(req)
    
    try:        
        sync_loginfo(req.context_sync,'[ot] updating changes from weladee-> odoo')

        # Calculate period
        period = sync_period(req.config.ot_period, req.config.ot_period_unit)

        for weladee_ot in stub.Getots(period, metadata=req.config.authorization):            
            
            sync_stat_to_sync(req.context_sync['stat-ot'], 1)
            if not weladee_ot :
               sync_logwarn(req.context_sync,'weladee ot is empty')
               continue

            odoo_ot = sync_ot_data(weladee_ot, req)
            
            if odoo_ot and odoo_ot['res-mode'] == 'create':
                newid = req.ot_obj.with_context({'mail_create_nosubscribe':False,'send2-weladee': False}).create(sync_clean_up(odoo_ot))
                if newid and newid.id:
                    sync_logdebug(req.context_sync, "Insert ot '%s' to odoo" % odoo_ot )
                    sync_stat_create(req.context_sync['stat-ot'], 1)
                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_ot) 
                    sync_logerror(req.context_sync, "error while create odoo ot id %s of '%s' in odoo" % (odoo_ot['res-id'], odoo_ot) ) 
                    sync_stat_error(req.context_sync['stat-ot'], 1)

            elif odoo_ot and odoo_ot['res-mode'] == 'update':
                odoo_id = req.ot_obj.browse(odoo_ot['res-id'])
                if odoo_id.id:
                   odoo_id.with_context({'mail_create_nosubscribe':False,'send2-weladee': False}).write(sync_clean_up(odoo_ot))

                   sync_logdebug(req.context_sync, "Updated ot '%s' to odoo" % odoo_ot['name'] )
                   sync_stat_update(req.context_sync['stat-ot'], 1)
                else:
                   sync_logdebug(req.context_sync, 'weladee > %s' % weladee_ot) 
                   sync_logerror(req.context_sync, "Not found this odoo ot id %s of '%s' in odoo" % (odoo_ot['res-id'], odoo_ot['name']) ) 
                   sync_stat_error(req.context_sync['stat-ot'], 1)


    except Exception as e:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        sync_logdebug(req.context_sync, 'odoo >> %s' % odoo_ot) 
        if sync_weladee_error(weladee_ot, 'ot', e, req.context_sync):
            return
    #stat
    sync_stat_info(req.context_sync,'stat-ot','[ot] updating changes from weladee-> odoo')