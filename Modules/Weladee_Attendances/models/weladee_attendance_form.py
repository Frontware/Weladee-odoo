# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import threading
import logging
_logger = logging.getLogger(__name__)
import datetime
import pytz

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.Weladee_Attendances.models.weladee_settings import get_synchronous_email 
from odoo.addons.Weladee_Attendances.library.weladee_translation import sync_form_title, sync_error1_title

class weladee_attendance_form(models.TransientModel):
    _name="weladee_attendance_form"
    _description="Weladee settings form"

    @api.model
    def _get_synchronous_email(self):
        return "get_synchronous_email(self)"

    @api.one
    def _get_synchronous_email(self):
        self.email = get_synchronous_email(self)

    #fields
    email = fields.Text(compute='_get_synchronous_email',default=_get_synchronous_email,string='Email')

    @api.model
    def open_sync_form(self):
        return {
            "name":sync_form_title(),
            "view_id": self.env.ref('Weladee_Attendances.weladee_attendance_wizard_frm').id,
            "res_model": "weladee_attendance_form",
            "res_id": self.create({}).id,
            "view_type": "form",
            "view_mode": "form",
            "type":"ir.actions.act_window",
            "target":"new"
        } 

    @api.multi
    def synchronousBtn(self):
        '''
        click confirm to start synchronous
        '''

        works = self.env['weladee_attendance.working'].search([])
        if works and len(works) > 0:           
           user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
           last_work = datetime.datetime.strptime(works.last_run,'%Y-%m-%d %H:%M:%S')
           last_run = last_work.astimezone(user_tz)

           raise UserError(sync_error1_title() % last_run.strftime('%d/%m/%Y %H:%M'))      

        cron = self.env.ref('Weladee_Attendances.weladee_attendance_synchronous_cron')
        #restart cron
        newnextcall = cron.nextcall - datetime.timedelta(days=30)
        cron.write({'nextcall': newnextcall})

        elapse_start = datetime.datetime.today()
        self.env['weladee_attendance.working'].create({'last_run':elapse_start})

        return {
            "name":sync_form_title(),
            "view_id": self.env.ref('Weladee_Attendances.weladee_attendance_wizard_frm_ok').id,
            "res_model": "weladee_attendance_form",
            "res_id": self.create({}).id,
            "view_type": "form",
            "view_mode": "form",
            "type":"ir.actions.act_window",
            "target":"new"
        }