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
from odoo.addons.Weladee_Attendances.models.weladee_settings import get_holiday_notify, get_holiday_notify_email

def sync_company_holiday_data(weladee_holiday, odoo_weladee_ids, context_sync, com_holiday_obj):
    '''
    company holiday data to sync
    '''
    date = datetime.datetime.strptime(str(weladee_holiday.Holiday.date),'%Y%m%d').strftime('%Y-%m-%d')
    data = {'company_holiday_description': weladee_holiday.Holiday.NameEnglish or weladee_holiday.Holiday.NameThai,
            'company_holiday_date': date,
            'company_holiday_active':weladee_holiday.Holiday.active,
            'company_holiday_notes':'sync from weladee %s' % weladee_holiday.Holiday.ID}
    data['res-type'] = 'company'
    # look if there is odoo record with same time
    # if not found then create else update    
    oldid = com_holiday_obj.search([('company_holiday_date','=',date),'|',('company_holiday_active','=',True),('company_holiday_active','=',False)])
    if not oldid.id:
       data['res-mode'] = 'create'
    else:
       data['res-mode'] = 'update'  
       data['res-id'] = oldid.id       
    
    # there is previous link
    if weladee_holiday.odoo and weladee_holiday.odoo.odoo_id:
        oldid = com_holiday_obj.search( [ ('id','=', weladee_holiday.odoo.odoo_id),'|',('company_holiday_active','=',True),('company_holiday_active','=',False)])
        if oldid.id:
           #update link
           data['res-id'] = oldid.id
           data['res-mode'] = 'update'

        else:
            sync_logdebug(context_sync, 'weladee > %s ' % weladee_holiday)
            sync_logwarn(context_sync, 'can''t find this odoo-id %s in company holiday' % weladee_holiday.odoo.odoo_id)

    return data      

def sync_holiday_data(self, weladee_holiday, odoo_weladee_ids, context_sync, holiday_status_id, holiday_obj, com_holiday_obj):
    '''
    holiday data to sync
    '''
    if not weladee_holiday.Holiday.EmployeeID:
       return sync_company_holiday_data(weladee_holiday, odoo_weladee_ids, context_sync, com_holiday_obj)

    date = datetime.datetime.strptime(str(weladee_holiday.Holiday.date),'%Y%m%d')
    data = {'name': (weladee_holiday.Holiday.NameEnglish or weladee_holiday.Holiday.NameThai or '').strip(' '),
            'date_from': _convert_to_tz_time(self, date.strftime('%Y-%m-%d') + ' 00:00:00'),
            'date_to': _convert_to_tz_time(self, date.strftime('%Y-%m-%d') + ' 23:59:59'),
            'employee_id':odoo_weladee_ids.get('%s' % weladee_holiday.Holiday.EmployeeID,False),
            'holiday_status_id': holiday_status_id,
            'number_of_days': 1,
            'holiday_type':'employee',
            'weladee_code': weladee_holiday.Holiday.code,
            'weladee_sick': weladee_holiday.Holiday.sickLeave,
            'state':'validate'}
    
    data['request_date_from'] = data['date_from']
    data['request_date_to'] = data['date_to']
   
    # look if there is odoo record with same time
    # if not found then create else update    
    oldid = holiday_obj.search([('employee_id','=',odoo_weladee_ids.get('%s' % weladee_holiday.Holiday.EmployeeID,False)),
                                ('date_from','=', _convert_to_tz_time(self, date.strftime('%Y-%m-%d') + ' 00:00:00').strftime('%Y-%m-%d 00:00:00'))])
    if not oldid.id:
       data['res-mode'] = 'create'
    else:
       data['res-mode'] = 'update'  
       data['res-id'] = oldid.id       
    data['res-type'] = 'employee'
    # there is previous link
    if weladee_holiday.odoo and weladee_holiday.odoo.odoo_id:
        oldid = holiday_obj.search( [ ('id','=', weladee_holiday.odoo.odoo_id)])
        if oldid.id:
           #update link
           data['res-id'] = oldid.id
           data['res-mode'] = 'update'

        else:
            sync_logdebug(context_sync, 'weladee > %s ' % weladee_holiday)
            sync_logwarn(context_sync, 'can''t find this odoo-id %s in odoo holiday, will skip and not update' % weladee_holiday.odoo.odoo_id)
            data['res-mode'] = ''

    return data   

def _update_weladee_holiday_back(weladee_holiday, holiday_odoo, context_sync, stub, authorization):
    #update record to weladee
    weladee_holiday.odoo.odoo_id = holiday_odoo.id
    weladee_holiday.odoo.odoo_created_on = int(time.time())
    weladee_holiday.odoo.odoo_synced_on = int(time.time())

    try:
        __ = stub.UpdateHoliday(weladee_holiday, metadata=authorization)
        sync_logdebug(context_sync, 'Updated this holiday id %s in weladee' % holiday_odoo.id)
    except Exception as e:
        sync_logerror(context_sync, e)         
        sync_logerror(context_sync, 'Error while update this holiday id %s in weladee' % holiday_odoo.id) 

