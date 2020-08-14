# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
import time
import pytz
from datetime import datetime,date, timedelta

from odoo import osv
from odoo import models, fields, api, _

from .grpcproto import odoo_pb2
from .grpcproto import weladee_pb2
from . import weladee_settings
from .sync.weladee_base import myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_has_error

from odoo.addons.Weladee_Attendances.models.weladee_settings import get_synchronous_email, get_synchronous_debug,get_synchronous_period 
from odoo.addons.Weladee_Attendances.models.sync.weladee_position import sync_position_data, sync_position, resync_position 
from odoo.addons.Weladee_Attendances.models.sync.weladee_department import sync_department_data, sync_department
from odoo.addons.Weladee_Attendances.models.sync.weladee_employee import sync_employee_data, sync_employee
from odoo.addons.Weladee_Attendances.models.sync.weladee_manager import sync_manager_dep,sync_manager_emp
from odoo.addons.Weladee_Attendances.models.sync.weladee_log import sync_log
from odoo.addons.Weladee_Attendances.models.sync.weladee_holiday import sync_holiday
from odoo.addons.Weladee_Attendances.models.sync.weladee_expense import sync_expense

class weladee_attendance_working(models.TransientModel):
      _name="weladee_attendance.working"  
      _description="Weladee schedule last run"  

      last_run = fields.Datetime('Last run')

class weladee_attendance(models.TransientModel):
    _name="weladee_attendance.synchronous"
    _description="synchronous Employee, Department, Holiday and attendance"

    @api.model
    def start_sync(self):
        '''
            request-date : date user request to sync
            request-error : if error and stop ?
            request-logs-y : if any error ?
            request-logs : logs info
            request-logs-key: internal use for prevent write duplicate log
            request-email : email recipient
            request-debug : display debug log

            remarks:
            2018-11-14 KPO change hr.holidays to hr.leave
        '''
        elapse_start = datetime.today()
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        try: 
            today = elapse_start.astimezone(user_tz)
        except:
            today = user_tz.localize(elapse_start)
        context_sync = {
            'request-date':today.strftime('%d/%m/%Y %H:%M'),
            'request-logs':[],
            'request-logs-key':{},
            'request-error':False,
            'request-logs-y':False,
            'request-email':get_synchronous_email(self),
            'request-debug':get_synchronous_debug(self)
        }
        sync_loginfo(context_sync,"Starting sync..")
        authorization, holiday_status_id, api_db = weladee_settings.get_api_key(self)

        to_email = True
        if api_db and (api_db != self.env.cr.dbname):
           sync_stop(context_sync)
           sync_logerror(context_sync,'Warning this api key of (%s) is not match with current database' % api_db)
           to_email = False
        
        if (not holiday_status_id) or (not authorization) and (api_db == self.env.cr.dbname):
            #raise exceptions.UserError('Must to be set Leave Type on Weladee setting')
            sync_stop(context_sync)
            sync_logerror(context_sync,'You must setup API Key, Default Holiday Status at Attendances -> Weladee settings')
        
        job_obj = False
        if not sync_has_error(context_sync):
            sync_logdebug(context_sync,"Start sync...Positions")
            job_obj = self.env['hr.job']    
            sync_position(job_obj, authorization, context_sync) 
            if context_sync.get('connection-error',False) == True:
               # re create connection
               context_sync['connection-error-count'] = context_sync.get('connection-error-count',0) + 1
               context_sync['connection-error'] = False
               resync_position(job_obj, authorization, context_sync) 

        department_obj = False
        dep_managers = {}
        if not sync_has_error(context_sync):
            sync_logdebug(context_sync,"Start sync...Departments")
            department_obj = self.env['hr.department']    
            sync_department(department_obj, authorization, dep_managers, context_sync)
        
        country = {}
        if not sync_has_error(context_sync):
            sync_logdebug(context_sync,"Loading...Countries")            
            country_line_ids = self.env['res.country'].search([])
            for cu in country_line_ids:
                if cu.name : country[ cu.name.lower() ] = cu.id
        
        emp_managers = {}
        emp_obj = False
        if not sync_has_error(context_sync):
            sync_logdebug(context_sync,"Start sync...Employee")
               
            emp_obj = self.env['hr.employee']    
            pdf_path = self.env['ir.config_parameter'].search([('key','=','tmppath')]).value
            sync_employee(job_obj, emp_obj, department_obj, country, authorization, emp_managers, context_sync, pdf_path)

        if not sync_has_error(context_sync):
            sync_logdebug(context_sync,"Start sync...Manager")

            sync_manager_dep(emp_obj, department_obj, dep_managers, authorization, context_sync)
            sync_manager_emp(emp_obj, emp_managers, authorization, context_sync)
        
        odoo_weladee_ids = {}
        if not sync_has_error(context_sync):
            sync_logdebug(context_sync,"Start sync...Log")
            att_obj = self.env['hr.attendance']
            sync_log(self, emp_obj, att_obj, authorization, context_sync, odoo_weladee_ids, get_synchronous_period(self))

        if not sync_has_error(context_sync):
            sync_logdebug(context_sync,"Start sync...Holiday")
            hr_obj = self.env['hr.leave']
            com_hr_obj = self.env['weladee_attendance.company.holidays']
            sync_holiday(self, emp_obj, hr_obj, com_hr_obj, authorization, context_sync, odoo_weladee_ids, holiday_status_id, to_email)

        if not sync_has_error(context_sync):
            sync_logdebug(context_sync,"Start sync...Expense")
            ex_obj = self.env['hr.expense']
            sync_expense(self, emp_obj, ex_obj, authorization, context_sync, odoo_weladee_ids, {'period': 'all' ,'unit': 0})

        sync_loginfo(context_sync,'sending result to %s' % context_sync['request-email'])
        context_sync['request-elapse'] = str(datetime.today() - elapse_start)
        # send email status
        context_sync['request-status'] = 'Success'
        # check failed, first
        if context_sync['request-logs-y']=='Y':context_sync['request-status'] = 'Not OK'
        if context_sync['request-error']:context_sync['request-status'] = 'Failed'

        # removed temporary    
        del context_sync['request-logs-key']
        # send email if need
        # will not send if db not match
        if to_email: 
            self.send_result_mail(context_sync)
        else:
            _logger.warn("!!! email will not sent, because consider it as error from restored db.")

        works = self.env['weladee_attendance.working'].search([])
        if works: works.unlink()

    def send_result_mail(self, ctx):
        '''
        send result email to admin
        '''
        template = self.env.ref('Weladee_Attendances.weladee_attendance_synchronous_cron_mail', raise_if_not_found=False)
        
        if template:
           template.with_context(ctx).send_mail(self.id)        
        else:
           _logger.error('sending result to %s failed, no template found' % ctx['request-email'])            

        # send debug mail        
        if ctx.get('request-debug',False):
            template = self.env.ref('Weladee_Attendances.weladee_attendance_synchronous_cron_mail_debug', raise_if_not_found=False)
            
            if template:
                template.with_context(ctx).send_mail(self.id)        
            else:
                _logger.error('sending result to %s failed, no template found' % ctx['request-email'])            

