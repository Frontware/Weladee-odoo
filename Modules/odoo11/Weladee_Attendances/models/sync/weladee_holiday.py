# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, sync_loginfo, sync_logerror, sync_logdebug 
from odoo.addons.Weladee_Attendances.models.sync.weladee_log import get_emp_odoo_weladee_ids

def sync_holiday_data(weladee_holiday, odoo_weladee_ids, context_sync):
    '''
    holiday data to sync
    '''
    return {}

def sync_holiday(emp_obj, holiday_obj, authorization, context_sync, odoo_weladee_ids):
    '''
    sync all holiday from weladee (1 way from weladee)

    '''
    #get change data from weladee
    odoo_weladee_ids = {}
    try:
        sync_loginfo(context_sync, 'updating changes from weladee-> odoo')
        for weladee_holiday in stub.GetCompanyHolidays(weladee_pb2.Empty(), metadata=authorization):
            sync_logdebug(context_sync, weladee_holiday)
            if weladee_holiday and weladee_holiday.Holiday:
               #if empty, create one 
               if not odoo_weladee_ids: 
                  sync_logdebug(context_sync, 'getting all employee-weladee link') 
                  odoo_weladee_ids = get_emp_odoo_weladee_ids(emp_obj, odoo_weladee_ids)

               odoo_hol = sync_holiday_data(weladee_holiday, odoo_weladee_ids, context_sync)

               if odoo_hol and odoo_hol['mode'] == 'create':
                  holiday_odoo_id = holiday_obj.create(odoo_hol) 
                  if holiday_odoo_id:
                     #update record to weladee
                     newHoliday = odoo_pb2.HolidayOdoo()
                     newHoliday.odoo.odoo_id = holiday_odoo_id.id
                     newHoliday.odoo.odoo_created_on = int(time.time())
                     newHoliday.odoo.odoo_synced_on = int(time.time())

                     try:
                        __ = stub.UpdateHoliday(newHoliday, metadata=authorization)
                        sync_logdebug(context_sync, 'Updated this holiday id %s in weladee' % odoo_hol['res-id'])
                     except Exception as e :
                        sync_logerror(context_sync, 'Error while update this holiday id %s in weladee' % odoo_hol['res-id'])        
                  else:
                     sync_logerror(context_sync, 'Error while create this holiday %s in odoo' % odoo_hol['res-id'])

               elif odoo_hol and odoo_hol['mode'] == 'update':
                  oldrec = holiday_obj.browse(odoo_hol['res-id'])
                  if holiday_obj.search([('id','=',odoo_hol['res-id'])]):
                     if oldrec.write(odoo_hol):
                        #update record to weladee
                        sync_logdebug(context_sync, 'Updated this holiday id %s in odoo' % odoo_hol['res-id'])
                     else:
                        sync_logerror(context_sync, 'Error while update this holiday id %s in odoo' % odoo_hol['res-id'])        
                  else:
                    sync_logerror(context_sync, 'Not found this holiday id %s in odoo' % odoo_hol['res-id'])
            else:
                sync_logdebug(context_sync, 'no holiday found')

    except Exception as e:
        sync_logdebug(context_sync, weladee_holiday)
        sync_logerror(context_sync, 'error while updating log %s' % e)
            