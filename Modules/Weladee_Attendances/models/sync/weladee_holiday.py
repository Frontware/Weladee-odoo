# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import datetime
import traceback
import pytz

from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info,sync_clean_up
from .weladee_log import get_emp_odoo_weladee_ids
from odoo.addons.Weladee_Attendances.library.weladee_lib import _convert_to_tz_time
from odoo.addons.Weladee_Attendances.models.weladee_settings import get_holiday_notify, get_holiday_notify_email

def sync_company_holiday_data(weladee_holiday, req):
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
    oldid = req.company_holiday_obj.search([('company_holiday_date','=',date),'|',('company_holiday_active','=',True),('company_holiday_active','=',False)])
    if not oldid.id:
       data['res-mode'] = 'create'
    else:
       data['res-mode'] = 'update'  
       data['res-id'] = oldid.id       
    
    # there is previous link
    if weladee_holiday.odoo and weladee_holiday.odoo.odoo_id:
        oldid = req.company_holiday_obj.search( [ ('id','=', weladee_holiday.odoo.odoo_id),'|',('company_holiday_active','=',True),('company_holiday_active','=',False)])
        if oldid.id:
           #update link
           data['res-id'] = oldid.id
           data['res-mode'] = 'update'

        else:
            sync_logdebug(req.context_sync, 'weladee > %s ' % weladee_holiday)
            sync_logwarn(req.context_sync, 'can''t find this odoo-id %s in company holiday' % weladee_holiday.odoo.odoo_id)

    return data      

def sync_holiday_data(weladee_holiday, req, leaves_types):
    '''
    holiday data to sync
    '''
    if not weladee_holiday.Holiday.EmployeeID:
       return sync_company_holiday_data(weladee_holiday, req)

    df = datetime.datetime.strptime(str(weladee_holiday.Holiday.date) + ' 00:00:00','%Y%m%d %H:%M:%S')
    dt = datetime.datetime.strptime(str(weladee_holiday.Holiday.date) + ' 23:59:59','%Y%m%d %H:%M:%S')
    tzoffset = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone(req.config.tz)).utcoffset().total_seconds() / 60 / 60 

    df = df + datetime.timedelta(hours=0-tzoffset)
    dt = dt + datetime.timedelta(hours=0-tzoffset)
    data = {'name': (weladee_holiday.Holiday.NameEnglish or weladee_holiday.Holiday.NameThai or '').strip(' '),
            'date_from': df,
            'date_to': dt,
            'employee_id':req.employee_odoo_weladee_ids.get('%s' % weladee_holiday.Holiday.EmployeeID,False),
            'holiday_status_id': req.config.holiday_status_id,            
            'holiday_type':'employee',
            'weladee_code': weladee_holiday.Holiday.code,
            'weladee_sick': weladee_holiday.Holiday.sickLeave,
            'state':'validate'}
    
    # 2018-11-14 KPO allow multiple type, but default come from setting
    if weladee_holiday.Holiday.code in leaves_types:
        data['holiday_status_id'] = leaves_types[weladee_holiday.Holiday.code] or req.config.holiday_status_id

    if req.config.sick_status_id and weladee_holiday.Holiday.sickLeave:
        data['holiday_status_id'] = req.config.sick_status_id

    # look if there is odoo record with same time
    # if not found then create else update    
    oldid = req.leave_obj.search([('employee_id','=',req.employee_odoo_weladee_ids.get('%s' % weladee_holiday.Holiday.EmployeeID,False)),
                                ('date_from','=', df),('date_to','=', dt)])
    if not oldid.id:
       data['res-mode'] = 'create'
    else:
       data['res-mode'] = 'update'  
       data['res-id'] = oldid.id       
    data['res-type'] = 'employee'

    # there is previous link
    if weladee_holiday.odoo and weladee_holiday.odoo.odoo_id:
        oldid = req.leave_obj.search( [ ('id','=', weladee_holiday.odoo.odoo_id)])
        if oldid.id:
           #update link
           data['res-id'] = oldid.id
           data['res-mode'] = 'update'

        else:
            sync_logdebug(req.context_sync, 'weladee > %s ' % weladee_holiday)
            sync_logwarn(req.context_sync, 'can''t find this odoo-id %s in odoo holiday, will skip and not update' % weladee_holiday.odoo.odoo_id)
            data['res-mode'] = ''

    return data   

def _update_weladee_holiday_back(req, weladee_holiday, holiday_odoo):
    #update record to weladee
    weladee_holiday.odoo.odoo_id = holiday_odoo.id
    weladee_holiday.odoo.odoo_created_on = int(time.time())
    weladee_holiday.odoo.odoo_synced_on = int(time.time())

    try:
        __ = stub.UpdateHoliday(weladee_holiday, metadata=req.config.authorization)
        sync_logdebug(req.context_sync, 'Updated this holiday id %s in weladee' % holiday_odoo.id)
    except Exception as e:
        sync_logerror(req.context_sync, e)         
        sync_logerror(req.context_sync, 'Error while update this holiday id %s in weladee' % holiday_odoo.id) 