def sync_holiday(self, emp_obj, holiday_obj, com_holiday_obj, authorization, context_sync, odoo_weladee_ids, holiday_status_id, to_email):
    '''
    sync all holiday from weladee (1 way from weladee)
    2018-11-14 KPO change hr.holidays to hr.leave
    '''
    context_sync['stat-hol'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    odoo_hol = False
    weladee_holiday = False
    try:        
        sync_loginfo(context_sync,'[log] updating changes from weladee-> odoo')
        for weladee_holiday in stub.GetHolidays(weladee_pb2.Empty(), metadata=authorization):
            sync_stat_to_sync(context_sync['stat-hol'], 1)
            if not weladee_holiday :
               sync_logwarn(context_sync,'weladee holiday is empty')
               continue

            #if empty, create one 
            if not odoo_weladee_ids: 
                sync_logdebug(context_sync, 'getting all employee-weladee link') 
                odoo_weladee_ids = get_emp_odoo_weladee_ids(emp_obj, odoo_weladee_ids)
            
            odoo_hol = sync_holiday_data(self, weladee_holiday, odoo_weladee_ids, context_sync, holiday_status_id, holiday_obj, com_holiday_obj)
            
            if odoo_hol and odoo_hol['res-mode'] == 'create':
                newid = False
                if odoo_hol['res-type']  == 'employee':
                     newid = holiday_obj.create(odoo_hol) 
                elif odoo_hol['res-type']  == 'company':
                     newid = com_holiday_obj.create(sync_clean_up(odoo_hol))
                if newid and newid.id:
                    sync_logdebug(context_sync, "Insert holiday '%s' to odoo" % odoo_hol )
                    sync_stat_create(context_sync['stat-hol'], 1)

                    _update_weladee_holiday_back(weladee_holiday, newid, context_sync, stub, authorization)
                else:
                    sync_logdebug(context_sync, 'weladee > %s' % weladee_holiday) 
                    sync_logerror(context_sync, "error while create odoo holiday id %s of '%s' in odoo" % (odoo_hol['res-id'], odoo_hol) ) 
                    sync_stat_error(context_sync['stat-hol'], 1)

            elif odoo_hol and odoo_hol['res-mode'] == 'update':
                odoo_id = False
                if odoo_hol['res-type']  == 'employee':
                     odoo_id = holiday_obj.search([('id','=',odoo_hol['res-id'])])
                elif odoo_hol['res-type']  == 'company':
                     odoo_id = com_holiday_obj.search([('id','=',odoo_hol['res-id']),'|',('company_holiday_active','=',True),('company_holiday_active','=',False)])
                
                if odoo_id and odoo_id.id:
                    if odoo_id.write(sync_clean_up(odoo_hol)):
                        sync_logdebug(context_sync, "Updated holiday '%s' to odoo" % odoo_hol )
                        sync_stat_update(context_sync['stat-hol'], 1)

                        _update_weladee_holiday_back(weladee_holiday, odoo_id, context_sync, stub, authorization)                     
                    else:
                        sync_logdebug(context_sync, 'odoo > %s' % odoo_hol) 
                        sync_logerror(context_sync, "error found while update this odoo holiday id %s" % odoo_hol['res-id']) 
                        sync_stat_error(context_sync['stat-hol'], 1)

                else:
                   sync_logdebug(context_sync, 'weladee > %s' % weladee_holiday) 
                   sync_logerror(context_sync, "Not found this odoo holiday id %s of '%s' in odoo" % (odoo_hol['res-id'], odoo_hol) ) 
                   sync_stat_error(context_sync['stat-hol'], 1)

    except Exception as e:
        sync_logdebug(context_sync, 'odoo >> %s' % odoo_hol) 

        # extra options
        if to_email and get_holiday_notify(self) and get_holiday_notify_email(self):
            if 'The number of remaining leaves is not sufficient for this leave type' in ("%s" % e):
                
                emp_name = ''
                emp = self.env['hr.employee'].search([('weladee_id','=',weladee_holiday.Holiday.EmployeeID)])
                if emp: emp_name = emp.name or 'employee (weladee id) %s' % weladee_holiday.Holiday.EmployeeID

                template = self.env.ref('Weladee_Attendances.weladee_attendance_allocate_emp_mail', raise_if_not_found=False)
                if template:
                    allocation_url='%s/web#view_type=list&model=hr.leave&menu_id=%s&action=%s' % (
                        self.env['ir.config_parameter'].search([('key','=','web.base.url')]).value,
                        self.env.ref('hr_holidays.menu_open_department_leave_allocation_approve').id,
                        self.env.ref('hr_holidays.open_department_holidays_allocation_approve').id)
                    template.with_context({'email-to':get_holiday_notify_email(self),
                                           'employee': emp_name,
                                           'url':allocation_url}).send_mail(self.id)        


        if sync_weladee_error(weladee_holiday, 'holiday', e, context_sync):
            return
    #stat
    sync_stat_info(context_sync,'stat-hol','[log] updating changes from weladee-> odoo')