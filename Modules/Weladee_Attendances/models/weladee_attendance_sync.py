# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

_logger = logging.getLogger(__name__)

import pytz
from datetime import datetime

from odoo import osv
from odoo import models, fields, api, _

from .sync.weladee_base import renew_connection, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_has_error

from odoo.addons.Weladee_Attendances.models.weladee_attendance_param import weladee_attendance_param
from odoo.addons.Weladee_Attendances.models.sync.weladee_position import sync_position, resync_position 
from odoo.addons.Weladee_Attendances.models.sync.weladee_department import sync_department
from odoo.addons.Weladee_Attendances.models.sync.weladee_employee import sync_employee
from odoo.addons.Weladee_Attendances.models.sync.weladee_manager import sync_manager_dep,sync_manager_emp
class weladee_attendance_working(models.TransientModel):
      _name="weladee_attendance.working"  

      last_run = fields.Datetime('Last run')

class weladee_attendance(models.TransientModel):
    _name="weladee_attendance.synchronous"
    _description="synchronous Employee, Department, Holiday and attendance"

    def init_param(self):
        return weladee_attendance_param()

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
        '''
        elapse_start = datetime.today()
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        try: 
            today = elapse_start.astimezone(user_tz)
        except:
            today = user_tz.localize(elapse_start)
        req = self.init_param()
        req.context_sync = {
            'features': self.env['weladee_attendance_form'].create({}).fns,
            'request-date':today.strftime('%d/%m/%Y %H:%M'),
            'request-logs':[],
            'request-logs-key':{},
            'request-error':False,
            'request-logs-y':False,
            'request-email':self.env['weladee_attendance.synchronous.setting'].get_synchronous_email(),
            'request-debug':self.env['weladee_attendance.synchronous.setting'].get_synchronous_debug()
        }
        sync_loginfo(req.context_sync,"Starting sync..")
        req.config = self.env['weladee_attendance.synchronous.setting'].get_settings()

        req.to_email = True
        if req.config.api_db and (req.config.api_db != self.env.cr.dbname):
           sync_stop(req.context_sync)
           sync_logerror(req.context_sync,'Warning this api key of (%s) is not match with current database' % req.config.api_db)
           req.to_email = False
        
        if  (not req.config.authorization) and (req.config.api_db == self.env.cr.dbname):            
            sync_stop(req.context_sync)
            sync_logerror(req.context_sync,'You must setup API Key, Default Holiday Status at Attendances -> Weladee settings')
        
        if req.config.sync_position and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...Positions")
            req.job_obj = self.env['hr.job']    
            sync_position(req) 
            if req.context_sync.get('connection-error',False) == True:
               # re create connection
               req.context_sync['connection-error-count'] = req.context_sync.get('connection-error-count',0) + 1
               req.context_sync['connection-error'] = False
               resync_position(req) 

        if req.config.sync_department and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...Departments")
            req.department_obj = self.env['hr.department']    
            sync_department(req)
        
        if not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Loading...Countries")            
            country_line_ids = self.env['res.country'].search([])
            for cu in country_line_ids:
                if cu.name : req.country[ cu.name ] = cu.id
        
        if req.config.sync_employee and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...Employee")
               
            req.employee_obj = self.env['hr.employee']    
            sync_employee(req)

        if req.config.sync_employee and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...Manager")

            sync_manager_dep(req)
            sync_manager_emp(req)
            
        self.do_sync_options(req)

        sync_loginfo(req.context_sync,'\n\nsending result to %s\n' % req.context_sync['request-email'])
        req.context_sync['request-elapse'] = str(datetime.today() - elapse_start)
        # send email status
        req.context_sync['request-status'] = 'Success'
        # check failed, first
        if req.context_sync['request-logs-y']=='Y':req.context_sync['request-status'] = 'Not OK'
        if req.context_sync['request-error']:req.context_sync['request-status'] = 'Failed'

        # removed temporary    
        del req.context_sync['request-logs-key']
        # send email if need
        # will not send if db not match
        if req.to_email: 
            self.send_result_mail(req.context_sync)
        else:
            _logger.warning("!!! email will not sent, because consider it as error from restored db.")

        works = self.env['weladee_attendance.working'].search([])
        if works: works.unlink()

    def do_sync_options(self, req):
        return

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
