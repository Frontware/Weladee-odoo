# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, _

class weladee_attendance_form_ot(models.TransientModel):
    _inherit="weladee_attendance_form"

    def get_synchronous_data(self):
        super(weladee_attendance_form_ot, self).get_synchronous_data()

        if self.env['weladee_attendance.synchronous.setting'].get_sync_ot():
           self.fns += _('''
            <li>OT</li>
            ''')