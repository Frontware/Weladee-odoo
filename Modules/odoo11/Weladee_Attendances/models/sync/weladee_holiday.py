# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import datetime

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, sync_loginfo, sync_logerror, sync_logdebug 
from odoo.addons.Weladee_Attendances.models.sync.weladee_log import get_emp_odoo_weladee_ids

def sync_company_holiday_data(weladee_holiday, odoo_weladee_ids, context_sync, com_holiday_obj):
    '''
    company holiday data to sync
    '''
    print(weladee_holiday)
    hol = {'company_holiday_description': weladee_holiday.Holiday.NameEnglish or weladee_holiday.Holiday.NameThai,
           'company_holiday_date': datetime.datetime.strptime(str(weladee_holiday.Holiday.date),'%Y%m%d').strftime('%Y-%m-%d'),
           'active':weladee_holiday.Holiday.active}

    if weladee_holiday.odoo and weladee_holiday.odoo.odoo_id:
       hol['mode'] = 'update'
       hol['res-id'] = weladee_holiday.odoo.odoo_id
    else:
       #find record
       hold = com_holiday_obj.search([('company_holiday_date','=',datetime.datetime.strptime(str(weladee_holiday.Holiday.date),'%Y%m%d').strftime('%Y-%m-%d'))])
       if hold:
          hol['mode'] = 'update-link'  
          hol['res-id'] = hold.id
       else:     
          hol['mode'] = 'create' 
          hol['res-id'] = ''
    
    hol['res-type'] = 'company'
    print(hol)
    return hol

def sync_holiday_data(weladee_holiday, odoo_weladee_ids, context_sync, holiday_status_id, holiday_obj, com_holiday_obj):
    '''
    holiday data to sync
    '''
    print(weladee_holiday)
    if not weladee_holiday.Holiday.EmployeeID:
       return sync_company_holiday_data(weladee_holiday, odoo_weladee_ids, context_sync, com_holiday_obj)

    hol = {'name': weladee_holiday.Holiday.NameEnglish or weladee_holiday.Holiday.NameThai,
           'date_from': datetime.datetime.strptime(str(weladee_holiday.Holiday.date),'%Y%m%d').strftime('%Y-%m-%d') + ' 00:00:00',
           'date_to': datetime.datetime.strptime(str(weladee_holiday.Holiday.date),'%Y%m%d').strftime('%Y-%m-%d') + ' 23:59:59',
           'employee_id':odoo_weladee_ids.get('%s' % weladee_holiday.Holiday.EmployeeID,False),
           'holiday_status_id': holiday_status_id,
           'number_of_days_temp': 1,
           'holiday_type':'employee'}

    if weladee_holiday.odoo and weladee_holiday.odoo.odoo_id:
       hol['mode'] = 'update'
       hol['res-id'] = weladee_holiday.odoo.odoo_id
    else:
       #find record
       hold = holiday_obj.search([('employee_id','=',odoo_weladee_ids.get('%s' % weladee_holiday.Holiday.EmployeeID,False)),
                           ('date_from','=',datetime.datetime.strptime(str(weladee_holiday.Holiday.date),'%Y%m%d').strftime('%Y-%m-%d') + ' 00:00:00')])
       if hold:
          hol['mode'] = 'update-link'  
          hol['res-id'] = hold.id
       else:     
          hol['mode'] = 'create' 
          hol['res-id'] = ''
    
    hol['res-type'] = 'employee'
    print(hol)
    return hol

def sync_holiday(emp_obj, holiday_obj, com_holiday_obj, authorization, context_sync, odoo_weladee_ids, holiday_status_id):
    '''
    sync all holiday from weladee (1 way from weladee)

    '''
    #get change data from weladee
    odoo_weladee_ids = {}
    odoo_hol = {}
    sync_loginfo(context_sync, 'updating changes from weladee-> odoo')
    try:
        sync_loginfo(context_sync, 'updating holiday')
        for weladee_holiday in stub.GetHolidays(weladee_pb2.Empty(), metadata=authorization):
            odoo_hol = {}
            sync_logdebug(context_sync, weladee_holiday)
            if weladee_holiday and weladee_holiday.Holiday:
               #if empty, create one 
               if not odoo_weladee_ids: 
                  sync_logdebug(context_sync, 'getting all employee-weladee link') 
                  odoo_weladee_ids = get_emp_odoo_weladee_ids(emp_obj, odoo_weladee_ids)

               odoo_hol = sync_holiday_data(weladee_holiday, odoo_weladee_ids, context_sync, holiday_status_id, holiday_obj, com_holiday_obj)

               if odoo_hol and odoo_hol['mode'] == 'create':
                  if odoo_hol['res-type']  == 'employee':
                     holiday_odoo_id = holiday_obj.create(odoo_hol) 
                  elif odoo_hol['res-type']  == 'company':
                     holiday_odoo_id = com_holiday_obj.create(odoo_hol)  
                  if holiday_odoo_id:
                     #update record to weladee
                     weladee_holiday.odoo.odoo_id = holiday_odoo_id.id
                     weladee_holiday.odoo.odoo_created_on = int(time.time())
                     weladee_holiday.odoo.odoo_synced_on = int(time.time())

                     try:
                        __ = stub.UpdateHoliday(weladee_holiday, metadata=authorization)
                        sync_logdebug(context_sync, 'Updated this holiday id %s in weladee' % holiday_odoo_id)
                     except Exception as e:
                        sync_logerror(context_sync, e)         
                        sync_logerror(context_sync, 'Error while update this holiday id %s in weladee' % holiday_odoo_id)        
                  else:
                     sync_logerror(context_sync, 'Error while create this holiday %s in odoo' % odoo_hol['res-id'])

               elif odoo_hol and odoo_hol['mode'] == 'update':
                  oldrec_look = False 
                  if odoo_hol['res-type']  == 'employee': 
                     oldrec = holiday_obj.browse(odoo_hol['res-id'])
                     oldrec_look = holiday_obj.search([('id','=',odoo_hol['res-id'])])
                  elif odoo_hol['res-type']  == 'company':
                     oldrec = com_holiday_obj.browse(odoo_hol['res-id'])
                     oldrec_look = com_holiday_obj.search([('id','=',odoo_hol['res-id'])])

                  if oldrec_look:
                     if oldrec.write(odoo_hol):
                        #update record to weladee
                        sync_logdebug(context_sync, 'Updated this holiday id %s in odoo' % odoo_hol['res-id'])
                     else:
                        sync_logerror(context_sync, 'Error while update this holiday id %s in odoo' % odoo_hol['res-id'])        
                  else:
                    sync_logerror(context_sync, 'Not found this holiday id %s in odoo' % odoo_hol['res-id'])
               
               elif odoo_hol and odoo_hol['mode'] == 'update-link':
                    #update record to weladee
                    weladee_holiday.odoo.odoo_id = odoo_hol['res-id']
                    weladee_holiday.odoo.odoo_created_on = int(time.time())
                    weladee_holiday.odoo.odoo_synced_on = int(time.time())

                    try:
                        __ = stub.UpdateHoliday(weladee_holiday, metadata=authorization)
                        sync_logdebug(context_sync, 'Updated this holiday id %s in weladee' % odoo_hol['res-id'])
                    except Exception as e:
                        sync_logerror(context_sync, e)         
                        sync_logerror(context_sync, 'Error while update this holiday id %s in weladee' % odoo_hol['res-id'])        
            else:
                sync_logdebug(context_sync, 'no holiday found')

    except Exception as e:
        sync_logerror(context_sync, odoo_hol)
        sync_logerror(context_sync, 'error while updating holiday %s' % e)
                        