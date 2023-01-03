# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import threading
import logging
_logger = logging.getLogger(__name__)
import datetime
import pytz

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class weladee_attendance_form(models.TransientModel):
    _name="weladee_attendance_form"

    @api.model
    def _get_synchronous_email(self):
        return "get_synchronous_data(self)"

    def get_synchronous_data(self):
        self.email = self.env['weladee_attendance.synchronous.setting'].get_synchronous_email()
        self.fns = '''
        <li>Position</li>
        <li>Department</li>
        <li>Employee</li>
        '''

    #fields
    email = fields.Text(compute='get_synchronous_data',default=_get_synchronous_email)
    fns = fields.Text(compute='get_synchronous_data',default=_get_synchronous_email)

    @api.model
    def open_sync_form(self):
        return {
            "name":"Weladee Synchronization",
            "view_id": self.env.ref('Weladee_Attendances.weladee_attendance_wizard_frm').id,
            "res_model": "weladee_attendance_form",
            "res_id": self.create({}).id,
            "view_type": "form",
            "view_mode": "form",
            "type":"ir.actions.act_window",
            "target":"new"
        } 

    def synchronousBtn(self):
        '''
        click confirm to start synchronous
        '''

        works = self.env['weladee_attendance.working'].search([],limit=1,order='last_run desc')
        if works and len(works) > 0:           
           user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
           last_work = works.last_run
           last_run = last_work.astimezone(user_tz)

           # if last run is more than xx hours
           h = int(self.env['ir.config_parameter'].get_param('weladee-sync-wait') or '2')
           if h > ((datetime.datetime.utcnow() - works.last_run).seconds / 3600):
              later = (datetime.datetime.now() + datetime.timedelta(hours=h)).astimezone(user_tz).strftime('%d/%m/%Y %H:%M')
              raise UserError('Caution, the task already started at %s. Please wait until done or try again later lafter %s' % (last_run.strftime('%d/%m/%Y %H:%M'), later))      

        cron = self.env.ref('Weladee_Attendances.weladee_attendance_synchronous_cron')
        #restart cron
        newnextcall = cron.nextcall
        newnextcall = newnextcall - datetime.timedelta(days=30)
        cron.write({'nextcall': newnextcall})

        elapse_start = datetime.datetime.today()
        self.env['weladee_attendance.working'].create({'last_run':elapse_start})

        return {
            "name":"Weladee Synchronization",
            "view_id": self.env.ref('Weladee_Attendances.weladee_attendance_wizard_frm_ok').id,
            "res_model": "weladee_attendance_form",
            "res_id": self.create({}).id,
            "view_type": "form",
            "view_mode": "form",
            "type":"ir.actions.act_window",
            "target":"new"
        }