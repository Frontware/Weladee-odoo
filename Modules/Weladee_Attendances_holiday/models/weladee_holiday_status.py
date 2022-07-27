# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv,api
from odoo import models, fields
from odoo import exceptions

class weladee_holiday_status(models.Model):
    _inherit = 'hr.leave.type'

    weladee_code = fields.Char('Weladee Code')
    is_weladee = fields.Boolean(compute='_compute_from_weladee', copy=False, readonly=True, store=True)

    _sql_constraints = [
      ('weladee_code_uniq', 'unique(weladee_code)', "Weladee Holiday Type can't duplicate !"),
    ]

    @api.depends('weladee_code')
    def _compute_from_weladee(self):
        for record in self:
            if record.weladee_code:
                record.weladee_code = True
            else:
                record.weladee_code = False