def sync_holiday(self, req):
    '''
    sync all holiday from weladee (1 way from weladee)

    '''
    req.context_sync['stat-hol'] = {'to-sync':0, "create":0, "update": 0, "error":0}

    #if empty, create one 
    if not req.employee_odoo_weladee_ids: 
        sync_logdebug(req.context_sync, 'getting all employee-weladee link') 
        req.employee_odoo_weladee_ids = get_emp_odoo_weladee_ids(req)

    odoo_hol = False
    weladee_holiday = False
    try:        
        sync_loginfo(req.context_sync,'[holiday] updating changes from weladee-> odoo')
        for weladee_holiday in stub.GetHolidays(weladee_pb2.Empty(), metadata=req.config.authorization):
            sync_stat_to_sync(req.context_sync['stat-hol'], 1)
            if not weladee_holiday :
               sync_logwarn(req.context_sync,'weladee holiday is empty')
               continue

            # collect leave type
            leaves_types = {}
            for t in self.env['hr.leave.type'].search([('weladee_code','!=',False)]):
                if not t.weladee_code in leaves_types:
                   leaves_types[t.weladee_code] = t.id 
            
            odoo_hol = sync_holiday_data(weladee_holiday, req, leaves_types)
            
            if odoo_hol and odoo_hol['res-mode'] == 'create':
                newid = False
                if odoo_hol['res-type']  == 'employee':
                     newid = req.leave_obj.sudo().with_context({'leave_skip_state_check': True,'leave_fast_create': True,'mail_create_nosubscribe':False,'mail_activity_automation_skip': True}).create(sync_clean_up( odoo_hol) )
                elif odoo_hol['res-type']  == 'company':
                     newid = req.company_holiday_obj.sudo().create(sync_clean_up(odoo_hol))
                if newid and newid.id:
                    sync_logdebug(req.context_sync, "Insert holiday '%s' to odoo" % odoo_hol )
                    sync_stat_create(req.context_sync['stat-hol'], 1)

                    _update_weladee_holiday_back(req, weladee_holiday, newid)
                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_holiday) 
                    sync_logerror(req.context_sync, "error while create odoo holiday id %s of '%s' in odoo" % (odoo_hol['res-id'], odoo_hol) ) 
                    sync_stat_error(req.context_sync['stat-hol'], 1)

            elif odoo_hol and odoo_hol['res-mode'] == 'update':
                odoo_id = False
                if odoo_hol['res-type']  == 'employee':
                     odoo_id = req.leave_obj.search([('id','=',odoo_hol['res-id'])])
                elif odoo_hol['res-type']  == 'company':
                     odoo_id = req.company_holiday_obj.search([('id','=',odoo_hol['res-id']),'|',('company_holiday_active','=',True),('company_holiday_active','=',False)])
                
                if odoo_id and odoo_id.id:
                    if odoo_id.sudo().with_context({'leave_skip_state_check': True}).write(sync_clean_up(odoo_hol)):
                        sync_logdebug(req.context_sync, "Updated holiday '%s' to odoo" % odoo_hol )
                        sync_stat_update(req.context_sync['stat-hol'], 1)

                        _update_weladee_holiday_back(req, weladee_holiday, odoo_id)                     
                    else:
                        sync_logdebug(req.context_sync, 'odoo > %s' % odoo_hol) 
                        sync_logerror(req.context_sync, "error found while update this odoo holiday id %s" % odoo_hol['res-id']) 
                        sync_stat_error(req.context_sync['stat-hol'], 1)

                else:
                   sync_logdebug(req.context_sync, 'weladee > %s' % weladee_holiday) 
                   sync_logerror(req.context_sync, "Not found this odoo holiday id %s of '%s' in odoo" % (odoo_hol['res-id'], odoo_hol) ) 
                   sync_stat_error(req.context_sync['stat-hol'], 1)

    except Exception as e:
        print(traceback.format_exc())
        sync_logdebug(req.context_sync, 'odoo >> %s' % odoo_hol) 

        # extra options
        if req.to_email and get_holiday_notify(self) and get_holiday_notify_email(self):
            if 'The number of remaining leaves is not sufficient for this leave type' in ("%s" % e):
                
                date = datetime.datetime.strptime(str(weladee_holiday.Holiday.date),'%Y%m%d')
                newid = req.leave_obj.search([('employee_id','=',req.employee_odoo_weladee_ids.get('%s' % weladee_holiday.Holiday.EmployeeID,False)),
                                ('date_from','=', _convert_to_tz_time(self, date.strftime('%Y-%m-%d') + ' 00:00:00').strftime('%Y-%m-%d %H:%M:%S'))])
                # 2018-11-20 KPO if not sufficient leave, update link back to weladee
                if newid:
                    _update_weladee_holiday_back(req, weladee_holiday, newid)

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


        if sync_weladee_error(weladee_holiday, 'holiday', e, req.context_sync):
            return
    #stat
    sync_stat_info(req.context_sync,'stat-hol','[holiday] updating changes from weladee-> odoo')