# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

_logger = logging.getLogger(__name__)

import pytz
from datetime import datetime

from odoo import osv
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .sync.weladee_base import renew_connection, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_has_error

from odoo.addons.Weladee_Attendances.models.weladee_attendance_param import weladee_attendance_param
from odoo.addons.Weladee_Attendances.models.sync.weladee_position import sync_position, resync_position 
from odoo.addons.Weladee_Attendances.models.sync.weladee_department import sync_department
from odoo.addons.Weladee_Attendances.models.sync.weladee_employee import sync_employee
from odoo.addons.Weladee_Attendances.models.sync.weladee_manager import sync_manager_dep,sync_manager_emp
class weladee_attendance_working(models.TransientModel):
      _name="weladee_attendance.working"  
      _description="weladee_attendance.working"  

      last_run = fields.Datetime('Last run')

class weladee_attendance(models.TransientModel):
    _name="weladee_attendance.synchronous"
    _description="synchronous Employee, Department and position"

    @api.model
    def check_weladee_id(self, recs, vals):
        """
        Checks for the presence of a 'weladee_id' in the provided records or values.

        This method verifies if a 'weladee_id' exists either in the `vals` dictionary or within the `recs` records.
        If a 'weladee_id' is found and the context allows validation of the 'weladee_id', a UserError is raised to
        prevent changes to records imported from Weladee.

        Args:
            recs (recordset): The records to check for a 'weladee_id'.
            vals (dict): The values to check for a 'weladee_id'.

        Raises:
            UserError: If a 'weladee_id' is found and the context allows validation, indicating that changes are not allowed.
        """
        wid = False
        if 'weladee_id' in vals:
           wid = vals['weladee_id'] 
        else:
           for each in recs:
               if each.weladee_id: 
                  wid = each.weladee_id    
                  break

        if wid and self.env.context.get('validate_weladee_id',True):
           raise UserError(_('This record is imported from weladee, any change in odoo will be replaced by data from weladee.'))         


    def init_param(self):
        """
        Initializes and returns the Weladee attendance parameters.

        Returns:
            weladee_attendance_param: An instance of the Weladee attendance parameters.
        """
        return weladee_attendance_param()

    def disable_weladee_schedule(self, req):
        """
        Disables the Weladee attendance synchronization schedule.

        This method deactivates the scheduled cron job responsible for synchronizing
        Weladee attendance data. It also logs an error message indicating that the
        synchronization schedule has been disabled.

        Args:
            req: The request object containing the context for synchronization.
        """
        self.env.ref('Weladee_Attendances.weladee_attendance_synchronous_cron').write({'active':False})
        sync_logerror(req.context_sync, 'The Weladee attendance synchronization schedule has been disabled.')

    @api.model
    def start_sync(self):
        """
        Starts the synchronization process for attendance data.
        This method initializes the synchronization parameters, validates the configuration,
        and performs the synchronization for positions, departments, employees, and managers.
        It also handles logging, error checking, and sending email notifications about the
        synchronization status.
        Attributes:
            elapse_start (datetime): The start time of the synchronization process.
            user_tz (timezone): The user's timezone.
            req (object): The request object containing synchronization parameters and context.
        Context Sync Dictionary:
            features (list): List of features for the attendance form.
            request-date (str): The date and time when the sync was requested.
            request-logs (list): List of log messages.
            request-logs-key (dict): Dictionary to prevent duplicate log entries.
            request-error (bool): Indicates if there was an error during the sync.
            request-logs-y (bool): Indicates if there were any errors.
            request-email (str): Email recipient for the sync results.
            request-debug (bool): Indicates if debug logs should be displayed.
            connection-error (bool): Indicates if there was a connection error.
            connection-error-count (int): Count of connection errors.
            request-elapse (str): The elapsed time for the synchronization process.
            request-status (str): The status of the synchronization process.
        Methods:
            init_param(): Initializes the synchronization parameters.
            sync_loginfo(context, message): Logs informational messages.
            sync_logerror(context, message): Logs error messages.
            sync_stop(context): Stops the synchronization process.
            sync_logdebug(context, message): Logs debug messages.
            sync_has_error(context): Checks if there were any errors during the sync.
            sync_position(req): Synchronizes positions.
            resync_position(req): Re-synchronizes positions in case of connection errors.
            sync_department(req): Synchronizes departments.
            sync_employee(req): Synchronizes employees.
            sync_manager_dep(req): Synchronizes department managers.
            sync_manager_emp(req): Synchronizes employee managers.
            do_sync_options(req): Performs additional synchronization options.
            do_delete_options(req): Performs deletion options after synchronization.
            send_result_mail(context): Sends the synchronization result via email.
        Raises:
            Exception: If there is an error during the synchronization process.
        """
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

        if not req.config.api_db:
           sync_logerror(
               req.context_sync,
               'Warning: Current API key is not defined for the current database %s, please re-setup weladee settings' % self.env.cr.dbname
           )
           self.disable_weladee_schedule(req)
           sync_stop(req.context_sync)

        req.to_email = True
        if req.config.api_db and (req.config.api_db != self.env.cr.dbname):
           sync_logerror(req.context_sync, 'Warning: The API key for (%s) does not match the current database' % req.config.api_db)
           self.disable_weladee_schedule(req)
           sync_stop(req.context_sync)
           req.to_email = False
        
        if  (not req.config.authorization) and (req.config.api_db == self.env.cr.dbname):            
            sync_logerror(req.context_sync,'API Key must be configured in Attendances -> Weladee settings.')
            self.disable_weladee_schedule(req)
            sync_stop(req.context_sync)

        # validate lang
        # weladee required 2 langs
        for lg in self.env['res.lang'].search([('active','=',False),('code','in',['en_US','th_TH'])]):            
            lg.active = True
            sync_loginfo(req.context_sync, "Language '%s' has been activated." % lg.name)

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
        
        oldcompanyid = req.config.company_id

        if req.config.sync_employee and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...Employee")
               
            req.employee_obj = self.env['hr.employee']    
            sync_employee(req)

        # keep config
        if not sync_has_error(req.context_sync):
           if oldcompanyid != req.config.company_id:         
              self.env['weladee_attendance.synchronous.setting'].set_company(req.config.company_id) 

        if req.config.sync_employee and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...Manager")

            sync_manager_dep(req)
            sync_manager_emp(req)
            
        self.do_sync_options(req)

        self.do_delete_options(req)

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

    def do_delete_options(self, req):
        pass

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
