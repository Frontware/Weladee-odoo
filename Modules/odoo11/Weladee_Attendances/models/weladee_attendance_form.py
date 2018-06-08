# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import threading
import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, _
from odoo.addons.Weladee_Attendances.models.weladee_settings import get_synchronous_email 

class weladee_attendance_form(models.TransientModel):
    _name="weladee_attendance_form"

    @api.model
    def _get_synchronous_email(self):
        return get_synchronous_email(self)

    @api.one
    def _get_synchronous_email(self):
        self.email = get_synchronous_email(self)

    #fields
    email = fields.Text(compute='_get_synchronous_email',default=_get_synchronous_email)

    @api.multi
    def synchronousBtn(self):
        '''
        click confirm to start synchronous
        '''
        try:
            self.env.ref('Weladee_Attendances.weladee_attendance_synchronous_cron').method_direct_trigger()
        except:
            pass

        return {
            "name":"Weladee Synchronization",
            "view_id": self.env.ref('Weladee_Attendances.weladee_attendance_wizard_frm_ok').id,
            "res_model": "weladee_attendance_form",
            "view_type": "form",
            "view_mode": "form",
            "type":"ir.actions.act_window",
            "target":"new"
        }