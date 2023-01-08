# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api, _

class weladee_attendance(models.Model):
    _inherit = 'hr.attendance'

    weladee_id = fields.Char(string="Weladee ID",copy=False)
    is_weladee = fields.Boolean(compute='_compute_from_weladee', copy=False, readonly=True, store=True)

    _sql_constraints = [
        ('unique_empin_timestamp', 'unique (employee_id, check_in)', 'employee checkin record'),
        ('unique_empout_timestamp', 'unique (employee_id, check_out)', 'employee checkout record'),
    ]

    @api.depends('weladee_id')
    def _compute_from_weladee(self):
        for record in self:
            if record.weladee_id:
                record.is_weladee = True
            else:
                record.is_weladee = False
